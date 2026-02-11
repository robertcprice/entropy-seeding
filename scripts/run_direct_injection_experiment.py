#!/usr/bin/env python3
"""
Direct entropy injection experiment — bypasses the seed bottleneck.

Instead of: entropy → seed → ollama (seed becomes just a number)
This does:  entropy → logit perturbation → token selection

Three injection modes:
  1. BASELINE: Standard sampling (torch.manual_seed only)
  2. LOGIT_PERTURB: Add entropy-derived noise to logits before sampling
  3. TEMP_MODULATE: Use entropy to vary temperature per-token

This tests whether entropy source quality matters when it actually
touches the generation process, not just the RNG seed.

Requires: pip install transformers torch

Usage:
    python run_direct_injection_experiment.py --model distilgpt2 --samples 10
    python run_direct_injection_experiment.py --model gpt2 --samples 10
    python run_direct_injection_experiment.py --model gpt2-medium --samples 10
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import argparse
import hashlib
import json
import os
import random
import re
import secrets
import time
from collections import Counter
from datetime import datetime
from math import log2
from pathlib import Path

import numpy as np
import torch

OUTPUT_DIR = Path(__file__).parent.parent / "results" / "direct_injection"

# ─────────────────────────────────────────────────────────────────────
# Prompts (subset matching v2 experiment — diverse domains)
# ─────────────────────────────────────────────────────────────────────

PROMPTS = [
    {"text": "The old lighthouse keeper had never seen anything like it.", "domain": "creative"},
    {"text": "What is the meaning of consciousness?", "domain": "philosophical"},
    {"text": "Explain the concept of entropy to a five-year-old.", "domain": "technical"},
    {"text": "Write a Python function that checks if a string is a palindrome.", "domain": "code"},
    {"text": "What are the three laws of thermodynamics and why do they matter?", "domain": "factual"},
    {"text": "Summarize the key ideas of evolutionary biology in three paragraphs.", "domain": "summarization"},
    {"text": "Create a comparison table of three programming paradigms.", "domain": "structured"},
    {"text": "If all roses are flowers, and some flowers fade quickly, can we conclude that some roses fade quickly?", "domain": "reasoning"},
    {"text": "The robot looked at its hands and wondered what it meant to be alive.", "domain": "creative"},
    {"text": "Describe what infinity feels like.", "domain": "philosophical"},
    {"text": "How does a neural network learn?", "domain": "technical"},
    {"text": "Write a function that finds the longest common subsequence of two strings.", "domain": "code"},
    {"text": "Describe the process of photosynthesis step by step.", "domain": "factual"},
    {"text": "Provide a concise overview of how the internet works.", "domain": "summarization"},
    {"text": "Invent a name for a magical creature that lives in clouds.", "domain": "naming"},
]


# ─────────────────────────────────────────────────────────────────────
# Entropy sources (same as v2 experiment)
# ─────────────────────────────────────────────────────────────────────

class PRNGSource:
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.name = "PRNG"
    def get_bytes(self, n: int) -> bytes:
        return bytes(self.rng.getrandbits(8) for _ in range(n))
    def get_float(self) -> float:
        return self.rng.random()

class TRNGSource:
    def __init__(self):
        self.name = "TRNG"
    def get_bytes(self, n: int) -> bytes:
        return secrets.token_bytes(n)
    def get_float(self) -> float:
        return int.from_bytes(secrets.token_bytes(4), 'big') / (2**32)

class HMIXSource:
    def __init__(self):
        self.name = "HMIX"
        self._counter = 0
    def get_bytes(self, n: int) -> bytes:
        self._counter += 1
        data = f"{time.time_ns()}-{secrets.token_hex(16)}-{self._counter}"
        h = hashlib.sha256(data.encode()).digest()
        result = h[:n] if n <= 32 else h * (n // 32 + 1)
        return result[:n]
    def get_float(self) -> float:
        return int.from_bytes(self.get_bytes(4), 'big') / (2**32)


# ─────────────────────────────────────────────────────────────────────
# Injection modes
# ─────────────────────────────────────────────────────────────────────

def inject_baseline(logits: torch.Tensor, source, step: int) -> torch.Tensor:
    """No injection — standard sampling."""
    return logits


def inject_logit_perturbation(logits: torch.Tensor, source, step: int,
                               scale: float = 0.1) -> torch.Tensor:
    """Add entropy-derived noise to logits before sampling.

    This is the key experiment: the noise comes from the entropy source,
    so if source quality matters, it will show up here.
    """
    vocab_size = logits.shape[-1]
    # Get entropy bytes and interpret as uint32, then map to [0, 1)
    n_bytes = vocab_size * 4
    raw = source.get_bytes(n_bytes)
    uint_vals = np.frombuffer(raw[:vocab_size * 4], dtype=np.uint32).copy()
    uniform = uint_vals.astype(np.float64) / (2**32)  # [0, 1)
    # Map to standard normal via inverse CDF approximation (Box-Muller-like)
    noise = (uniform - 0.5) * 2  # [-1, 1)
    # Normalize to zero-mean, unit-variance
    std = noise.std()
    if std > 1e-8:
        noise = (noise - noise.mean()) / std
    noise_tensor = torch.from_numpy(noise.astype(np.float32)).to(logits.device) * scale
    return logits + noise_tensor


def inject_temperature_modulation(logits: torch.Tensor, source, step: int,
                                    base_temp: float = 0.7,
                                    modulation: float = 0.3) -> torch.Tensor:
    """Use entropy to vary temperature per token.

    Temperature = base_temp + modulation * (entropy_float - 0.5)
    Range: [base_temp - modulation/2, base_temp + modulation/2]
    """
    entropy_val = source.get_float()
    temp = base_temp + modulation * (entropy_val - 0.5)
    temp = max(0.1, min(2.0, temp))  # clamp
    return logits / temp


INJECTION_MODES = {
    "baseline": inject_baseline,
    "logit_perturb": inject_logit_perturbation,
    "temp_modulate": inject_temperature_modulation,
}


# ─────────────────────────────────────────────────────────────────────
# Metrics (same as v2)
# ─────────────────────────────────────────────────────────────────────

def compute_mtld(words, threshold=0.72):
    if len(words) < 10:
        return float('nan')
    def _pass(wl):
        factors = 0; fl = 0; ts = set()
        for w in wl:
            fl += 1; ts.add(w)
            if len(ts) / fl <= threshold:
                factors += 1; fl = 0; ts = set()
        if fl > 0:
            cur = len(ts) / fl
            factors += (1.0 - cur) / (1.0 - threshold) if threshold < 1.0 else 0
        return len(wl) / factors if factors > 0 else float(len(wl))
    return (_pass(words) + _pass(list(reversed(words)))) / 2.0

def calculate_metrics(text):
    if not text or not text.strip():
        return {}
    words = text.lower().split()
    total = len(words)
    if total == 0:
        return {}
    unique = len(set(words))
    bigrams = [(words[i], words[i+1]) for i in range(total - 1)]
    char_counts = Counter(text)
    tc = len(text)
    shannon_char = -sum((c/tc) * log2(c/tc) for c in char_counts.values() if c > 0)
    word_counts = Counter(words)
    num_types = len(word_counts)
    shannon_word = -sum((c/total) * log2(c/total) for c in word_counts.values() if c > 0)
    shannon_word += (num_types - 1) / (2 * total)  # Miller-Madow
    return {
        "length_words": total,
        "shannon_char": round(shannon_char, 6),
        "shannon_word": round(shannon_word, 6),
        "word_diversity": round(unique / total, 6),
        "mtld": round(compute_mtld(words), 4),
        "distinct_2": round(len(set(bigrams)) / len(bigrams), 6) if bigrams else 0,
    }


# ─────────────────────────────────────────────────────────────────────
# Generation with direct injection
# ─────────────────────────────────────────────────────────────────────

def generate_with_injection(model, tokenizer, prompt: str, source,
                             injection_fn, max_new_tokens: int = 150,
                             base_seed: int = 42) -> str:
    """Generate text with entropy injection at the logit level."""
    # Seed torch for reproducibility of the base sampling
    torch.manual_seed(base_seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(base_seed)

    device = next(model.parameters()).device
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)

    generated = input_ids.clone()

    with torch.no_grad():
        for step in range(max_new_tokens):
            outputs = model(generated)
            next_logits = outputs.logits[:, -1, :].float()  # float32 for stability

            # Apply entropy injection
            next_logits = injection_fn(next_logits[0], source, step).unsqueeze(0)

            # Top-k + top-p sampling
            top_k = 50
            top_p = 0.9

            # Top-k filtering
            if top_k > 0:
                indices_to_remove = next_logits < torch.topk(next_logits, top_k)[0][..., -1, None]
                next_logits[indices_to_remove] = -float('inf')

            # Top-p (nucleus) filtering
            sorted_logits, sorted_indices = torch.sort(next_logits, descending=True)
            cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
            sorted_indices_to_remove = cumulative_probs > top_p
            sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
            sorted_indices_to_remove[..., 0] = 0
            indices_to_remove = sorted_indices_to_remove.scatter(
                1, sorted_indices, sorted_indices_to_remove)
            next_logits[indices_to_remove] = -float('inf')

            # Sample
            probs = torch.softmax(next_logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)

            generated = torch.cat([generated, next_token], dim=-1)

            # Stop at EOS
            if next_token.item() == tokenizer.eos_token_id:
                break

    output_ids = generated[0][input_ids.shape[-1]:]
    return tokenizer.decode(output_ids, skip_special_tokens=True)


# ─────────────────────────────────────────────────────────────────────
# Experiment runner
# ─────────────────────────────────────────────────────────────────────

def run_experiment(model_name: str, num_samples: int, max_tokens: int):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"\n{'='*70}")
    print(f" DIRECT INJECTION EXPERIMENT: {model_name}")
    print(f" Samples per condition: {num_samples}")
    print(f" Max tokens: {max_tokens}")
    print(f" Injection modes: {list(INJECTION_MODES.keys())}")
    print(f"{'='*70}")

    # Load model
    print(f"\nLoading {model_name}...")
    device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, dtype=torch.float32
    ).to(device)
    model.eval()

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"  Device: {device}")
    print(f"  Parameters: {sum(p.numel() for p in model.parameters()) / 1e6:.1f}M")

    # Randomization
    order_rng = random.Random(12345)

    results = {
        "model": model_name,
        "device": device,
        "parameters_m": round(sum(p.numel() for p in model.parameters()) / 1e6, 1),
        "experiment_type": "direct_entropy_injection",
        "timestamp": datetime.now().isoformat(),
        "num_samples": num_samples,
        "max_tokens": max_tokens,
        "injection_modes": list(INJECTION_MODES.keys()),
        "sources": ["PRNG", "TRNG", "HMIX"],
        "prompts": [],
    }

    source_classes = {"PRNG": PRNGSource, "TRNG": TRNGSource, "HMIX": HMIXSource}
    source_names = list(source_classes.keys())
    mode_names = list(INJECTION_MODES.keys())

    for prompt_idx, prompt_info in enumerate(PROMPTS):
        prompt_text = prompt_info["text"]
        domain = prompt_info["domain"]
        print(f"\n  [{prompt_idx+1}/{len(PROMPTS)}] [{domain}] {prompt_text[:50]}...")

        prompt_result = {
            "prompt": prompt_text,
            "domain": domain,
            "conditions": {},
        }

        # Shuffle order of conditions
        conditions = [(mode, src) for mode in mode_names for src in source_names]
        order_rng.shuffle(conditions)

        for mode_name, source_name in conditions:
            key = f"{mode_name}__{source_name}"
            injection_fn = INJECTION_MODES[mode_name]
            samples = []

            for i in range(num_samples):
                # Fresh source each sample
                source = source_classes[source_name]() if source_name != "PRNG" else PRNGSource(seed=42 + i)

                try:
                    t0 = time.time()
                    output = generate_with_injection(
                        model, tokenizer, prompt_text, source,
                        injection_fn, max_new_tokens=max_tokens,
                        base_seed=42 + i,
                    )
                    elapsed = time.time() - t0

                    metrics = calculate_metrics(output)
                    samples.append({
                        "output": output[:500],  # truncate for storage
                        "metrics": metrics,
                        "generation_time": round(elapsed, 3),
                    })
                    print(f"      {key}[{i+1}]: {metrics.get('length_words', 0)} words, "
                          f"{elapsed:.1f}s")
                except Exception as e:
                    samples.append({"error": str(e)[:200]})
                    print(f"      {key}[{i+1}]: ERROR {str(e)[:80]}")

            valid = [s for s in samples if "metrics" in s and s["metrics"]]
            if valid:
                agg = {}
                for mkey in valid[0]["metrics"]:
                    vals = [s["metrics"][mkey] for s in valid if s["metrics"].get(mkey) is not None]
                    if vals:
                        agg[f"{mkey}_mean"] = round(sum(vals) / len(vals), 6)
                prompt_result["conditions"][key] = {
                    "samples": samples,
                    "aggregate": agg,
                    "n_valid": len(valid),
                }
            else:
                prompt_result["conditions"][key] = {"samples": samples, "aggregate": None, "n_valid": 0}

        results["prompts"].append(prompt_result)

    return results


def analyze_results(results: dict) -> dict:
    """Quick inline analysis of injection experiment results."""
    from scipy import stats as sp_stats

    modes = results["injection_modes"]
    sources = results["sources"]
    metrics_to_check = ["word_diversity", "mtld", "distinct_2", "shannon_word"]

    analysis = {"comparisons": []}

    # For each injection mode, compare sources
    for mode in modes:
        for metric in metrics_to_check:
            source_vals = {src: [] for src in sources}
            for prompt_data in results["prompts"]:
                for src in sources:
                    key = f"{mode}__{src}"
                    cond = prompt_data["conditions"].get(key, {})
                    if cond.get("aggregate"):
                        v = cond["aggregate"].get(f"{metric}_mean")
                        if v is not None:
                            source_vals[src].append(v)

            # Pairwise tests
            for i in range(len(sources)):
                for j in range(i + 1, len(sources)):
                    s1, s2 = sources[i], sources[j]
                    a = np.array(source_vals[s1])
                    b = np.array(source_vals[s2])
                    n = min(len(a), len(b))
                    if n < 3:
                        continue
                    a, b = a[:n], b[:n]
                    diff = a - b
                    d = float(np.mean(diff) / np.std(diff, ddof=1)) if np.std(diff, ddof=1) > 0 else 0
                    try:
                        _, p = sp_stats.wilcoxon(a, b)
                    except Exception:
                        p = 1.0
                    analysis["comparisons"].append({
                        "mode": mode,
                        "metric": metric,
                        "comparison": f"{s1}_vs_{s2}",
                        "n": n,
                        "mean_diff": round(float(np.mean(diff)), 6),
                        "cohens_d": round(d, 4),
                        "p_value": round(float(p), 6),
                    })

    # Also compare across injection modes (same source)
    for src in sources:
        for metric in metrics_to_check:
            mode_vals = {mode: [] for mode in modes}
            for prompt_data in results["prompts"]:
                for mode in modes:
                    key = f"{mode}__{src}"
                    cond = prompt_data["conditions"].get(key, {})
                    if cond.get("aggregate"):
                        v = cond["aggregate"].get(f"{metric}_mean")
                        if v is not None:
                            mode_vals[mode].append(v)

            # Compare each injection mode to baseline
            baseline = np.array(mode_vals.get("baseline", []))
            for mode in modes:
                if mode == "baseline":
                    continue
                other = np.array(mode_vals.get(mode, []))
                n = min(len(baseline), len(other))
                if n < 3:
                    continue
                bl, ot = baseline[:n], other[:n]
                diff = ot - bl
                d = float(np.mean(diff) / np.std(diff, ddof=1)) if np.std(diff, ddof=1) > 0 else 0
                try:
                    _, p = sp_stats.wilcoxon(bl, ot)
                except Exception:
                    p = 1.0
                analysis["comparisons"].append({
                    "mode": f"{mode}_vs_baseline",
                    "source": src,
                    "metric": metric,
                    "n": n,
                    "mean_diff": round(float(np.mean(diff)), 6),
                    "cohens_d": round(d, 4),
                    "p_value": round(float(p), 6),
                })

    # BH-FDR correction on all p-values
    all_p = [c["p_value"] for c in analysis["comparisons"]]
    n_tests = len(all_p)
    if n_tests > 0:
        indexed = sorted(enumerate(all_p), key=lambda x: x[1])
        running_min = 1.0
        adj_p = [0.0] * n_tests
        for rank_from_end, (orig_idx, p) in enumerate(reversed(indexed)):
            rank = n_tests - rank_from_end  # 1-indexed from top
            raw_adj = p * n_tests / rank
            running_min = min(running_min, min(raw_adj, 1.0))
            adj_p[orig_idx] = running_min
        for i, comp in enumerate(analysis["comparisons"]):
            comp["p_value_bh"] = round(adj_p[i], 6)
            comp["significant_bh"] = adj_p[i] < 0.05

    analysis["summary"] = {
        "total_tests": n_tests,
        "significant_uncorrected": sum(1 for c in analysis["comparisons"] if c["p_value"] < 0.05),
        "significant_bh": sum(1 for c in analysis["comparisons"] if c.get("significant_bh", False)),
    }

    return analysis


def main():
    parser = argparse.ArgumentParser(description="Direct entropy injection experiment")
    parser.add_argument("--model", type=str, default="distilgpt2",
                        help="HuggingFace model (distilgpt2, gpt2, gpt2-medium, gpt2-large)")
    parser.add_argument("--samples", type=int, default=10,
                        help="Samples per condition per prompt")
    parser.add_argument("--max-tokens", type=int, default=150,
                        help="Max tokens to generate")

    args = parser.parse_args()

    results = run_experiment(args.model, args.samples, args.max_tokens)

    # Inline analysis
    print(f"\n{'='*70}")
    print(" ANALYSIS")
    print(f"{'='*70}")

    analysis = analyze_results(results)
    results["analysis"] = analysis

    print(f"\n  Total tests: {analysis['summary']['total_tests']}")
    print(f"  Significant (uncorrected): {analysis['summary']['significant_uncorrected']}")
    print(f"  Significant (BH-corrected): {analysis['summary']['significant_bh']}")

    # Print significant results
    sig = [c for c in analysis["comparisons"] if c.get("significant_bh")]
    if sig:
        print(f"\n  BH-significant results:")
        for c in sig:
            print(f"    {c.get('mode', '')} | {c.get('metric', '')} | "
                  f"{c.get('comparison', c.get('source', ''))} | "
                  f"d={c['cohens_d']:.3f} | p_bh={c['p_value_bh']:.4f}")
    else:
        print(f"\n  No results survive BH correction.")

    # Print top effects by |d|
    top = sorted(analysis["comparisons"], key=lambda c: abs(c["cohens_d"]), reverse=True)[:10]
    print(f"\n  Top 10 effects by |d|:")
    for c in top:
        print(f"    {c.get('mode', '')} | {c.get('metric', '')} | "
              f"{c.get('comparison', c.get('source', ''))} | "
              f"d={c['cohens_d']:+.3f} | p={c['p_value']:.4f} | p_bh={c.get('p_value_bh', 'N/A')}")

    # Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    model_safe = args.model.replace("/", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = OUTPUT_DIR / f"injection_{model_safe}_{timestamp}.json"

    with open(filepath, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved: {filepath}")


if __name__ == "__main__":
    main()
