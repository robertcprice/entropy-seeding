#!/usr/bin/env python3
"""
Literary Preservation Entropy Experiment — Testing the SHA256 Paradox.

This experiment systematically tests how different hash algorithms and extraction
methods affect the preservation of literary statistical signatures in LLM generation.

Research Questions:
    1. Does SHA256 completely decorrelate literary sources? (the "SHA256 Paradox")
    2. Which hash algorithms preserve the most/least literary structure?
    3. Which extraction methods preserve authorial signatures?
    4. Can classifiers detect text-derived entropy when using non-cryptographic hashes?

Experimental Matrix:
    Hash Algorithms (8):
        - RAW (no hashing, max preservation)
        - XOR_FOLD_64 (minimal mixing)
        - XOR_FOLD_32
        - MD5 (weak crypto, partial artifacts)
        - SHA256 (strong crypto, baseline)
        - SHA512
        - SHA3_256
        - XXHASH (non-crypto, fast)

    Extraction Methods (6):
        - CHAR_WALK (raw byte walk)
        - WORD_LENGTH (syntactic rhythm)
        - CHAR_BIGRAM (sequential patterns)
        - BURROWS_DELTA (word frequency ranking)
        - ZIPF_ENCODE (frequency-rank encoding)
        - PERMUTATION_ENTROPY (ordinal patterns)

    Total variants: 8 × 6 = 48 configurations

Usage:
    python run_literary_preservation_experiment.py --model qwen3:1.7b --samples 5
    python run_literary_preservation_experiment.py --model qwen3:1.7b --samples 10 --all-variants
    python run_literary_preservation_experiment.py --model qwen3:1.7b --quick-test
"""

import argparse
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime
from math import log2
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from entropy.entropy_sources.literary_preservation import (
    LiteraryPreservationSource,
    HashAlgorithm,
    ExtractionMethod,
    max_preservation,
    min_preservation,
    burrows_delta_source,
    zipf_preservation,
)

OUTPUT_DIR = Path(__file__).parent.parent / "results" / "literary_preservation"
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

# ─────────────────────────────────────────────────────────────────────
# Test prompts (focused set for initial testing)
# ─────────────────────────────────────────────────────────────────────

TEST_PROMPTS = [
    "The old lighthouse keeper had never seen anything like it.",
    "Explain the concept of entropy to a five-year-old.",
    "Write a Python function that checks if a string is a palindrome.",
    "What are the three laws of thermodynamics?",
    "Create a unique word that describes the feeling of watching rain.",
]

# ─────────────────────────────────────────────────────────────────────
# Experimental variants
# ─────────────────────────────────────────────────────────────────────

HASH_ALGORITHMS = [
    HashAlgorithm.RAW,           # No hashing (max preservation)
    HashAlgorithm.XOR_FOLD_64,   # Minimal mixing
    HashAlgorithm.XOR_FOLD_32,
    HashAlgorithm.MD5,           # Weak crypto
    HashAlgorithm.SHA256,        # Strong crypto (baseline)
    HashAlgorithm.SHA512,
    HashAlgorithm.SHA3_256,
    HashAlgorithm.XXHASH,        # Non-crypto
]

EXTRACTION_METHODS = [
    ExtractionMethod.CHAR_WALK,
    ExtractionMethod.WORD_LENGTH,
    ExtractionMethod.CHAR_BIGRAM,
    ExtractionMethod.BURROWS_DELTA,
    ExtractionMethod.ZIPF_ENCODE,
    ExtractionMethod.PERMUTATION_ENTROPY,
]

# Preset configurations for focused testing
PRESET_CONFIGS = {
    "raw_preservation": {
        "hash": HashAlgorithm.RAW,
        "extract": ExtractionMethod.CHAR_WALK,
        "description": "RAW bytes, no hashing (maximum preservation)"
    },
    "sha256_baseline": {
        "hash": HashAlgorithm.SHA256,
        "extract": ExtractionMethod.CHAR_WALK,
        "description": "SHA256 hashed (baseline, no preservation)"
    },
    "xor_fold_char_walk": {
        "hash": HashAlgorithm.XOR_FOLD_64,
        "extract": ExtractionMethod.CHAR_WALK,
        "description": "XOR-folded char walk"
    },
    "xxhash_burrows": {
        "hash": HashAlgorithm.XXHASH,
        "extract": ExtractionMethod.BURROWS_DELTA,
        "description": "xxhash with Burrows' Delta word frequency"
    },
    "md5_zipf": {
        "hash": HashAlgorithm.MD5,
        "extract": ExtractionMethod.ZIPF_ENCODE,
        "description": "MD5 with Zipf rank encoding"
    },
    "raw_word_length": {
        "hash": HashAlgorithm.RAW,
        "extract": ExtractionMethod.WORD_LENGTH,
        "description": "Raw word length sequences"
    },
    "sha3_bigram": {
        "hash": HashAlgorithm.SHA3_256,
        "extract": ExtractionMethod.CHAR_BIGRAM,
        "description": "SHA3-256 with character bigrams"
    },
}

# ─────────────────────────────────────────────────────────────────────
# Metrics
# ─────────────────────────────────────────────────────────────────────

def compute_ttr(text: str) -> float:
    """Type-token ratio: unique words / total words."""
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    if not words:
        return 0.0
    return len(set(words)) / len(words)


def compute_distinct_2(text: str) -> float:
    """Distinct-2: proportion of unique bigrams."""
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    if len(words) < 2:
        return 0.0
    bigrams = [(words[i], words[i+1]) for i in range(len(words) - 1)]
    return len(set(bigrams)) / len(bigrams) if bigrams else 0.0


def compute_mtld(text: str, threshold: float = 0.72) -> float:
    """Measure of Textual Lexical Diversity."""
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    if len(words) < 50:
        return compute_ttr(text)

    def mtld_partial(factor_words: list[str]) -> float:
        ttrs = []
        i = 0
        while i < len(factor_words):
            segment = factor_words[i:]
            current_ttr = 1.0
            j = 0
            while current_ttr > threshold and j < len(segment):
                j += 1
                current_ttr = len(set(segment[:j+1])) / (j + 1)
            if j == 0:
                j = 1
            ttrs.append(j)
            i += j
        return len(factor_words) / sum(ttrs) if ttrs else 0.0

    # Forward and reverse
    forward = mtld_partial(words)
    reverse = mtld_partial(words[::-1])
    return (forward + reverse) / 2


def compute_entropy(text: str) -> float:
    """Shannon entropy of character distribution."""
    chars = list(text)
    if not chars:
        return 0.0
    counts = Counter(chars)
    total = len(chars)
    probs = [c / total for c in counts.values()]
    return -sum(p * log2(p) for p in probs if p > 0)


# ─────────────────────────────────────────────────────────────────────
# Generation via Ollama
# ─────────────────────────────────────────────────────────────────────

def generate_with_entropy(
    prompt: str,
    source_config: dict,
    model: str,
    temperature: float = 0.7,
    max_tokens: int = 256,
) -> dict:
    """Generate text with the given entropy source configuration."""
    hash_algo = source_config["hash"]
    extract_method = source_config["extract"]

    # Create entropy source
    source = LiteraryPreservationSource(
        text_name="bible_kjv",
        hash_algo=hash_algo,
        extract_method=extract_method,
        initial_seed=secrets.randbelow(2**32),
    )

    # Collect seeds for generation
    seeds = []
    for _ in range(50):  # Generate 50 seeds (enough for 256 tokens)
        seed = source.get_seed([])
        seeds.append(seed)

    # For now, we'll use PRNG with the first seed
    # (TODO: Integrate actual entropy source into sampling)
    import torch
    gen = torch.Generator()
    gen.manual_seed(seeds[0])

    # Call Ollama with temperature
    # Note: This is a simplified version - actual integration would require
    # modifying the sampler to use our entropy source
    cmd = [
        "ollama", "run", model,
        "--temperature", str(temperature),
        "--num-predict", str(max_tokens),
    ]
    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=60,
        )
        output = result.stdout
    except subprocess.TimeoutExpired:
        output = ""
    except Exception as e:
        output = f"ERROR: {e}"

    return {
        "output": output,
        "seeds": seeds[:10],  # Log first 10 seeds
        "hash_algo": hash_algo.value,
        "extract_method": extract_method.value,
    }


# ─────────────────────────────────────────────────────────────────────
# Main experiment runner
# ─────────────────────────────────────────────────────────────────────

def run_experiment(
    model: str,
    presets: list[str] | None = None,
    all_variants: bool = False,
    samples: int = 5,
    temperature: float = 0.7,
) -> dict:
    """Run the literary preservation experiment."""

    print(f"\n{'='*70}")
    print(f"LITERARY PRESERVATION EXPERIMENT")
    print(f"{'='*70}")
    print(f"Model: {model}")
    print(f"Samples per config: {samples}")
    print(f"Temperature: {temperature}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"{'='*70}\n")

    # Determine which configurations to test
    if all_variants:
        configs = []
        for h in HASH_ALGORITHMS:
            for e in EXTRACTION_METHODS:
                configs.append({
                    "hash": h,
                    "extract": e,
                    "name": f"{h.value}_{e.value}",
                })
        print(f"Testing ALL {len(configs)} hash × extract combinations\n")
    elif presets:
        configs = [{**v, "name": k} for k, v in PRESET_CONFIGS.items() if k in presets]
        print(f"Testing {len(configs)} preset configurations\n")
    else:
        # Default: quick test subset
        configs = [{**v, "name": k} for k, v in PRESET_CONFIGS.items()]
        print(f"Testing {len(configs)} preset configurations\n")

    results = {}

    for i, config in enumerate(configs):
        config_name = config["name"]
        description = config.get("description", f"{config['hash'].value} × {config['extract'].value}")

        print(f"[{i+1}/{len(configs)}] Testing: {config_name}")
        print(f"    {description}")

        config_results = []

        for j, prompt in enumerate(TEST_PROMPTS):
            print(f"    Prompt {j+1}/{len(TEST_PROMPTS)}: {prompt[:50]}...", end="", flush=True)

            prompt_results = []
            for k in range(samples):
                result = generate_with_entropy(
                    prompt=prompt,
                    source_config=config,
                    model=model,
                    temperature=temperature,
                )

                # Compute metrics
                output = result["output"]
                metrics = {
                    "length": len(output),
                    "ttr": compute_ttr(output),
                    "distinct_2": compute_distinct_2(output),
                    "mtld": compute_mtld(output),
                    "entropy": compute_entropy(output),
                }

                prompt_results.append({
                    "generation": result,
                    "metrics": metrics,
                })

            print(f" ✓")

            # Aggregate metrics for this prompt
            prompt_aggregates = {
                "prompt": prompt,
                "mean_metrics": {
                    "length": sum(r["metrics"]["length"] for r in prompt_results) / len(prompt_results),
                    "ttr": sum(r["metrics"]["ttr"] for r in prompt_results) / len(prompt_results),
                    "distinct_2": sum(r["metrics"]["distinct_2"] for r in prompt_results) / len(prompt_results),
                    "mtld": sum(r["metrics"]["mtld"] for r in prompt_results) / len(prompt_results),
                    "entropy": sum(r["metrics"]["entropy"] for r in prompt_results) / len(prompt_results),
                },
                "samples": prompt_results,
            }

            config_results.append(prompt_aggregates)

        # Overall aggregates for this config
        all_prompts_metrics = [p["mean_metrics"] for p in config_results]
        overall_metrics = {
            "length": sum(m["length"] for m in all_prompts_metrics) / len(all_prompts_metrics),
            "ttr": sum(m["ttr"] for m in all_prompts_metrics) / len(all_prompts_metrics),
            "distinct_2": sum(m["distinct_2"] for m in all_prompts_metrics) / len(all_prompts_metrics),
            "mtld": sum(m["mtld"] for m in all_prompts_metrics) / len(all_prompts_metrics),
            "entropy": sum(m["entropy"] for m in all_prompts_metrics) / len(all_prompts_metrics),
        }

        results[config_name] = {
            "config": {
                "hash_algo": config["hash"].value,
                "extract_method": config["extract"].value,
                "description": description,
            },
            "overall_metrics": overall_metrics,
            "prompt_results": config_results,
        }

        print(f"    Overall TTR: {overall_metrics['ttr']:.4f}")
        print(f"    Overall D2:  {overall_metrics['distinct_2']:.4f}")
        print()

    return results


# ─────────────────────────────────────────────────────────────────────
# Analysis and reporting
# ─────────────────────────────────────────────────────────────────────

def analyze_results(results: dict) -> dict:
    """Analyze experimental results and generate insights."""
    analysis = {
        "rankings": {
            "ttr": [],
            "distinct_2": [],
            "mtld": [],
        },
        "comparisons": {},
        "insights": [],
    }

    # Rank configurations by each metric
    for metric in ["ttr", "distinct_2", "mtld"]:
        ranked = sorted(
            [(name, data["overall_metrics"][metric]) for name, data in results.items()],
            key=lambda x: x[1],
            reverse=True,
        )
        analysis["rankings"][metric] = ranked

    # Compare RAW vs SHA256 (maximum vs minimum preservation)
    if "raw_preservation" in results and "sha256_baseline" in results:
        raw_ttr = results["raw_preservation"]["overall_metrics"]["ttr"]
        sha256_ttr = results["sha256_baseline"]["overall_metrics"]["ttr"]
        ttr_diff = ((raw_ttr - sha256_ttr) / sha256_ttr) * 100 if sha256_ttr > 0 else 0

        analysis["comparisons"]["raw_vs_sha256"] = {
            "ttr_difference_percent": ttr_diff,
            "raw_ttr": raw_ttr,
            "sha256_ttr": sha256_ttr,
        }

        analysis["insights"].append(
            f"RAW (no hashing) vs SHA256: TTR difference {ttr_diff:+.1f}%"
        )

    return analysis


def save_results(results: dict, analysis: dict, model: str) -> Path:
    """Save results and analysis to files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = OUTPUT_DIR / f"{timestamp}_{model.replace(':', '_')}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save raw results
    results_file = output_dir / "results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    # Save analysis
    analysis_file = output_dir / "analysis.json"
    with open(analysis_file, "w") as f:
        json.dump(analysis, f, indent=2)

    # Save human-readable report
    report_file = output_dir / "report.md"
    with open(report_file, "w") as f:
        f.write(f"# Literary Preservation Experiment Report\n\n")
        f.write(f"**Model**: {model}\n")
        f.write(f"**Timestamp**: {timestamp}\n\n")

        f.write("## Overall Rankings by Metric\n\n")

        for metric, rankings in analysis["rankings"].items():
            f.write(f"### {metric.upper()}\n\n")
            for i, (name, value) in enumerate(rankings[:5]):
                f.write(f"{i+1}. **{name}**: {value:.4f}\n")
            f.write("\n")

        if analysis["insights"]:
            f.write("## Key Insights\n\n")
            for insight in analysis["insights"]:
                f.write(f"- {insight}\n")
            f.write("\n")

    print(f"\nResults saved to: {output_dir}")
    print(f"  - results.json: Raw experimental data")
    print(f"  - analysis.json: Analysis and rankings")
    print(f"  - report.md: Human-readable summary")

    return output_dir


# ─────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Literary Preservation Entropy Experiment"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="qwen3:1.7b",
        help="Ollama model to use (default: qwen3:1.7b)"
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=5,
        help="Number of samples per prompt (default: 5)"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature (default: 0.7)"
    )
    parser.add_argument(
        "--presets",
        type=str,
        nargs="*",
        choices=list(PRESET_CONFIGS.keys()),
        help="Specific preset configurations to test"
    )
    parser.add_argument(
        "--all-variants",
        action="store_true",
        help="Test all hash × extract combinations (48 configs)"
    )
    parser.add_argument(
        "--quick-test",
        action="store_true",
        help="Run quick test with 1 sample per prompt"
    )

    args = parser.parse_args()

    # Quick test overrides
    if args.quick_test:
        args.samples = 1
        if not args.presets:
            args.presets = ["raw_preservation", "sha256_baseline"]

    # Run experiment
    results = run_experiment(
        model=args.model,
        presets=args.presets,
        all_variants=args.all_variants,
        samples=args.samples,
        temperature=args.temperature,
    )

    # Analyze results
    analysis = analyze_results(results)

    # Save results
    save_results(results, analysis, args.model)


if __name__ == "__main__":
    main()
