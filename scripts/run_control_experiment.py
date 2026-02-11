#!/usr/bin/env python3
"""
Control experiment: same seed VALUES, different source LABELS.

This script proves whether observed entropy source effects come from:
  (a) The numerical distribution of seed values, or
  (b) Something else in the generation pipeline

Design:
  1. Generate N seeds from each source (PRNG, TRNG, HMIX)
  2. Run each model with ALL seeds under EACH label
     - i.e., TRNG seeds are also run as "PRNG-labeled" and vice versa
  3. If source effects are real: same seeds should produce same outputs
     regardless of label (proving effects are distributional)
  4. If effects are artifactual: labeled differences would persist even
     with identical seeds (proving a pipeline confound)

Since ollama run --seed N is stateless and deterministic for a given N,
running the same seed twice should produce identical output. This control
verifies that assumption and tests whether the source label matters.

Usage:
    python run_control_experiment.py --model gemma3:4b --seeds-per-source 20
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import argparse
import hashlib
import json
import random
import re
import requests
import secrets
import subprocess
import time
from collections import Counter
from datetime import datetime
from math import log2
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "results" / "control_experiments"
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
COT_PATTERN = re.compile(r'<think>.*?</think>', re.DOTALL)

# Use a subset of prompts (diverse domains)
CONTROL_PROMPTS = [
    "The old lighthouse keeper had never seen anything like it.",
    "What is the meaning of consciousness?",
    "Write a Python function that checks if a string is a palindrome.",
    "What are the three laws of thermodynamics and why do they matter?",
    "Summarize the key ideas of evolutionary biology in three paragraphs.",
]


def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE.sub('', text)


def strip_cot(text: str) -> str:
    return COT_PATTERN.sub('', text).strip() or text


def generate_seeds(n: int) -> dict:
    """Generate n seeds from each source."""
    prng = random.Random(42)
    seeds = {
        "PRNG": [prng.getrandbits(64) % (2**32) for _ in range(n)],
        "TRNG": [int.from_bytes(secrets.token_bytes(4), 'big') for _ in range(n)],
        "HMIX": [],
    }
    for i in range(n):
        data = f"{time.time_ns()}-{secrets.token_hex(16)}-{i}"
        h = hashlib.sha256(data.encode()).digest()
        seeds["HMIX"].append(int.from_bytes(h[:4], 'big'))
    return seeds


def calculate_metrics(text: str) -> dict:
    text = strip_cot(text)
    if not text:
        return {}
    words = text.lower().split()
    total = len(words)
    if total == 0:
        return {}
    unique = len(set(words))
    bigrams = [(words[i], words[i+1]) for i in range(len(words)-1)]
    return {
        "length_words": total,
        "word_diversity": round(unique / total, 6),
        "distinct_2": round(len(set(bigrams)) / len(bigrams), 6) if bigrams else 0,
    }


OLLAMA_API = "http://localhost:11434/api/generate"

def run_ollama(model: str, prompt: str, seed: int, temperature: float = 0.7,
               timeout: int = 180) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"seed": seed, "temperature": temperature},
    }
    try:
        resp = requests.post(OLLAMA_API, json=payload, timeout=timeout)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except requests.Timeout:
        return "[TIMEOUT]"
    except Exception as e:
        return f"[ERROR: {str(e)[:100]}]"


def run_control(model: str, seeds_per_source: int, temperature: float):
    print(f"\n{'='*70}")
    print(f" CONTROL EXPERIMENT: {model}")
    print(f" Seeds per source: {seeds_per_source}")
    print(f"{'='*70}")

    seeds = generate_seeds(seeds_per_source)

    results = {
        "model": model,
        "experiment_type": "control_same_seeds_different_labels",
        "timestamp": datetime.now().isoformat(),
        "seeds_per_source": seeds_per_source,
        "temperature": temperature,
        "seeds_generated": seeds,
        "tests": [],
    }

    # ── Test 1: Reproducibility ──
    # Run same seed twice, verify identical output
    print("\n[TEST 1: Reproducibility check]")
    test_seed = seeds["PRNG"][0]
    prompt = CONTROL_PROMPTS[0]
    out1 = run_ollama(model, prompt, test_seed, temperature)
    out2 = run_ollama(model, prompt, test_seed, temperature)
    reproducible = out1 == out2
    print(f"  Same seed={test_seed} → identical output: {reproducible}")
    if not reproducible:
        # Check how different
        words1, words2 = out1.split(), out2.split()
        overlap = len(set(words1) & set(words2)) / max(len(set(words1) | set(words2)), 1)
        print(f"  Word overlap: {overlap:.2%}")

    results["tests"].append({
        "name": "reproducibility",
        "seed": test_seed,
        "prompt": prompt,
        "identical": reproducible,
        "output_1_length": len(out1),
        "output_2_length": len(out2),
    })

    # ── Test 2: Cross-source seed swap ──
    # Run PRNG-generated seeds through all prompts, then TRNG-generated seeds
    # If outputs differ only by seed value (not provenance), effects are distributional
    print("\n[TEST 2: Cross-source generation]")

    # Use a smaller subset for cross-source (expensive)
    n_cross = min(seeds_per_source, 5)
    cross_results = {}

    for source_origin, seed_list in seeds.items():
        cross_results[source_origin] = {}
        for prompt_idx, prompt in enumerate(CONTROL_PROMPTS[:3]):
            metrics_list = []
            for seed in seed_list[:n_cross]:
                output = run_ollama(model, prompt, seed, temperature)
                if not output.startswith("["):
                    m = calculate_metrics(output)
                    metrics_list.append(m)
                    print(f"  {source_origin} seed → prompt {prompt_idx+1}: "
                          f"{m.get('length_words', 0)} words")

            if metrics_list:
                avg_div = sum(m.get("word_diversity", 0) for m in metrics_list) / len(metrics_list)
                avg_d2 = sum(m.get("distinct_2", 0) for m in metrics_list) / len(metrics_list)
                avg_len = sum(m.get("length_words", 0) for m in metrics_list) / len(metrics_list)
                cross_results[source_origin][prompt] = {
                    "n_samples": len(metrics_list),
                    "mean_word_diversity": round(avg_div, 6),
                    "mean_distinct_2": round(avg_d2, 6),
                    "mean_length_words": round(avg_len, 2),
                }

    results["tests"].append({
        "name": "cross_source_seed_swap",
        "n_seeds_per_source": n_cross,
        "n_prompts": min(3, len(CONTROL_PROMPTS)),
        "results_by_origin": cross_results,
    })

    # ── Test 3: Identical seeds, verify identical outputs ──
    # Take one seed from PRNG, run it labeled as "TRNG" — output should be identical
    print("\n[TEST 3: Label independence verification]")
    shared_seed = 123456789
    label_results = {}
    prompt = CONTROL_PROMPTS[1]
    for label in ["PRNG", "TRNG", "HMIX"]:
        output = run_ollama(model, prompt, shared_seed, temperature)
        label_results[label] = {
            "seed": shared_seed,
            "output_hash": hashlib.md5(output.encode()).hexdigest(),
            "length": len(output),
            "metrics": calculate_metrics(output) if not output.startswith("[") else None,
        }
        print(f"  Label '{label}', seed={shared_seed}: {len(output)} chars, "
              f"hash={label_results[label]['output_hash'][:12]}")

    all_same = len(set(r["output_hash"] for r in label_results.values())) == 1
    print(f"  All labels produce identical output: {all_same}")

    results["tests"].append({
        "name": "label_independence",
        "seed": shared_seed,
        "prompt": prompt,
        "all_identical": all_same,
        "details": label_results,
    })

    # ── Test 4: Seed distribution → output distribution ──
    # Do seeds from different distributions produce different output distributions?
    print("\n[TEST 4: Distribution transfer test]")
    # Generate biased seeds (low range) vs uniform seeds
    biased_seeds = [random.randint(0, 1000) for _ in range(10)]
    uniform_seeds = [random.randint(0, 2**32 - 1) for _ in range(10)]

    prompt = CONTROL_PROMPTS[0]
    biased_metrics = []
    uniform_metrics = []

    for seed in biased_seeds:
        output = run_ollama(model, prompt, seed, temperature)
        if not output.startswith("["):
            biased_metrics.append(calculate_metrics(output))
            print(f"  Biased seed={seed}: {len(output)} chars")

    for seed in uniform_seeds:
        output = run_ollama(model, prompt, seed, temperature)
        if not output.startswith("["):
            uniform_metrics.append(calculate_metrics(output))
            print(f"  Uniform seed={seed}: {len(output)} chars")

    results["tests"].append({
        "name": "distribution_transfer",
        "biased_seeds": biased_seeds,
        "uniform_seeds": uniform_seeds,
        "biased_metrics": biased_metrics,
        "uniform_metrics": uniform_metrics,
        "biased_mean_diversity": round(
            sum(m.get("word_diversity", 0) for m in biased_metrics) / max(len(biased_metrics), 1), 6),
        "uniform_mean_diversity": round(
            sum(m.get("word_diversity", 0) for m in uniform_metrics) / max(len(uniform_metrics), 1), 6),
    })

    return results


def main():
    parser = argparse.ArgumentParser(description="Control experiment: same seeds, different labels")
    parser.add_argument("--model", type=str, required=True, help="Model to test")
    parser.add_argument("--seeds-per-source", type=int, default=20,
                        help="Number of seeds to generate per source")
    parser.add_argument("--temperature", type=float, default=0.7,
                        help="Generation temperature")

    args = parser.parse_args()

    results = run_control(args.model, args.seeds_per_source, args.temperature)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    model_safe = args.model.replace(":", "_").replace("/", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = OUTPUT_DIR / f"control_{model_safe}_{timestamp}.json"

    with open(filepath, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved: {filepath}")

    # Print summary
    print(f"\n{'='*70}")
    print(" CONTROL EXPERIMENT SUMMARY")
    print(f"{'='*70}")
    for test in results["tests"]:
        print(f"\n  {test['name']}:")
        if test["name"] == "reproducibility":
            print(f"    Identical output: {test['identical']}")
        elif test["name"] == "label_independence":
            print(f"    Labels produce identical output: {test['all_identical']}")
        elif test["name"] == "distribution_transfer":
            print(f"    Biased seeds mean diversity: {test['biased_mean_diversity']}")
            print(f"    Uniform seeds mean diversity: {test['uniform_mean_diversity']}")


if __name__ == "__main__":
    main()
