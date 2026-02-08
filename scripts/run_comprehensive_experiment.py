#!/usr/bin/env python3
"""
Comprehensive entropy source comparison with multi-turn conversations.

Usage:
    python run_comprehensive_experiment.py --model mistral:latest --samples 5
    python run_comprehensive_experiment.py --all-models --samples 3
"""

import argparse
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
from collections import Counter
from datetime import datetime
from math import log2
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "results" / "valid_entropy_comparisons"
SUMMARIES_DIR = Path(__file__).parent.parent / "results" / "formatted_summaries"

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

# Expanded prompts
SINGLE_TURN_PROMPTS = [
    # Creative writing
    "The old lighthouse keeper had never seen anything like it.",
    "She opened the letter, and everything changed.",
    "Once upon a time, in a kingdom by the sea,",
    "The robot looked at its hands and wondered what it meant to be alive.",
    "In the year 2157, humanity discovered they were not alone.",

    # Abstract/philosophical
    "Think of a color you have never seen before. Describe it in detail.",
    "What is the meaning of consciousness?",
    "Is it ever ethical to tell a lie? If so, under what circumstances?",
    "Describe what infinity feels like.",
    "What would music look like if you could see it?",

    # Technical/explanatory
    "Explain the concept of entropy to a five-year-old.",
    "How does a neural network learn?",
    "What is the relationship between time and gravity?",

    # Character/naming
    "Invent a name for a magical creature that lives in clouds.",
    "Create a unique word that describes the feeling of watching rain.",
]

# Multi-turn conversations
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


def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE.sub('', text)


class PRNGSource:
    def __init__(self, seed: int = 42):
        import random
        self.rng = random.Random(seed)
        self.name = "PRNG"

    def get_seed(self) -> int:
        return self.rng.getrandbits(64)


class TRNGSource:
    def __init__(self):
        self.name = "TRNG"

    def get_seed(self) -> int:
        return int.from_bytes(secrets.token_bytes(8), byteorder='big')


class QRNGSource:
    def __init__(self):
        self.name = "QRNG"
        self._counter = 0

    def get_seed(self) -> int:
        import time
        self._counter += 1
        data = f"{time.time_ns()}-{secrets.token_hex(16)}-{self._counter}"
        h = hashlib.sha256(data.encode()).digest()
        return int.from_bytes(h[:8], byteorder='big')


def calculate_metrics(text: str) -> dict:
    if not text:
        return {}

    words = text.split()
    chars = list(text)

    # Shannon entropy
    char_counts = Counter(chars)
    total_chars = len(chars)
    shannon_char = -sum((c/total_chars) * log2(c/total_chars)
                        for c in char_counts.values() if c > 0) if total_chars > 0 else 0

    word_counts = Counter(words)
    total_words = len(words)
    shannon_word = -sum((c/total_words) * log2(c/total_words)
                        for c in word_counts.values() if c > 0) if total_words > 0 else 0

    return {
        "length_chars": len(text),
        "length_words": total_words,
        "shannon_char": round(shannon_char, 4),
        "shannon_word": round(shannon_word, 4),
        "unique_words": len(set(words)),
        "word_diversity": round(len(set(words)) / total_words, 4) if total_words > 0 else 0,
    }


def run_ollama(model: str, prompt: str, seed: int, context: str = "", timeout: int = 180) -> str:
    """Run ollama with optional context for multi-turn."""
    seed_32 = seed % (2**32)

    full_prompt = f"{context}\n\n{prompt}" if context else prompt

    cmd = ["ollama", "run", model, "--seed", str(seed_32), full_prompt]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=True)
        return strip_ansi(result.stdout).strip()
    except subprocess.TimeoutExpired:
        return "[TIMEOUT]"
    except Exception as e:
        return f"[ERROR: {str(e)[:100]}]"


def run_single_turn_experiments(model: str, num_samples: int, sources: dict) -> dict:
    """Run single-turn prompt experiments."""
    results = {}

    for prompt_idx, prompt in enumerate(SINGLE_TURN_PROMPTS):
        print(f"\n  [{prompt_idx+1}/{len(SINGLE_TURN_PROMPTS)}] {prompt[:50]}...")
        results[prompt] = {}

        for source_name, source in sources.items():
            samples = []
            for i in range(num_samples):
                seed = source.get_seed()
                output = run_ollama(model, prompt, seed)

                if not output.startswith("["):
                    metrics = calculate_metrics(output)
                    samples.append({"seed": seed, "output": output, "metrics": metrics})
                    print(f"      {source_name}[{i+1}]: {len(output)} chars")
                else:
                    samples.append({"seed": seed, "output": output, "metrics": None})
                    print(f"      {source_name}[{i+1}]: {output}")

            valid = [s for s in samples if s["metrics"]]
            if valid:
                agg = {}
                for key in valid[0]["metrics"].keys():
                    vals = [s["metrics"][key] for s in valid]
                    agg[f"{key}_mean"] = round(sum(vals)/len(vals), 4)
                results[prompt][source_name] = {"samples": samples, "aggregate": agg}
            else:
                results[prompt][source_name] = {"samples": samples, "aggregate": None}

    return results


def run_multi_turn_experiments(model: str, num_samples: int, sources: dict) -> dict:
    """Run multi-turn conversation experiments."""
    results = {}

    for conv in MULTI_TURN_CONVERSATIONS:
        print(f"\n  [Multi-turn: {conv['name']}]")
        results[conv["name"]] = {}

        for source_name, source in sources.items():
            conv_samples = []

            for sample_idx in range(num_samples):
                seed = source.get_seed()
                context = ""
                turns = []

                for turn_idx, turn_prompt in enumerate(conv["turns"]):
                    output = run_ollama(model, turn_prompt, seed, context)
                    turns.append({
                        "prompt": turn_prompt,
                        "output": output,
                        "metrics": calculate_metrics(output) if not output.startswith("[") else None
                    })
                    context = f"{context}\n\nUser: {turn_prompt}\nAssistant: {output}"
                    print(f"      {source_name}[{sample_idx+1}] Turn {turn_idx+1}: {len(output)} chars")

                conv_samples.append({"seed": seed, "turns": turns})

            results[conv["name"]][source_name] = conv_samples

    return results


def run_full_experiment(model: str, num_samples: int):
    """Run complete experiment suite."""
    print(f"\n{'='*70}")
    print(f" COMPREHENSIVE ENTROPY EXPERIMENT: {model}")
    print(f" Samples per condition: {num_samples}")
    print(f"{'='*70}")

    sources = {
        "PRNG": PRNGSource(seed=42),
        "TRNG": TRNGSource(),
        "QRNG": QRNGSource(),
    }

    results = {
        "model": model,
        "timestamp": datetime.now().isoformat(),
        "num_samples": num_samples,
        "single_turn": {},
        "multi_turn": {},
    }

    print("\n[PHASE 1: Single-Turn Prompts]")
    results["single_turn"] = run_single_turn_experiments(model, num_samples, sources)

    print("\n[PHASE 2: Multi-Turn Conversations]")
    results["multi_turn"] = run_multi_turn_experiments(model, num_samples, sources)

    return results


def get_model_family(model: str) -> str:
    model_lower = model.lower()
    if "mistral" in model_lower:
        return "mistral"
    elif "llama" in model_lower:
        return "llama"
    elif "qwen" in model_lower:
        return "qwen"
    elif "gemma" in model_lower:
        return "gemma"
    else:
        return "other"


def save_results(results: dict, model: str) -> Path:
    family = get_model_family(model)
    output_dir = OUTPUT_DIR / family
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_safe = model.replace(":", "_").replace("/", "_")
    filename = f"comprehensive_{model_safe}_{timestamp}.json"

    filepath = output_dir / filename
    with open(filepath, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved: {filepath}")
    return filepath


def generate_model_summary(results: dict) -> str:
    """Generate comprehensive markdown summary."""
    lines = [f"# Comprehensive Entropy Comparison: {results['model']}\n"]
    lines.append(f"**Timestamp:** {results['timestamp']}")
    lines.append(f"**Samples per condition:** {results['num_samples']}\n")

    # Single-turn results
    lines.append("## Single-Turn Prompts\n")

    for prompt, sources in results.get("single_turn", {}).items():
        lines.append(f"### {prompt[:60]}...\n")
        lines.append("| Metric | PRNG | TRNG | QRNG |")
        lines.append("|--------|------|------|------|")

        for metric in ["shannon_char_mean", "shannon_word_mean", "word_diversity_mean", "length_words_mean"]:
            row = [metric.replace("_mean", "")]
            for src in ["PRNG", "TRNG", "QRNG"]:
                agg = sources.get(src, {}).get("aggregate", {})
                val = agg.get(metric, "N/A") if agg else "N/A"
                row.append(f"{val:.3f}" if isinstance(val, float) else str(val))
            lines.append(f"| {' | '.join(row)} |")

        # Sample outputs
        lines.append("\n**Sample Outputs:**\n")
        for src in ["PRNG", "TRNG", "QRNG"]:
            samples = sources.get(src, {}).get("samples", [])
            if samples and samples[0].get("output") and not samples[0]["output"].startswith("["):
                out = samples[0]["output"][:200].replace("\n", " ")
                lines.append(f"- **{src}:** {out}...\n")
        lines.append("")

    # Multi-turn results
    lines.append("\n## Multi-Turn Conversations\n")

    for conv_name, sources in results.get("multi_turn", {}).items():
        lines.append(f"### {conv_name.title()}\n")

        for src in ["PRNG", "TRNG", "QRNG"]:
            samples = sources.get(src, [])
            if samples and samples[0].get("turns"):
                lines.append(f"\n**{src} Conversation:**\n")
                for i, turn in enumerate(samples[0]["turns"]):
                    prompt = turn["prompt"][:50]
                    output = turn["output"][:150].replace("\n", " ") if turn["output"] else "[No output]"
                    lines.append(f"- **Turn {i+1}** ({prompt}...): {output}...\n")
        lines.append("")

    return "\n".join(lines)


def update_master_summary():
    """Update the master summary file with all results."""
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)

    lines = ["# Entropy Source Comparison - Master Summary\n"]
    lines.append(f"**Last Updated:** {datetime.now().isoformat()}\n")
    lines.append("## Available Model Results\n")

    for family_dir in sorted(OUTPUT_DIR.iterdir()):
        if family_dir.is_dir() and family_dir.name not in ["formatted_summaries"]:
            json_files = list(family_dir.glob("*.json"))
            if json_files:
                lines.append(f"\n### {family_dir.name.upper()}\n")
                lines.append(f"- **Files:** {len(json_files)}")

                # Get latest file info
                latest = max(json_files, key=lambda x: x.stat().st_mtime)
                try:
                    with open(latest) as f:
                        data = json.load(f)
                    lines.append(f"- **Latest:** {latest.name}")
                    lines.append(f"- **Model:** {data.get('model', 'Unknown')}")
                    lines.append(f"- **Timestamp:** {data.get('timestamp', 'Unknown')}")
                except:
                    pass

    master_path = SUMMARIES_DIR / "MASTER_SUMMARY.md"
    with open(master_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Master summary updated: {master_path}")


def main():
    parser = argparse.ArgumentParser(description="Comprehensive entropy experiments")
    parser.add_argument("--model", type=str, help="Single model to test")
    parser.add_argument("--all-models", action="store_true", help="Test all available models")
    parser.add_argument("--samples", type=int, default=3, help="Samples per condition")
    parser.add_argument("--list-models", action="store_true", help="List available models")

    args = parser.parse_args()

    if args.list_models:
        subprocess.run(["ollama", "list"])
        return

    models_to_test = []

    if args.all_models:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        for line in result.stdout.strip().split("\n")[1:]:
            if line.strip():
                model = line.split()[0]
                # Skip very large models
                if "70b" not in model.lower() and "32b" not in model.lower():
                    models_to_test.append(model)
    elif args.model:
        models_to_test = [args.model]
    else:
        print("Specify --model or --all-models")
        return

    print(f"Models to test: {models_to_test}")

    for model in models_to_test:
        try:
            results = run_full_experiment(model, args.samples)
            filepath = save_results(results, model)

            # Generate individual summary
            summary = generate_model_summary(results)
            summary_path = filepath.with_suffix(".md")
            with open(summary_path, "w") as f:
                f.write(summary)
            print(f"Summary saved: {summary_path}")

        except Exception as e:
            print(f"Error with {model}: {e}")
            continue

    # Update master summary
    update_master_summary()

    print("\n" + "="*70)
    print(" ALL EXPERIMENTS COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
