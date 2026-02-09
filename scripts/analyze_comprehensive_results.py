#!/usr/bin/env python3
"""
Deep statistical analysis of entropy-seeding comprehensive experiment results.

Computes cross-prompt aggregates, deltas, statistical significance tests,
multi-turn evolution analysis, inter-sample variance, and cross-model comparisons.

Usage:
    python analyze_comprehensive_results.py FILE1 [FILE2 ...] [-o OUTPUT_PATH]

Examples:
    # Two-model cross comparison (default output path):
    python analyze_comprehensive_results.py \
        results/valid_entropy_comparisons/qwen/comprehensive_qwen3_4b_*.json \
        results/valid_entropy_comparisons/qwen/comprehensive_qwen3_1.7b_*.json

    # Single model analysis with custom output:
    python analyze_comprehensive_results.py data.json -o results/analysis.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

METRICS = ["shannon_char", "shannon_word", "word_diversity", "length_words"]
SOURCES = ["PRNG", "TRNG", "QRNG"]
BASELINE = "PRNG"


# ---------------------------------------------------------------------------
# Data extraction helpers
# ---------------------------------------------------------------------------


def load_experiment(path: str | Path) -> dict[str, Any]:
    """Load a single experiment JSON file."""
    with open(path, "r") as fh:
        return json.load(fh)


def extract_single_turn_samples(
    data: dict[str, Any],
) -> dict[str, dict[str, list[dict[str, float]]]]:
    """Return {source: {prompt: [metric_dicts]}} from single_turn data."""
    result: dict[str, dict[str, list[dict[str, float]]]] = {
        s: {} for s in SOURCES
    }
    for prompt, source_data in data["single_turn"].items():
        for source in SOURCES:
            if source not in source_data:
                continue
            metrics_list = [
                sample["metrics"]
                for sample in source_data[source]["samples"]
                if sample.get("metrics") is not None
            ]
            if metrics_list:
                result[source][prompt] = metrics_list
    return result


def extract_multi_turn_samples(
    data: dict[str, Any],
) -> dict[str, dict[str, list[list[dict[str, float]]]]]:
    """Return {source: {conv: [[turn_metrics_per_turn] per sample]}}."""
    result: dict[str, dict[str, list[list[dict[str, float]]]]] = {
        s: {} for s in SOURCES
    }
    for conv_name, source_data in data.get("multi_turn", {}).items():
        for source in SOURCES:
            if source not in source_data:
                continue
            per_sample: list[list[dict[str, float]]] = []
            for item in source_data[source]:
                turn_metrics = [
                    turn["metrics"]
                    for turn in item["turns"]
                    if turn.get("metrics") is not None
                ]
                if turn_metrics:
                    per_sample.append(turn_metrics)
            if per_sample:
                result[source][conv_name] = per_sample
    return result


# ---------------------------------------------------------------------------
# Core statistical computations
# ---------------------------------------------------------------------------


def compute_per_prompt_means(
    samples: dict[str, dict[str, list[dict[str, float]]]],
) -> dict[str, dict[str, dict[str, float]]]:
    """Compute mean of each metric per (source, prompt).

    Returns {source: {prompt: {metric: mean_value}}}.
    """
    out: dict[str, dict[str, dict[str, float]]] = {}
    for source in SOURCES:
        out[source] = {}
        for prompt, metric_list in samples[source].items():
            means: dict[str, float] = {}
            for m in METRICS:
                vals = [s[m] for s in metric_list]
                means[m] = float(np.mean(vals))
            out[source][prompt] = means
    return out


def aggregate_stats(
    per_prompt_means: dict[str, dict[str, dict[str, float]]],
) -> dict[str, dict[str, dict[str, float]]]:
    """Cross-prompt aggregate (mean, std, cv) for each source.

    Returns {source: {metric: {mean, std, cv}}}.
    """
    out: dict[str, dict[str, dict[str, float]]] = {}
    for source in SOURCES:
        out[source] = {}
        for m in METRICS:
            vals = [
                per_prompt_means[source][p][m]
                for p in per_prompt_means[source]
            ]
            arr = np.array(vals)
            mean_val = float(np.mean(arr))
            std_val = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
            cv_val = std_val / mean_val if mean_val != 0 else 0.0
            out[source][m] = {
                "mean": round(mean_val, 6),
                "std": round(std_val, 6),
                "cv": round(cv_val, 6),
            }
    return out


def compute_deltas(
    agg: dict[str, dict[str, dict[str, float]]],
) -> dict[str, dict[str, float]]:
    """Percent change of TRNG and QRNG vs PRNG baseline.

    Returns {comparison_label: {metric: pct_change}}.
    """
    out: dict[str, dict[str, float]] = {}
    for alt in ("TRNG", "QRNG"):
        label = f"{alt}_vs_{BASELINE}"
        out[label] = {}
        for m in METRICS:
            base = agg[BASELINE][m]["mean"]
            alt_val = agg[alt][m]["mean"]
            pct = ((alt_val - base) / base * 100) if base != 0 else 0.0
            out[label][m] = round(pct, 4)
    return out


def run_statistical_tests(
    per_prompt_means: dict[str, dict[str, dict[str, float]]],
) -> dict[str, dict[str, dict[str, Any]]]:
    """Paired tests (t-test and Wilcoxon) on per-prompt means: alt vs PRNG.

    Returns {comparison: {metric: {t_stat, t_pvalue, w_stat, w_pvalue, n,
                                    significant_t, significant_w}}}.
    """
    prompts = sorted(per_prompt_means[BASELINE].keys())
    out: dict[str, dict[str, dict[str, Any]]] = {}

    for alt in ("TRNG", "QRNG"):
        label = f"{alt}_vs_{BASELINE}"
        out[label] = {}
        for m in METRICS:
            base_vals = np.array(
                [per_prompt_means[BASELINE][p][m] for p in prompts]
            )
            alt_vals = np.array(
                [per_prompt_means[alt][p][m] for p in prompts]
            )

            n = len(base_vals)

            # Paired t-test
            t_stat, t_p = stats.ttest_rel(alt_vals, base_vals)

            # Wilcoxon signed-rank (non-parametric alternative)
            diffs = alt_vals - base_vals
            # Wilcoxon requires at least one non-zero difference
            if np.all(diffs == 0):
                w_stat, w_p = float("nan"), 1.0
            else:
                try:
                    w_stat, w_p = stats.wilcoxon(diffs)
                except ValueError:
                    # Too few samples for Wilcoxon
                    w_stat, w_p = float("nan"), float("nan")

            out[label][m] = {
                "n_prompts": n,
                "paired_t_stat": round(float(t_stat), 6),
                "paired_t_pvalue": round(float(t_p), 6),
                "wilcoxon_stat": (
                    round(float(w_stat), 6)
                    if not math.isnan(w_stat)
                    else None
                ),
                "wilcoxon_pvalue": (
                    round(float(w_p), 6) if not math.isnan(w_p) else None
                ),
                "significant_t_005": float(t_p) < 0.05,
                "significant_w_005": (
                    float(w_p) < 0.05 if not math.isnan(w_p) else False
                ),
            }
    return out


# ---------------------------------------------------------------------------
# Multi-turn analysis
# ---------------------------------------------------------------------------


def analyze_multi_turn_evolution(
    mt_samples: dict[str, dict[str, list[list[dict[str, float]]]]],
) -> dict[str, dict[str, dict[str, Any]]]:
    """Analyze metric evolution across turns for each (source, conversation).

    For each metric, fits a simple linear trend across turns (averaged over
    samples) and reports slope, direction, and per-turn means.

    Returns {conv: {source: {metric: {per_turn_means, slope, direction}}}}.
    """
    out: dict[str, dict[str, dict[str, Any]]] = {}
    for source in SOURCES:
        for conv_name, sample_list in mt_samples[source].items():
            if conv_name not in out:
                out[conv_name] = {}
            if source not in out[conv_name]:
                out[conv_name][source] = {}

            if not sample_list:
                continue

            n_turns = len(sample_list[0])
            for m in METRICS:
                per_turn_means: list[float] = []
                for t_idx in range(n_turns):
                    vals = [s[t_idx][m] for s in sample_list]
                    per_turn_means.append(float(np.mean(vals)))

                # Linear regression for trend
                x = np.arange(n_turns)
                if n_turns >= 2:
                    slope, intercept, r_value, p_value, std_err = (
                        stats.linregress(x, per_turn_means)
                    )
                    direction = (
                        "increasing"
                        if slope > 0.001
                        else ("decreasing" if slope < -0.001 else "stable")
                    )
                else:
                    slope = 0.0
                    r_value = 0.0
                    p_value = 1.0
                    direction = "stable"

                out[conv_name][source][m] = {
                    "per_turn_means": [round(v, 6) for v in per_turn_means],
                    "slope": round(float(slope), 6),
                    "r_squared": round(float(r_value**2), 6),
                    "trend_pvalue": round(float(p_value), 6),
                    "direction": direction,
                }
    return out


# ---------------------------------------------------------------------------
# Inter-sample variance
# ---------------------------------------------------------------------------


def compute_inter_sample_variance(
    samples: dict[str, dict[str, list[dict[str, float]]]],
) -> dict[str, dict[str, dict[str, float]]]:
    """Measure how much samples vary within the same source.

    For each (source, metric) computes mean intra-prompt std and CV across
    all prompts.

    Returns {source: {metric: {mean_intra_std, mean_intra_cv,
                                overall_mean, overall_std}}}.
    """
    out: dict[str, dict[str, dict[str, float]]] = {}
    for source in SOURCES:
        out[source] = {}
        for m in METRICS:
            intra_stds: list[float] = []
            intra_cvs: list[float] = []
            all_vals: list[float] = []

            for prompt, metric_list in samples[source].items():
                vals = [s[m] for s in metric_list]
                all_vals.extend(vals)
                arr = np.array(vals)
                std = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
                mean = float(np.mean(arr))
                cv = std / mean if mean != 0 else 0.0
                intra_stds.append(std)
                intra_cvs.append(cv)

            all_arr = np.array(all_vals)
            out[source][m] = {
                "mean_intra_prompt_std": round(float(np.mean(intra_stds)), 6),
                "mean_intra_prompt_cv": round(float(np.mean(intra_cvs)), 6),
                "overall_mean": round(float(np.mean(all_arr)), 6),
                "overall_std": round(
                    float(np.std(all_arr, ddof=1)) if len(all_arr) > 1 else 0.0,
                    6,
                ),
            }
    return out


# ---------------------------------------------------------------------------
# Cross-model comparison
# ---------------------------------------------------------------------------


def cross_model_sensitivity(
    model_results: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Compare sensitivity to entropy source across models.

    For each model, computes the absolute delta (TRNG/QRNG vs PRNG) across
    metrics and reports which model is more sensitive.

    Returns structured comparison dict.
    """
    models = sorted(model_results.keys())
    if len(models) < 2:
        return {"note": "Need at least 2 models for cross-model comparison"}

    comparison: dict[str, Any] = {"models": models, "comparisons": {}}

    for alt in ("TRNG", "QRNG"):
        label = f"{alt}_vs_{BASELINE}"
        comparison["comparisons"][label] = {}
        for m in METRICS:
            per_model: dict[str, float] = {}
            for model in models:
                deltas = model_results[model].get("deltas", {})
                if label in deltas and m in deltas[label]:
                    per_model[model] = deltas[label][m]
            comparison["comparisons"][label][m] = {
                "deltas_pct": per_model,
                "most_sensitive": (
                    max(per_model, key=lambda k: abs(per_model[k]))
                    if per_model
                    else None
                ),
                "least_sensitive": (
                    min(per_model, key=lambda k: abs(per_model[k]))
                    if per_model
                    else None
                ),
            }

    # Aggregate sensitivity score: mean absolute delta across all metrics
    comparison["sensitivity_scores"] = {}
    for model in models:
        scores: list[float] = []
        for alt in ("TRNG", "QRNG"):
            label = f"{alt}_vs_{BASELINE}"
            deltas = model_results[model].get("deltas", {})
            if label in deltas:
                for m in METRICS:
                    if m in deltas[label]:
                        scores.append(abs(deltas[label][m]))
        comparison["sensitivity_scores"][model] = round(
            float(np.mean(scores)) if scores else 0.0, 4
        )

    # Statistical test: is there a significant model-size effect?
    # Compare per-prompt means between models for each source
    comparison["model_effect_tests"] = {}
    for source in SOURCES:
        for m in METRICS:
            vals_by_model: dict[str, list[float]] = {}
            for model in models:
                ppm = model_results[model].get("per_prompt_means", {})
                if source in ppm:
                    vals_by_model[model] = [
                        ppm[source][p][m] for p in sorted(ppm[source].keys())
                    ]

            if len(vals_by_model) == 2:
                keys = sorted(vals_by_model.keys())
                a = np.array(vals_by_model[keys[0]])
                b = np.array(vals_by_model[keys[1]])
                # Independent t-test (prompts are paired but models are not)
                t_stat, t_p = stats.ttest_ind(a, b, equal_var=False)
                # Mann-Whitney U
                try:
                    u_stat, u_p = stats.mannwhitneyu(
                        a, b, alternative="two-sided"
                    )
                except ValueError:
                    u_stat, u_p = float("nan"), float("nan")

                key = f"{source}_{m}"
                comparison["model_effect_tests"][key] = {
                    "models": keys,
                    "means": {
                        keys[0]: round(float(np.mean(a)), 6),
                        keys[1]: round(float(np.mean(b)), 6),
                    },
                    "welch_t_stat": round(float(t_stat), 6),
                    "welch_t_pvalue": round(float(t_p), 6),
                    "mannwhitney_u": (
                        round(float(u_stat), 6)
                        if not math.isnan(u_stat)
                        else None
                    ),
                    "mannwhitney_pvalue": (
                        round(float(u_p), 6)
                        if not math.isnan(u_p)
                        else None
                    ),
                    "significant_005": float(t_p) < 0.05,
                }

    return comparison


# ---------------------------------------------------------------------------
# Summary printing
# ---------------------------------------------------------------------------


def print_summary(
    model_results: dict[str, dict[str, Any]],
    cross_model: dict[str, Any] | None,
) -> None:
    """Print formatted summary tables to stdout."""
    sep = "=" * 90

    print(f"\n{sep}")
    print("  ENTROPY SOURCE COMPREHENSIVE STATISTICAL ANALYSIS")
    print(sep)

    for model, res in sorted(model_results.items()):
        print(f"\n{'─' * 90}")
        print(f"  MODEL: {model}")
        print(f"{'─' * 90}")

        # --- Aggregate stats table ---
        print(f"\n  {'Cross-Prompt Aggregate Statistics':^86}")
        header = f"  {'Source':<8}"
        for m in METRICS:
            header += f"  {m:<20}"
        print(header)
        print(f"  {'─' * 86}")

        agg = res["aggregate_stats"]
        for source in SOURCES:
            row = f"  {source:<8}"
            for m in METRICS:
                s = agg[source][m]
                cell = f"{s['mean']:.4f} +/- {s['std']:.4f}"
                row += f"  {cell:<20}"
            print(row)

        # CV row
        print(f"\n  {'Coefficient of Variation (CV)':^86}")
        for source in SOURCES:
            row = f"  {source:<8}"
            for m in METRICS:
                row += f"  {agg[source][m]['cv']:.4f}{'':<15}"
            print(row)

        # --- Deltas table ---
        print(f"\n  {'Percent Change vs PRNG':^86}")
        header = f"  {'Comparison':<18}"
        for m in METRICS:
            header += f"  {m:<18}"
        print(header)
        print(f"  {'─' * 86}")

        deltas = res["deltas"]
        for label, mvals in deltas.items():
            row = f"  {label:<18}"
            for m in METRICS:
                val = mvals[m]
                sign = "+" if val > 0 else ""
                row += f"  {sign}{val:.3f}%{'':<11}"
            print(row)

        # --- Statistical tests ---
        print(f"\n  {'Statistical Tests (paired, n={})':^86}".format(
            list(res["stat_tests"].values())[0][METRICS[0]]["n_prompts"]
            if res["stat_tests"]
            else "?"
        ))
        header = f"  {'Comparison':<18}  {'Metric':<16}  {'t-stat':>8}  {'t-p':>8}  {'W-stat':>8}  {'W-p':>8}  {'Sig?':>6}"
        print(header)
        print(f"  {'─' * 86}")

        for label, metric_tests in res["stat_tests"].items():
            for m in METRICS:
                t = metric_tests[m]
                w_stat_str = (
                    f"{t['wilcoxon_stat']:.4f}"
                    if t["wilcoxon_stat"] is not None
                    else "N/A"
                )
                w_p_str = (
                    f"{t['wilcoxon_pvalue']:.4f}"
                    if t["wilcoxon_pvalue"] is not None
                    else "N/A"
                )
                sig = "YES" if t["significant_t_005"] else "no"
                row = (
                    f"  {label:<18}  {m:<16}  "
                    f"{t['paired_t_stat']:>8.4f}  {t['paired_t_pvalue']:>8.4f}  "
                    f"{w_stat_str:>8}  {w_p_str:>8}  {sig:>6}"
                )
                print(row)

        # --- Inter-sample variance ---
        print(f"\n  {'Inter-Sample Variance (within-source variability)':^86}")
        header = f"  {'Source':<8}  {'Metric':<16}  {'IntraStd':>10}  {'IntraCV':>10}  {'OverallMean':>12}  {'OverallStd':>12}"
        print(header)
        print(f"  {'─' * 86}")

        isv = res["inter_sample_variance"]
        for source in SOURCES:
            for m in METRICS:
                v = isv[source][m]
                row = (
                    f"  {source:<8}  {m:<16}  "
                    f"{v['mean_intra_prompt_std']:>10.4f}  "
                    f"{v['mean_intra_prompt_cv']:>10.4f}  "
                    f"{v['overall_mean']:>12.4f}  "
                    f"{v['overall_std']:>12.4f}"
                )
                print(row)

        # --- Multi-turn evolution ---
        mt = res.get("multi_turn_evolution", {})
        if mt:
            print(f"\n  {'Multi-Turn Metric Evolution':^86}")
            for conv_name, source_data in sorted(mt.items()):
                print(f"\n  Conversation: {conv_name}")
                header = f"    {'Source':<8}  {'Metric':<16}  {'Turns':>30}  {'Slope':>8}  {'Dir':>12}"
                print(header)
                print(f"    {'─' * 80}")
                for source in SOURCES:
                    if source not in source_data:
                        continue
                    for m in METRICS:
                        if m not in source_data[source]:
                            continue
                        info = source_data[source][m]
                        turns_str = " -> ".join(
                            f"{v:.3f}" for v in info["per_turn_means"]
                        )
                        row = (
                            f"    {source:<8}  {m:<16}  "
                            f"{turns_str:>30}  "
                            f"{info['slope']:>8.4f}  "
                            f"{info['direction']:>12}"
                        )
                        print(row)

    # --- Cross-model comparison ---
    if cross_model and len(cross_model.get("models", [])) >= 2:
        print(f"\n{sep}")
        print("  CROSS-MODEL COMPARISON")
        print(sep)

        print(f"\n  Models: {', '.join(cross_model['models'])}")

        # Sensitivity scores
        print(f"\n  {'Sensitivity Scores (mean |delta| across all metrics)':^86}")
        for model, score in sorted(
            cross_model["sensitivity_scores"].items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            bar = "#" * int(score * 10)
            print(f"    {model:<25} {score:>8.4f}  {bar}")

        # Per-metric sensitivity
        print(f"\n  {'Per-Metric Sensitivity (% change vs PRNG)':^86}")
        for label, metric_data in cross_model["comparisons"].items():
            print(f"\n  {label}:")
            header = f"    {'Metric':<18}  {'Model Deltas':<40}  {'Most Sensitive':>20}"
            print(header)
            print(f"    {'─' * 80}")
            for m in METRICS:
                info = metric_data[m]
                deltas_str = "  ".join(
                    f"{k}: {v:+.3f}%"
                    for k, v in sorted(info["deltas_pct"].items())
                )
                row = (
                    f"    {m:<18}  {deltas_str:<40}  "
                    f"{info['most_sensitive'] or 'N/A':>20}"
                )
                print(row)

        # Model effect tests
        tests = cross_model.get("model_effect_tests", {})
        if tests:
            print(f"\n  {'Model Size Effect Tests (Welch t-test)':^86}")
            header = f"    {'Source+Metric':<30}  {'Mean A':>10}  {'Mean B':>10}  {'t-stat':>8}  {'p-value':>8}  {'Sig?':>6}"
            print(header)
            print(f"    {'─' * 80}")
            for key, t in sorted(tests.items()):
                models_list = t["models"]
                sig = "YES" if t["significant_005"] else "no"
                row = (
                    f"    {key:<30}  "
                    f"{t['means'][models_list[0]]:>10.4f}  "
                    f"{t['means'][models_list[1]]:>10.4f}  "
                    f"{t['welch_t_stat']:>8.4f}  "
                    f"{t['welch_t_pvalue']:>8.4f}  "
                    f"{sig:>6}"
                )
                print(row)

    print(f"\n{sep}")
    print("  END OF ANALYSIS")
    print(f"{sep}\n")


# ---------------------------------------------------------------------------
# Analyze one model
# ---------------------------------------------------------------------------


def analyze_model(data: dict[str, Any]) -> dict[str, Any]:
    """Run full analysis pipeline on a single model experiment."""
    model_name = data["model"]

    # Extract samples
    st_samples = extract_single_turn_samples(data)
    mt_samples = extract_multi_turn_samples(data)

    # Per-prompt means
    ppm = compute_per_prompt_means(st_samples)

    # Aggregate stats
    agg = aggregate_stats(ppm)

    # Deltas
    deltas = compute_deltas(agg)

    # Statistical tests
    stat_tests = run_statistical_tests(ppm)

    # Multi-turn evolution
    mt_evolution = analyze_multi_turn_evolution(mt_samples)

    # Inter-sample variance
    isv = compute_inter_sample_variance(st_samples)

    return {
        "model": model_name,
        "num_prompts": len(data["single_turn"]),
        "num_samples_per_prompt": data["num_samples"],
        "num_conversations": len(data.get("multi_turn", {})),
        "aggregate_stats": agg,
        "deltas": deltas,
        "stat_tests": stat_tests,
        "multi_turn_evolution": mt_evolution,
        "inter_sample_variance": isv,
        "per_prompt_means": {
            source: {
                prompt: {m: round(v, 6) for m, v in means.items()}
                for prompt, means in ppm[source].items()
            }
            for source, prompts in ppm.items()
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Deep statistical analysis of entropy-seeding experiment results."
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="One or more comprehensive experiment JSON files.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help=(
            "Output JSON path. Defaults to "
            "results/valid_entropy_comparisons/analysis_<models>.json"
        ),
    )
    args = parser.parse_args()

    # Load and analyze each model
    model_results: dict[str, dict[str, Any]] = {}
    for fpath in args.files:
        data = load_experiment(fpath)
        model_name = data["model"]
        result = analyze_model(data)
        model_results[model_name] = result
        print(f"Analyzed: {model_name} ({fpath})")

    # Cross-model comparison (if >=2 models)
    cross_model = None
    if len(model_results) >= 2:
        cross_model = cross_model_sensitivity(model_results)

    # Assemble output
    output = {
        "analysis_type": "comprehensive_entropy_source_comparison",
        "models_analyzed": sorted(model_results.keys()),
        "metrics": METRICS,
        "sources": SOURCES,
        "baseline": BASELINE,
        "per_model": {},
        "cross_model_comparison": cross_model,
    }

    for model_name, res in model_results.items():
        # Strip per_prompt_means from output JSON to keep it manageable
        # (still used internally for cross-model tests)
        res_copy = {k: v for k, v in res.items() if k != "per_prompt_means"}
        output["per_model"][model_name] = res_copy

    # Determine output path
    if args.output:
        out_path = Path(args.output)
    else:
        model_tag = "_".join(
            m.replace(":", "-") for m in sorted(model_results.keys())
        )
        out_path = Path(args.files[0]).parent / f"analysis_{model_tag}.json"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as fh:
        json.dump(output, fh, indent=2)
    print(f"\nResults written to: {out_path}")

    # Print summary
    print_summary(model_results, cross_model)


if __name__ == "__main__":
    main()
