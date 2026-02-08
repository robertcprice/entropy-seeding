#!/usr/bin/env python3
"""
Run entropy source comparison experiments on local models via Ollama.

Usage:
    python run_local_entropy_experiment.py --model mistral:latest
    python run_local_entropy_experiment.py --model llama3.1:8b
    python run_local_entropy_experiment.py --model qwen3:8b
"""

import argparse
import hashlib
import json
import os
import re
import secrets
import struct
import subprocess
import sys
from collections import Counter
from datetime import datetime
from math import log2
from pathlib import Path

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "results" / "valid_entropy_comparisons"

# ANSI escape code pattern
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

# Test prompts
PROMPTS = [
    "The old lighthouse keeper had never seen anything like it.",
    "She opened the letter, and everything changed.",
    "Once upon a time, in a kingdom by the sea,",
    "Explain the concept of entropy to a five-year-old.",
    "What is the meaning of consciousness?",
    "Think of a color you have never seen before. Describe it.",
    "Is it ever ethical to tell a lie? If so, under what circumstances?",
]


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    return ANSI_ESCAPE.sub('', text)


class PRNGSource:
    """Pseudo-random number generator (deterministic)."""
    def __init__(self, seed: int = 42):
        import random
        self.rng = random.Random(seed)
        self.name = "PRNG"
        self.description = "Standard pseudo-random (deterministic, seed=42)"

    def get_seed(self) -> int:
        return self.rng.getrandbits(64)


class TRNGSource:
    """True random number generator (OS cryptographic RNG)."""
    def __init__(self):
        self.name = "TRNG"
        self.description = "OS cryptographic RNG (/dev/urandom)"

    def get_seed(self) -> int:
        return int.from_bytes(secrets.token_bytes(8), byteorder='big')


class QRNGSource:
    """Quantum random number generator (simulated via hash mixing)."""
    def __init__(self):
        self.name = "QRNG"
        self.description = "Quantum-inspired RNG (hash mixing + timing)"
        self._counter = 0

    def get_seed(self) -> int:
        # Mix multiple entropy sources for quantum-like behavior
        import time
        self._counter += 1
        data = f"{time.time_ns()}-{secrets.token_hex(16)}-{self._counter}"
        h = hashlib.sha256(data.encode()).digest()
        return int.from_bytes(h[:8], byteorder='big')


def calculate_shannon_entropy(text: str) -> float:
    """Calculate Shannon entropy of text."""
    if not text:
        return 0.0
    char_counts = Counter(text)
    total = len(text)
    return -sum((c/total) * log2(c/total) for c in char_counts.values() if c > 0)


def calculate_word_entropy(text: str) -> float:
    """Calculate word-level Shannon entropy."""
    words = text.split()
    if not words:
        return 0.0
    word_counts = Counter(words)
    total = len(words)
    return -sum((c/total) * log2(c/total) for c in word_counts.values() if c > 0)


def calculate_metrics(text: str) -> dict:
    """Calculate all metrics for a text sample."""
    words = text.split()
    chars = list(text)

    return {
        "length_chars": len(text),
        "length_words": len(words),
        "shannon_char": calculate_shannon_entropy(text),
        "shannon_word": calculate_word_entropy(text),
        "unique_words": len(set(words)),
        "unique_chars": len(set(chars)),
        "word_diversity": len(set(words)) / len(words) if words else 0,
        "char_diversity": len(set(chars)) / len(chars) if chars else 0,
    }


def run_ollama(model: str, prompt: str, seed: int, timeout: int = 120) -> str:
    """Run ollama with specified seed and return output."""
    # Ollama seed must be 32-bit
    seed_32 = seed % (2**32)

    cmd = [
        "ollama", "run", model,
        "--seed", str(seed_32),
        prompt
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )
        return strip_ansi(result.stdout).strip()
    except subprocess.TimeoutExpired:
        return "[TIMEOUT]"
    except subprocess.CalledProcessError as e:
        return f"[ERROR: {e.stderr[:100]}]"
    except Exception as e:
        return f"[ERROR: {str(e)[:100]}]"


def run_experiment(model: str, num_samples: int = 5):
    """Run full entropy comparison experiment."""
    print(f"\n{'='*60}")
    print(f" ENTROPY SOURCE COMPARISON: {model}")
    print(f"{'='*60}\n")

    sources = {
        "PRNG": PRNGSource(seed=42),
        "TRNG": TRNGSource(),
        "QRNG": QRNGSource(),
    }

    results = {
        "model": model,
        "timestamp": datetime.now().isoformat(),
        "num_samples": num_samples,
        "prompts": {},
    }

    for prompt_idx, prompt in enumerate(PROMPTS):
        print(f"\n[{prompt_idx+1}/{len(PROMPTS)}] Prompt: {prompt[:50]}...")
        results["prompts"][prompt] = {}

        for source_name, source in sources.items():
            print(f"  Testing {source_name}...")
            samples = []

            for sample_idx in range(num_samples):
                seed = source.get_seed()
                output = run_ollama(model, prompt, seed)

                if not output.startswith("["):
                    metrics = calculate_metrics(output)
                    samples.append({
                        "seed": seed,
                        "output": output,
                        "metrics": metrics,
                    })
                    print(f"    Sample {sample_idx+1}: {len(output)} chars, "
                          f"shannon={metrics['shannon_char']:.2f}")
                else:
                    print(f"    Sample {sample_idx+1}: {output}")
                    samples.append({
                        "seed": seed,
                        "output": output,
                        "metrics": None,
                    })

            # Aggregate metrics for this source
            valid_samples = [s for s in samples if s["metrics"]]
            if valid_samples:
                agg_metrics = {}
                for key in valid_samples[0]["metrics"].keys():
                    values = [s["metrics"][key] for s in valid_samples]
                    agg_metrics[f"{key}_mean"] = sum(values) / len(values)
                    agg_metrics[f"{key}_min"] = min(values)
                    agg_metrics[f"{key}_max"] = max(values)

                results["prompts"][prompt][source_name] = {
                    "samples": samples,
                    "aggregate_metrics": agg_metrics,
                    "valid_samples": len(valid_samples),
                }
            else:
                results["prompts"][prompt][source_name] = {
                    "samples": samples,
                    "aggregate_metrics": None,
                    "valid_samples": 0,
                }

    return results


def save_results(results: dict, model: str):
    """Save results to JSON file."""
    # Determine model family
    model_lower = model.lower()
    if "mistral" in model_lower:
        family = "mistral"
    elif "llama" in model_lower:
        family = "llama"
    elif "qwen" in model_lower:
        family = "qwen"
    elif "gemma" in model_lower:
        family = "gemma"
    else:
        family = "other"

    # Create output directory
    output_dir = OUTPUT_DIR / family
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_safe = model.replace(":", "_").replace("/", "_")
    filename = f"entropy_comparison_{model_safe}_{timestamp}.json"

    filepath = output_dir / filename
    with open(filepath, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {filepath}")
    return filepath


def generate_summary(results: dict) -> str:
    """Generate markdown summary of results."""
    lines = [f"# Entropy Comparison: {results['model']}\n"]
    lines.append(f"**Timestamp:** {results['timestamp']}")
    lines.append(f"**Samples per condition:** {results['num_samples']}\n")

    for prompt, sources in results["prompts"].items():
        lines.append(f"\n## Prompt: \"{prompt[:50]}...\"\n")
        lines.append("| Metric | PRNG | TRNG | QRNG |")
        lines.append("|--------|------|------|------|")

        metrics_to_show = ["shannon_char_mean", "shannon_word_mean",
                          "word_diversity_mean", "length_words_mean"]

        for metric in metrics_to_show:
            prng = sources.get("PRNG", {}).get("aggregate_metrics", {})
            trng = sources.get("TRNG", {}).get("aggregate_metrics", {})
            qrng = sources.get("QRNG", {}).get("aggregate_metrics", {})

            prng_val = prng.get(metric, "N/A") if prng else "N/A"
            trng_val = trng.get(metric, "N/A") if trng else "N/A"
            qrng_val = qrng.get(metric, "N/A") if qrng else "N/A"

            if isinstance(prng_val, float):
                prng_val = f"{prng_val:.3f}"
            if isinstance(trng_val, float):
                trng_val = f"{trng_val:.3f}"
            if isinstance(qrng_val, float):
                qrng_val = f"{qrng_val:.3f}"

            metric_name = metric.replace("_mean", "")
            lines.append(f"| {metric_name} | {prng_val} | {trng_val} | {qrng_val} |")

        # Sample outputs
        lines.append("\n### Sample Outputs\n")
        for source_name in ["PRNG", "TRNG", "QRNG"]:
            source_data = sources.get(source_name, {})
            samples = source_data.get("samples", [])
            if samples and samples[0].get("output") and not samples[0]["output"].startswith("["):
                output = samples[0]["output"][:150].replace("\n", " ")
                lines.append(f"**{source_name}:** {output}...\n")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Run entropy comparison experiments")
    parser.add_argument("--model", type=str, default="mistral:latest",
                       help="Ollama model to use (default: mistral:latest)")
    parser.add_argument("--samples", type=int, default=3,
                       help="Number of samples per condition (default: 3)")
    parser.add_argument("--list-models", action="store_true",
                       help="List available Ollama models")

    args = parser.parse_args()

    if args.list_models:
        print("Available Ollama models:")
        subprocess.run(["ollama", "list"])
        return

    print(f"Running entropy experiment on: {args.model}")
    print(f"Samples per condition: {args.samples}")

    # Check if model exists
    try:
        result = subprocess.run(["ollama", "show", args.model],
                               capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: Model '{args.model}' not found. Run 'ollama pull {args.model}'")
            sys.exit(1)
    except FileNotFoundError:
        print("Error: Ollama not found. Please install Ollama first.")
        sys.exit(1)

    # Run experiment
    results = run_experiment(args.model, args.samples)

    # Save results
    filepath = save_results(results, args.model)

    # Generate summary
    summary = generate_summary(results)
    summary_path = filepath.with_suffix(".md")
    with open(summary_path, "w") as f:
        f.write(summary)
    print(f"Summary saved to: {summary_path}")

    print("\n" + "="*60)
    print(" EXPERIMENT COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
