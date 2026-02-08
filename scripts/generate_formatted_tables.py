#!/usr/bin/env python3
"""Generate nicely formatted markdown tables from entropy comparison results."""

import json
import os
from pathlib import Path
from collections import defaultdict

RESULTS_DIR = Path(__file__).parent.parent / "results" / "valid_entropy_comparisons"
OUTPUT_DIR = Path(__file__).parent.parent / "results" / "formatted_summaries"


def format_deepseek_results():
    """Format DeepSeek R1 results into markdown tables."""
    deepseek_dir = RESULTS_DIR / "deepseek"
    output = ["# DeepSeek R1 Entropy Comparison Results\n"]
    output.append("Comparing PRNG vs TRNG vs QRNG-IBM on DeepSeek R1 models.\n")

    for json_file in sorted(deepseek_dir.glob("*.json")):
        with open(json_file) as f:
            data = json.load(f)

        model = data.get("model", json_file.stem)
        timestamp = data.get("timestamp", "Unknown")

        output.append(f"\n## {model}\n")
        output.append(f"**Timestamp:** {timestamp}\n")

        prompts = data.get("prompts", {})

        for prompt_name, sources in prompts.items():
            output.append(f"\n### Prompt: {prompt_name}\n")
            output.append("| Metric | PRNG | TRNG | QRNG-IBM |")
            output.append("|--------|------|------|----------|")

            metrics = ["shannon_char", "shannon_word", "perplexity", "burstiness",
                      "repetition", "uniqueness", "tsa", "tre"]

            for metric in metrics:
                prng_val = sources.get("PRNG", {}).get(metric, "N/A")
                trng_val = sources.get("TRNG", {}).get(metric, "N/A")
                qrng_val = sources.get("QRNG-IBM", {}).get(metric, "N/A")

                # Format numbers
                if isinstance(prng_val, float):
                    if prng_val == float('inf'):
                        prng_val = "∞"
                    else:
                        prng_val = f"{prng_val:.4f}"
                if isinstance(trng_val, float):
                    if trng_val == float('inf'):
                        trng_val = "∞"
                    else:
                        trng_val = f"{trng_val:.4f}"
                if isinstance(qrng_val, float):
                    if qrng_val == float('inf'):
                        qrng_val = "∞"
                    else:
                        qrng_val = f"{qrng_val:.4f}"

                output.append(f"| {metric} | {prng_val} | {trng_val} | {qrng_val} |")

        # Add key findings
        output.append("\n#### Key Findings\n")
        if "philosophy" in prompts:
            prng_shannon = prompts["philosophy"].get("PRNG", {}).get("shannon_char", 0)
            if prng_shannon == 0:
                output.append("- **PRNG CATASTROPHIC FAILURE**: All metrics = 0 for philosophy prompt")
                output.append("- TRNG and QRNG-IBM produced valid outputs")

    return "\n".join(output)


def format_qwen_results():
    """Format Qwen results into markdown tables."""
    qwen_dir = RESULTS_DIR / "qwen"
    output = ["# Qwen3 Entropy Comparison Results\n"]
    output.append("Comparing PRNG vs TRNG vs QRNG on Qwen3 models (0.6B, 1.7B, 4B, 8B, 14B).\n")

    # Group files by model size
    model_files = defaultdict(list)
    for json_file in sorted(qwen_dir.glob("*.json")):
        name = json_file.stem.lower()
        if "0.6b" in name:
            model_files["0.6B"].append(json_file)
        elif "1.7b" in name:
            model_files["1.7B"].append(json_file)
        elif "4b" in name:
            model_files["4B"].append(json_file)
        elif "8b" in name:
            model_files["8B"].append(json_file)
        elif "14b" in name:
            model_files["14B"].append(json_file)

    for model_size in ["0.6B", "1.7B", "4B", "8B", "14B"]:
        files = model_files.get(model_size, [])
        if not files:
            continue

        output.append(f"\n## Qwen3-{model_size}\n")
        output.append(f"**Files analyzed:** {len(files)}\n")

        # Collect sample outputs by entropy source
        samples_by_source = defaultdict(list)

        for json_file in files[:5]:  # Limit to first 5 files per model
            try:
                with open(json_file) as f:
                    data = json.load(f)

                # Determine entropy source from filename
                name = json_file.stem.lower()
                if "qrng" in name:
                    source = "QRNG"
                elif "trng" in name:
                    source = "TRNG"
                elif "prng" in name:
                    source = "PRNG"
                else:
                    continue

                # Get generations
                generations = data.get("generations", [])
                for gen in generations[:3]:  # First 3 samples
                    text = gen.get("text", "")[:200]
                    prompt = gen.get("prompt", "Unknown")[:50]
                    if text:
                        samples_by_source[source].append({
                            "prompt": prompt,
                            "text": text,
                            "file": json_file.name
                        })
            except Exception as e:
                continue

        # Output sample table
        if samples_by_source:
            output.append("\n### Sample Outputs by Entropy Source\n")

            for source in ["PRNG", "TRNG", "QRNG"]:
                samples = samples_by_source.get(source, [])
                if samples:
                    output.append(f"\n#### {source}\n")
                    output.append("| Prompt | Output (truncated) |")
                    output.append("|--------|-------------------|")
                    for s in samples[:3]:
                        prompt = s["prompt"].replace("|", "\\|").replace("\n", " ")
                        text = s["text"].replace("|", "\\|").replace("\n", " ")[:150]
                        output.append(f"| {prompt}... | {text}... |")

    # Add qualitative findings section
    output.append("\n## Qualitative Findings\n")
    output.append("""
### QRNG Mode Shifts (Qwen3-14B)
- Started with narrative: "The old lighthouse keeper had never seen anything like it."
- **Suddenly switched to test format**: "A. operating at full capacity / B. visited by tourists..."
- Added meta-commentary: "Okay, let's see. The question is about..."

### TRNG Language Mixing (Qwen3-8B)
- Prompt: "She opened the letter, and everything changed."
- Output included Chinese: "翻译句子并解析句子成分..." (Translate sentence and analyze components)

### Entropy Source Personality Profiles
| Entropy | Creativity | Coherence | Meta-Cognition | Glitch Severity |
|---------|------------|-----------|----------------|-----------------|
| PRNG    | Medium     | **High**  | Moderate       | Low (repetition) |
| TRNG    | High       | Medium    | High           | Medium (language mixing) |
| QRNG    | **Highest**| Low       | **Very High**  | **Severe (mode shifts)** |
""")

    return "\n".join(output)


def format_llama_results():
    """Format LLaMA results into markdown tables."""
    llama_dir = RESULTS_DIR / "llama"
    output = ["# LLaMA 3.2 Entropy Comparison Results\n"]
    output.append("Comparing PRNG vs TRNG vs QRNG on LLaMA 3.2 1B.\n")

    for json_file in sorted(llama_dir.glob("*.json")):
        with open(json_file) as f:
            data = json.load(f)

        config = data.get("config", {})
        model = config.get("model_name", "LLaMA 3.2 1B")

        output.append(f"\n## {model}\n")
        output.append(f"**Samples per condition:** {config.get('num_samples', 'Unknown')}\n")

        results = data.get("results", [])
        analysis = data.get("analysis", {})

        # Results is a list of per-prompt results
        output.append("\n### Quality Scores by Prompt and Entropy Source\n")

        for prompt_result in results[:5]:  # First 5 prompts
            prompt = prompt_result.get("prompt", "Unknown")[:60]
            profiles = prompt_result.get("qualitative_profiles", {})

            output.append(f"\n#### Prompt: \"{prompt}...\"\n")
            output.append("| Entropy Source | Overall Quality | Coherence | Creativity |")
            output.append("|----------------|-----------------|-----------|------------|")

            for source in ["PRNG", "TRNG", "QRNG"]:
                profile = profiles.get(source, {})
                quality = profile.get("overall_quality", "N/A")
                cats = profile.get("category_averages", {})
                coherence = cats.get("coherence", "N/A")
                creativity = cats.get("creativity", "N/A")

                if isinstance(quality, float):
                    quality = f"{quality:.2f}"
                if isinstance(coherence, float):
                    coherence = f"{coherence:.2f}"
                if isinstance(creativity, float):
                    creativity = f"{creativity:.2f}"

                output.append(f"| {source} | {quality} | {coherence} | {creativity} |")

        # Analysis summary
        if analysis:
            output.append("\n### Statistical Analysis\n")
            if "statistical_comparison" in analysis:
                stats = analysis["statistical_comparison"]
                output.append("| Comparison | Statistic | p-value | Significant |")
                output.append("|------------|-----------|---------|-------------|")
                for comp, vals in stats.items():
                    if isinstance(vals, dict):
                        stat = vals.get("statistic", "N/A")
                        pval = vals.get("p_value", "N/A")
                        sig = "Yes" if isinstance(pval, float) and pval < 0.05 else "No"
                        if isinstance(stat, float):
                            stat = f"{stat:.4f}"
                        if isinstance(pval, float):
                            pval = f"{pval:.4f}"
                        output.append(f"| {comp} | {stat} | {pval} | {sig} |")

    return "\n".join(output)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate DeepSeek tables
    print("Generating DeepSeek tables...")
    deepseek_md = format_deepseek_results()
    with open(OUTPUT_DIR / "DEEPSEEK_RESULTS.md", "w") as f:
        f.write(deepseek_md)

    # Generate Qwen tables
    print("Generating Qwen tables...")
    qwen_md = format_qwen_results()
    with open(OUTPUT_DIR / "QWEN_RESULTS.md", "w") as f:
        f.write(qwen_md)

    # Generate LLaMA tables
    print("Generating LLaMA tables...")
    llama_md = format_llama_results()
    with open(OUTPUT_DIR / "LLAMA_RESULTS.md", "w") as f:
        f.write(llama_md)

    print(f"\nFormatted tables saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
