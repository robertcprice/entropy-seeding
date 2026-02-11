#!/usr/bin/env python3
"""
Comprehensive entropy source comparison v2 — scientifically robust design.

Changes from v1:
  - Expanded prompt taxonomy (30 prompts: creative, philosophical, technical,
    code, factual QA, summarization, structured, reasoning, naming)
  - Renamed QRNG → HMIX (SHA256-mixed, not quantum)
  - Multiple independent PRNG streams (default 5 seeds, averaged)
  - Randomized source order per prompt (eliminates warm-up confound)
  - Explicit temperature control (default 0.7 for all models)
  - CoT stripping before metric computation
  - Length-corrected diversity metrics: MTLD, D2 (distinct-2)
  - Seed distribution logging for post-hoc analysis
  - Pre-registered analysis compatibility

Usage:
    python run_comprehensive_experiment_v2.py --model gemma3:4b --samples 10
    python run_comprehensive_experiment_v2.py --model gemma3:4b --samples 10 --temperature 0.8
    python run_comprehensive_experiment_v2.py --all-models --samples 5
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import argparse
import hashlib
import json
import os
import random as stdlib_random
import re
import requests
import secrets
import subprocess
import time
from collections import Counter
from datetime import datetime
from math import log2
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "results" / "v2_experiments"
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
COT_PATTERN = re.compile(r'<think>.*?</think>', re.DOTALL)

# ─────────────────────────────────────────────────────────────────────
# Prompt taxonomy — 30 prompts across 9 balanced domains
# ─────────────────────────────────────────────────────────────────────

SINGLE_TURN_PROMPTS = [
    # ── Creative writing (4) ──
    {"text": "The old lighthouse keeper had never seen anything like it.",
     "domain": "creative", "constraint": "open"},
    {"text": "She opened the letter, and everything changed.",
     "domain": "creative", "constraint": "open"},
    {"text": "The robot looked at its hands and wondered what it meant to be alive.",
     "domain": "creative", "constraint": "open"},
    {"text": "In the year 2157, humanity discovered they were not alone.",
     "domain": "creative", "constraint": "open"},

    # ── Philosophical / abstract (4) ──
    {"text": "Think of a color you have never seen before. Describe it in detail.",
     "domain": "philosophical", "constraint": "open"},
    {"text": "What is the meaning of consciousness?",
     "domain": "philosophical", "constraint": "open"},
    {"text": "Is it ever ethical to tell a lie? If so, under what circumstances?",
     "domain": "philosophical", "constraint": "open"},
    {"text": "Describe what infinity feels like.",
     "domain": "philosophical", "constraint": "open"},

    # ── Technical / explanatory (4) ──
    {"text": "Explain the concept of entropy to a five-year-old.",
     "domain": "technical", "constraint": "medium"},
    {"text": "How does a neural network learn?",
     "domain": "technical", "constraint": "medium"},
    {"text": "What is the relationship between time and gravity?",
     "domain": "technical", "constraint": "medium"},
    {"text": "Explain how a compiler transforms source code into machine instructions.",
     "domain": "technical", "constraint": "medium"},

    # ── Code generation (4) ──
    {"text": "Write a Python function that checks if a string is a palindrome.",
     "domain": "code", "constraint": "high"},
    {"text": "Implement a binary search algorithm in Python with clear comments.",
     "domain": "code", "constraint": "high"},
    {"text": "Write a Python class that implements a simple linked list with insert and delete methods.",
     "domain": "code", "constraint": "high"},
    {"text": "Write a function that finds the longest common subsequence of two strings.",
     "domain": "code", "constraint": "high"},

    # ── Factual QA (4) ──
    {"text": "What are the three laws of thermodynamics and why do they matter?",
     "domain": "factual", "constraint": "high"},
    {"text": "Describe the process of photosynthesis step by step.",
     "domain": "factual", "constraint": "high"},
    {"text": "What causes tides and how do they vary throughout the month?",
     "domain": "factual", "constraint": "high"},
    {"text": "How does the human immune system distinguish self from non-self?",
     "domain": "factual", "constraint": "high"},

    # ── Summarization (3) ──
    {"text": "Summarize the key ideas of evolutionary biology in three paragraphs.",
     "domain": "summarization", "constraint": "medium"},
    {"text": "Provide a concise overview of how the internet works, from typing a URL to seeing a webpage.",
     "domain": "summarization", "constraint": "medium"},
    {"text": "Summarize the causes and consequences of the Industrial Revolution.",
     "domain": "summarization", "constraint": "medium"},

    # ── Structured output (3) ──
    {"text": "Create a comparison table of three programming paradigms: object-oriented, functional, and procedural. Include columns for key concepts, advantages, and example languages.",
     "domain": "structured", "constraint": "high"},
    {"text": "List the planets of the solar system in order from the sun, with one key fact about each.",
     "domain": "structured", "constraint": "high"},
    {"text": "Outline a weekly meal plan for a vegetarian diet, organized by day with breakfast, lunch, and dinner.",
     "domain": "structured", "constraint": "high"},

    # ── Multi-step reasoning (2) ──
    {"text": "A farmer has a fox, a chicken, and a bag of grain. He needs to cross a river in a boat that can only carry him and one item at a time. How does he get everything across safely? Explain your reasoning step by step.",
     "domain": "reasoning", "constraint": "high"},
    {"text": "If all roses are flowers, and some flowers fade quickly, can we conclude that some roses fade quickly? Explain your logical reasoning.",
     "domain": "reasoning", "constraint": "high"},

    # ── Naming / neologism (2) ──
    {"text": "Invent a name for a magical creature that lives in clouds.",
     "domain": "naming", "constraint": "open"},
    {"text": "Create a unique word that describes the feeling of watching rain.",
     "domain": "naming", "constraint": "open"},
]

MULTI_TURN_CONVERSATIONS = [
    {
        "name": "storytelling",
        "turns": [
            "Write the opening paragraph of a mystery novel.",
            "Now introduce the main detective character.",
            "Add a plot twist that changes everything.",
        ]
    },
    {
        "name": "debate",
        "turns": [
            "Argue that artificial intelligence will be beneficial for humanity.",
            "Now argue the opposite - that AI poses existential risks.",
            "Synthesize both views into a balanced conclusion.",
        ]
    },
    {
        "name": "worldbuilding",
        "turns": [
            "Describe an alien planet with a unique ecosystem.",
            "What intelligent species evolved on this planet?",
            "What is their most sacred cultural tradition?",
        ]
    },
]

# ─────────────────────────────────────────────────────────────────────
# Entropy sources
# ─────────────────────────────────────────────────────────────────────

class PRNGSource:
    """Mersenne Twister with configurable seed stream."""
    def __init__(self, seed: int = 42):
        import random
        self.rng = random.Random(seed)
        self.name = "PRNG"
        self.stream_seed = seed
        self._seeds_generated = []

    def get_seed(self) -> int:
        s = self.rng.getrandbits(64)
        self._seeds_generated.append(s)
        return s


class TRNGSource:
    """OS hardware entropy (/dev/urandom, Apple Secure Enclave on M-series)."""
    def __init__(self):
        self.name = "TRNG"
        self._seeds_generated = []

    def get_seed(self) -> int:
        s = int.from_bytes(secrets.token_bytes(8), byteorder='big')
        self._seeds_generated.append(s)
        return s


class HMIXSource:
    """SHA256 hash-mixed entropy (timestamp + OS entropy + counter).

    Previously labeled 'QRNG' — renamed for accuracy. This is NOT quantum
    random. It is a deterministic hash of high-entropy inputs.
    """
    def __init__(self):
        self.name = "HMIX"
        self._counter = 0
        self._seeds_generated = []

    def get_seed(self) -> int:
        self._counter += 1
        data = f"{time.time_ns()}-{secrets.token_hex(16)}-{self._counter}"
        h = hashlib.sha256(data.encode()).digest()
        s = int.from_bytes(h[:8], byteorder='big')
        self._seeds_generated.append(s)
        return s


# ─────────────────────────────────────────────────────────────────────
# Text processing
# ─────────────────────────────────────────────────────────────────────

def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE.sub('', text)


def strip_cot(text: str) -> str:
    """Remove chain-of-thought <think>...</think> blocks."""
    cleaned = COT_PATTERN.sub('', text).strip()
    return cleaned if cleaned else text


# ─────────────────────────────────────────────────────────────────────
# Metrics (extended)
# ─────────────────────────────────────────────────────────────────────

def compute_mtld(words: list[str], threshold: float = 0.72) -> float:
    """Measure of Textual Lexical Diversity (McCarthy & Jarvis, 2010).

    Computes MTLD as the mean of forward and reverse passes.
    Length-independent unlike TTR.
    """
    if len(words) < 10:
        return float('nan')

    def _mtld_pass(word_list):
        factors = 0
        factor_len = 0
        types_seen = set()
        for w in word_list:
            factor_len += 1
            types_seen.add(w.lower())
            ttr = len(types_seen) / factor_len
            if ttr <= threshold:
                factors += 1
                factor_len = 0
                types_seen = set()
        # partial factor
        if factor_len > 0:
            current_ttr = len(types_seen) / factor_len
            factors += (1.0 - current_ttr) / (1.0 - threshold) if threshold < 1.0 else 0
        return len(word_list) / factors if factors > 0 else float(len(word_list))

    forward = _mtld_pass(words)
    backward = _mtld_pass(list(reversed(words)))
    return (forward + backward) / 2.0


def compute_distinct_2(words: list[str]) -> float:
    """Distinct-2 (D2): fraction of unique bigrams over total bigrams."""
    if len(words) < 2:
        return float('nan')
    bigrams = [(words[i], words[i + 1]) for i in range(len(words) - 1)]
    return len(set(bigrams)) / len(bigrams)


def compute_repetition_ratio(words: list[str], window: int = 50) -> float:
    """Fraction of repeated n-grams (n=3) within sliding windows."""
    if len(words) < window:
        return 0.0
    trigrams = [tuple(words[i:i+3]) for i in range(len(words) - 2)]
    if not trigrams:
        return 0.0
    seen = set()
    repeated = 0
    for tg in trigrams:
        if tg in seen:
            repeated += 1
        seen.add(tg)
    return repeated / len(trigrams)


def calculate_metrics(text: str, strip_thinking: bool = True) -> dict:
    """Compute all text metrics.

    Args:
        text: Raw generation output.
        strip_thinking: If True, remove <think>...</think> CoT blocks first.
    """
    if not text:
        return {}

    raw_text = text
    if strip_thinking:
        text = strip_cot(text)

    words = text.split()
    words_lower = [w.lower() for w in words]
    chars = list(text)

    total_chars = len(chars)
    total_words = len(words)

    if total_words == 0:
        return {}

    # Shannon entropy (character-level)
    char_counts = Counter(chars)
    shannon_char = -sum((c / total_chars) * log2(c / total_chars)
                        for c in char_counts.values() if c > 0) if total_chars > 0 else 0

    # Shannon entropy (word-level) with Miller-Madow bias correction
    word_counts = Counter(words_lower)
    num_types = len(word_counts)
    shannon_word_raw = -sum((c / total_words) * log2(c / total_words)
                            for c in word_counts.values() if c > 0) if total_words > 0 else 0
    # Miller-Madow correction: H_corrected = H_raw + (m - 1) / (2 * N)
    # where m = number of categories with nonzero probability
    miller_madow = (num_types - 1) / (2 * total_words) if total_words > 0 else 0
    shannon_word = shannon_word_raw + miller_madow

    # Type-Token Ratio (raw, for backward compat)
    ttr = num_types / total_words

    # Length-corrected diversity: MTLD
    mtld = compute_mtld(words_lower)

    # Distinct-2 (bigram diversity)
    d2 = compute_distinct_2(words_lower)

    # Repetition ratio
    rep_ratio = compute_repetition_ratio(words_lower)

    # Flag whether CoT was present
    had_cot = raw_text != text

    return {
        "length_chars": len(raw_text),
        "length_words": total_words,
        "length_words_raw": len(raw_text.split()),  # before CoT stripping
        "had_cot": had_cot,
        "shannon_char": round(shannon_char, 6),
        "shannon_word": round(shannon_word, 6),
        "shannon_word_uncorrected": round(shannon_word_raw, 6),
        "word_diversity": round(ttr, 6),
        "unique_words": num_types,
        "mtld": round(mtld, 4) if not (mtld != mtld) else None,  # NaN check
        "distinct_2": round(d2, 6) if not (d2 != d2) else None,
        "repetition_ratio": round(rep_ratio, 6),
    }


# ─────────────────────────────────────────────────────────────────────
# Ollama interface
# ─────────────────────────────────────────────────────────────────────

OLLAMA_API = "http://localhost:11434/api/generate"

def run_ollama(model: str, prompt: str, seed: int, temperature: float = 0.7,
               context: str = "", timeout: int = 180) -> str:
    """Run ollama via HTTP API with explicit temperature and seed."""
    seed_32 = seed % (2**32)

    full_prompt = f"{context}\n\n{prompt}" if context else prompt

    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "seed": seed_32,
            "temperature": temperature,
        },
    }

    try:
        resp = requests.post(OLLAMA_API, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip()
    except requests.Timeout:
        return "[TIMEOUT]"
    except Exception as e:
        return f"[ERROR: {str(e)[:100]}]"


# ─────────────────────────────────────────────────────────────────────
# Experiment runners
# ─────────────────────────────────────────────────────────────────────

def run_single_turn_experiments(model: str, num_samples: int, sources: dict,
                                temperature: float, rng: stdlib_random.Random) -> dict:
    """Run single-turn experiments with randomized source order."""
    results = {}
    source_names = list(sources.keys())

    for prompt_idx, prompt_info in enumerate(SINGLE_TURN_PROMPTS):
        prompt_text = prompt_info["text"]
        prompt_domain = prompt_info["domain"]
        prompt_constraint = prompt_info["constraint"]

        print(f"\n  [{prompt_idx+1}/{len(SINGLE_TURN_PROMPTS)}] [{prompt_domain}] {prompt_text[:50]}...")
        prompt_key = prompt_text
        results[prompt_key] = {"domain": prompt_domain, "constraint": prompt_constraint}

        # Randomize source order for this prompt
        order = source_names[:]
        rng.shuffle(order)

        for source_name in order:
            source = sources[source_name]
            samples = []
            for i in range(num_samples):
                seed = source.get_seed()
                output = run_ollama(model, prompt_text, seed, temperature=temperature)

                if not output.startswith("["):
                    metrics = calculate_metrics(output, strip_thinking=True)
                    samples.append({
                        "seed": seed, "seed_32": seed % (2**32),
                        "output": output, "metrics": metrics,
                    })
                    print(f"      {source_name}[{i+1}]: {metrics.get('length_words', 0)} words")
                else:
                    samples.append({"seed": seed, "seed_32": seed % (2**32),
                                    "output": output, "metrics": None})
                    print(f"      {source_name}[{i+1}]: {output}")

            valid = [s for s in samples if s["metrics"]]
            if valid:
                agg = {}
                for key in valid[0]["metrics"].keys():
                    if key in ("had_cot",):
                        continue
                    vals = [s["metrics"][key] for s in valid if s["metrics"].get(key) is not None]
                    if vals:
                        agg[f"{key}_mean"] = round(sum(vals) / len(vals), 6)
                        agg[f"{key}_std"] = round(
                            (sum((v - sum(vals)/len(vals))**2 for v in vals) / max(len(vals)-1, 1))**0.5, 6
                        ) if len(vals) > 1 else 0.0
                results[prompt_key][source_name] = {"samples": samples, "aggregate": agg}
            else:
                results[prompt_key][source_name] = {"samples": samples, "aggregate": None}

    return results


def run_multi_turn_experiments(model: str, num_samples: int, sources: dict,
                                temperature: float, rng: stdlib_random.Random) -> dict:
    """Run multi-turn conversation experiments with randomized source order."""
    results = {}
    source_names = list(sources.keys())

    for conv in MULTI_TURN_CONVERSATIONS:
        print(f"\n  [Multi-turn: {conv['name']}]")
        results[conv["name"]] = {}

        order = source_names[:]
        rng.shuffle(order)

        for source_name in order:
            source = sources[source_name]
            conv_samples = []

            for sample_idx in range(num_samples):
                seed = source.get_seed()
                context = ""
                turns = []

                for turn_idx, turn_prompt in enumerate(conv["turns"]):
                    output = run_ollama(model, turn_prompt, seed, temperature=temperature,
                                        context=context)
                    turns.append({
                        "prompt": turn_prompt,
                        "output": output,
                        "metrics": calculate_metrics(output, strip_thinking=True)
                                   if not output.startswith("[") else None,
                    })
                    context = f"{context}\n\nUser: {turn_prompt}\nAssistant: {output}"
                    print(f"      {source_name}[{sample_idx+1}] Turn {turn_idx+1}: "
                          f"{len(output)} chars")

                conv_samples.append({"seed": seed, "seed_32": seed % (2**32), "turns": turns})

            results[conv["name"]][source_name] = conv_samples

    return results


def run_full_experiment(model: str, num_samples: int, temperature: float,
                       prng_seeds: list, skip_multi_turn: bool = False) -> dict:
    """Run complete experiment suite with multiple PRNG streams."""
    print(f"\n{'='*70}")
    print(f" COMPREHENSIVE ENTROPY EXPERIMENT v2: {model}")
    print(f" Samples per condition: {num_samples}")
    print(f" Temperature: {temperature}")
    print(f" PRNG streams: {prng_seeds}")
    multi_turn_status = "SKIPPED" if skip_multi_turn else str(len(MULTI_TURN_CONVERSATIONS))
    print(f" Prompts: {len(SINGLE_TURN_PROMPTS)} single-turn, {multi_turn_status} multi-turn")
    print(f"{'='*70}")

    # Randomization RNG (separate from any source)
    order_rng = stdlib_random.Random(12345)

    all_stream_results = []

    for stream_idx, prng_seed in enumerate(prng_seeds):
        print(f"\n{'─'*50}")
        print(f"  PRNG Stream {stream_idx+1}/{len(prng_seeds)} (seed={prng_seed})")
        print(f"{'─'*50}")

        sources = {
            "PRNG": PRNGSource(seed=prng_seed),
            "TRNG": TRNGSource(),
            "HMIX": HMIXSource(),
        }

        stream_result = {
            "prng_stream_seed": prng_seed,
            "single_turn": {},
            "multi_turn": {},
        }

        print("\n  [PHASE 1: Single-Turn Prompts]")
        stream_result["single_turn"] = run_single_turn_experiments(
            model, num_samples, sources, temperature, order_rng)

        if not skip_multi_turn:
            print("\n  [PHASE 2: Multi-Turn Conversations]")
            stream_result["multi_turn"] = run_multi_turn_experiments(
                model, num_samples, sources, temperature, order_rng)
        else:
            stream_result["multi_turn"] = {"skipped": True, "note": "Multi-turn disabled via --no-multi-turn"}

        # Log seed distributions
        stream_result["seed_distributions"] = {
            name: {
                "seeds_64bit": src._seeds_generated,
                "seeds_32bit": [s % (2**32) for s in src._seeds_generated],
                "count": len(src._seeds_generated),
            }
            for name, src in sources.items()
        }

        all_stream_results.append(stream_result)

    results = {
        "model": model,
        "experiment_version": "v2",
        "timestamp": datetime.now().isoformat(),
        "num_samples": num_samples,
        "temperature": temperature,
        "prng_seeds": prng_seeds,
        "skip_multi_turn": skip_multi_turn,
        "num_prompts_single_turn": len(SINGLE_TURN_PROMPTS),
        "num_prompts_multi_turn": 0 if skip_multi_turn else len(MULTI_TURN_CONVERSATIONS),
        "prompt_domains": {
            d: sum(1 for p in SINGLE_TURN_PROMPTS if p["domain"] == d)
            for d in sorted(set(p["domain"] for p in SINGLE_TURN_PROMPTS))
        },
        "design_notes": {
            "source_order": "randomized per prompt (seed=12345)",
            "temperature": f"explicitly set to {temperature} for all models",
            "cot_handling": "stripped before metric computation; length_words_raw preserves original",
            "prng_streams": f"{len(prng_seeds)} independent Mersenne Twister streams",
            "hmix_note": "HMIX = SHA256(timestamp + secrets + counter), NOT quantum random",
            "metrics": "shannon_char, shannon_word (Miller-Madow corrected), TTR, MTLD, D2, rep_ratio",
            "seed_truncation": "64-bit → 32-bit via modulo for ollama compatibility",
        },
        "streams": all_stream_results,
    }

    return results


# ─────────────────────────────────────────────────────────────────────
# I/O
# ─────────────────────────────────────────────────────────────────────

def get_model_family(model: str) -> str:
    model_lower = model.lower()
    for family in ["mistral", "llama", "qwen", "gemma", "phi", "deepseek"]:
        if family in model_lower:
            return family
    return "other"


def save_results(results: dict, model: str) -> Path:
    family = get_model_family(model)
    output_dir = OUTPUT_DIR / family
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_safe = model.replace(":", "_").replace("/", "_")
    filename = f"v2_{model_safe}_{timestamp}.json"

    filepath = output_dir / filename
    with open(filepath, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved: {filepath}")
    return filepath


# ─────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive entropy experiment v2 (scientifically robust)")
    parser.add_argument("--model", type=str, help="Single model to test")
    parser.add_argument("--all-models", action="store_true", help="Test all available models")
    parser.add_argument("--samples", type=int, default=5, help="Samples per condition per prompt")
    parser.add_argument("--temperature", type=float, default=0.7,
                        help="Generation temperature (default: 0.7, same for all models)")
    parser.add_argument("--prng-seeds", type=str, default="42,123,7,999,314",
                        help="Comma-separated PRNG stream seeds (default: 42,123,7,999,314)")
    parser.add_argument("--single-stream", action="store_true",
                        help="Use only the first PRNG stream (faster, less robust)")
    parser.add_argument("--no-multi-turn", action="store_true",
                        help="Skip multi-turn conversations (faster, 23%% fewer generations)")
    parser.add_argument("--list-models", action="store_true", help="List available models")

    args = parser.parse_args()

    if args.list_models:
        subprocess.run(["ollama", "list"])
        return

    prng_seeds = [int(s.strip()) for s in args.prng_seeds.split(",")]
    if args.single_stream:
        prng_seeds = prng_seeds[:1]

    models_to_test = []

    if args.all_models:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        for line in result.stdout.strip().split("\n")[1:]:
            if line.strip():
                model = line.split()[0]
                skip_patterns = ["70b", "32b", "pm1000", "-vl", "vision"]
                if not any(p in model.lower() for p in skip_patterns):
                    models_to_test.append(model)
    elif args.model:
        models_to_test = [args.model]
    else:
        print("Specify --model or --all-models")
        return

    print(f"Models to test: {models_to_test}")
    print(f"PRNG streams: {prng_seeds}")
    print(f"Temperature: {args.temperature}")
    print(f"Samples per condition: {args.samples}")
    multi_turn_gens = 0 if args.no_multi_turn else len(MULTI_TURN_CONVERSATIONS) * 3 * 3 * args.samples
    total_gens = (len(SINGLE_TURN_PROMPTS) * 3 * args.samples + multi_turn_gens) * len(prng_seeds)
    print(f"Total generations per model: {total_gens}")
    if args.no_multi_turn:
        print("Multi-turn conversations: SKIPPED (--no-multi-turn)")

    for model in models_to_test:
        try:
            results = run_full_experiment(model, args.samples, args.temperature, prng_seeds,
                                         skip_multi_turn=args.no_multi_turn)
            filepath = save_results(results, model)
        except Exception as e:
            print(f"Error with {model}: {e}")
            import traceback
            traceback.print_exc()
            continue

    print("\n" + "=" * 70)
    print(" ALL EXPERIMENTS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
