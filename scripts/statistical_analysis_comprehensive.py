"""
Statistical analysis of comprehensive entropy seeding experiments.

Computes per-model:
  1. Per-metric means across all prompts for each source (PRNG, TRNG, QRNG)
  2. Wilcoxon signed-rank tests: TRNG vs PRNG, QRNG vs PRNG (paired by prompt)
  3. Paired t-tests: same comparisons
  4. Cohen's d effect sizes
  5. Cross-source coefficient of variation (CV%) per prompt
  6. Overall mean CV across prompts
  7. Multi-turn vs single-turn diversity comparison

Cross-model comparison:
  - Which model shows higher entropy sensitivity to source
  - Mean effect sizes compared
"""

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = Path("/Users/bobbyprice/projects/entropy/entropy-seeding")
RESULT_DIR = BASE_DIR / "results" / "valid_entropy_comparisons"

FILES = {
    "qwen3_8b": RESULT_DIR / "qwen" / "comprehensive_qwen3_8b_20260209_053534.json",
    "mistral": RESULT_DIR / "mistral" / "comprehensive_mistral_latest_20260209_063602.json",
}

OUTPUT_FILES = {
    "qwen3_8b": RESULT_DIR / "statistical_tests_qwen3_8b_comprehensive.json",
    "mistral": RESULT_DIR / "statistical_tests_mistral_comprehensive.json",
}

METRICS = ["shannon_char", "shannon_word", "word_diversity", "length_words"]
SOURCES = ["PRNG", "TRNG", "QRNG"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def safe_float(v: Any) -> float:
    """Convert to float, handling None/NaN."""
    if v is None:
        return float("nan")
    return float(v)


def cohens_d(x: np.ndarray, y: np.ndarray) -> float:
    """
    Compute Cohen's d for paired samples.
    d = mean(x - y) / std(x - y, ddof=1)
    """
    diff = x - y
    sd = np.std(diff, ddof=1)
    if sd == 0:
        return 0.0
    return float(np.mean(diff) / sd)


def cohens_d_independent(x: np.ndarray, y: np.ndarray) -> float:
    """
    Cohen's d for independent samples using pooled SD.
    """
    nx, ny = len(x), len(y)
    var_x, var_y = np.var(x, ddof=1), np.var(y, ddof=1)
    pooled_sd = np.sqrt(((nx - 1) * var_x + (ny - 1) * var_y) / (nx + ny - 2))
    if pooled_sd == 0:
        return 0.0
    return float((np.mean(x) - np.mean(y)) / pooled_sd)


def cv_percent(values: np.ndarray) -> float:
    """Coefficient of variation as a percentage."""
    mean = np.mean(values)
    if mean == 0:
        return 0.0
    return float(np.std(values, ddof=1) / abs(mean) * 100)


def interpret_effect_size(d: float) -> str:
    """Interpret Cohen's d magnitude."""
    d_abs = abs(d)
    if d_abs < 0.2:
        return "negligible"
    elif d_abs < 0.5:
        return "small"
    elif d_abs < 0.8:
        return "medium"
    else:
        return "large"


# ---------------------------------------------------------------------------
# Data extraction
# ---------------------------------------------------------------------------
def extract_single_turn_prompt_means(data: dict) -> dict[str, dict[str, dict[str, float]]]:
    """
    For each prompt, compute the mean of each metric across the 5 samples
    for each source. Returns: {prompt: {source: {metric: mean_value}}}.
    """
    result = {}
    st = data.get("single_turn", {})
    for prompt, sources in st.items():
        result[prompt] = {}
        for source in SOURCES:
            if source not in sources:
                continue
            samples = sources[source].get("samples", [])
            metric_vals = {m: [] for m in METRICS}
            for sample in samples:
                m = sample.get("metrics")
                if m is None:
                    continue
                for metric in METRICS:
                    v = m.get(metric)
                    if v is not None:
                        metric_vals[metric].append(safe_float(v))
            result[prompt][source] = {
                metric: float(np.mean(vals)) if vals else float("nan")
                for metric, vals in metric_vals.items()
            }
    return result


def extract_paired_vectors(prompt_means: dict) -> dict[str, dict[str, np.ndarray]]:
    """
    Create paired vectors across prompts: for each metric, one value per prompt.
    Returns: {metric: {source: np.array of length n_prompts}}.
    """
    prompts = list(prompt_means.keys())
    result = {}
    for metric in METRICS:
        result[metric] = {}
        for source in SOURCES:
            vals = []
            for prompt in prompts:
                if source in prompt_means[prompt]:
                    vals.append(prompt_means[prompt][source][metric])
                else:
                    vals.append(float("nan"))
            result[metric][source] = np.array(vals)
    return result


def extract_multi_turn_metrics(data: dict) -> dict[str, dict[str, list[dict[str, float]]]]:
    """
    Extract multi-turn metrics. For each multi-turn prompt and source,
    collect metrics from each turn of each sample.
    Returns: {prompt_name: {source: [list of turn-level metric dicts]}}.
    """
    result = {}
    mt = data.get("multi_turn", {})
    for prompt_name, sources in mt.items():
        result[prompt_name] = {}
        for source in SOURCES:
            if source not in sources:
                continue
            samples = sources[source]  # This is a list
            all_turn_metrics = []
            for sample in samples:
                turns = sample.get("turns", [])
                for turn in turns:
                    m = turn.get("metrics", {})
                    all_turn_metrics.append({
                        metric: safe_float(m.get(metric, float("nan")))
                        for metric in METRICS
                    })
            result[prompt_name][source] = all_turn_metrics
    return result


def compute_multi_turn_means(mt_metrics: dict) -> dict[str, dict[str, dict[str, float]]]:
    """Compute means across all turns and samples for multi-turn data."""
    result = {}
    for prompt_name, sources in mt_metrics.items():
        result[prompt_name] = {}
        for source, turn_list in sources.items():
            metric_means = {}
            for metric in METRICS:
                vals = [t[metric] for t in turn_list if not np.isnan(t[metric])]
                metric_means[metric] = float(np.mean(vals)) if vals else float("nan")
            result[prompt_name][source] = metric_means
    return result


def compute_single_turn_all_samples(data: dict) -> dict[str, dict[str, list[float]]]:
    """
    Collect all individual sample values for each source across ALL single-turn prompts.
    Returns: {metric: {source: [all sample values]}}.
    """
    result = {m: {s: [] for s in SOURCES} for m in METRICS}
    st = data.get("single_turn", {})
    for prompt, sources in st.items():
        for source in SOURCES:
            if source not in sources:
                continue
            samples = sources[source].get("samples", [])
            for sample in samples:
                m = sample.get("metrics")
                if m is None:
                    continue
                for metric in METRICS:
                    v = m.get(metric)
                    if v is not None:
                        result[metric][source].append(safe_float(v))
    return result


# ---------------------------------------------------------------------------
# Statistical tests
# ---------------------------------------------------------------------------
def run_paired_tests(
    paired_vectors: dict[str, dict[str, np.ndarray]],
) -> dict[str, dict[str, dict]]:
    """
    Run Wilcoxon signed-rank and paired t-tests for TRNG vs PRNG and QRNG vs PRNG.
    """
    comparisons = [("TRNG", "PRNG"), ("QRNG", "PRNG")]
    results = {}

    for metric in METRICS:
        results[metric] = {}
        for alt_source, base_source in comparisons:
            key = f"{alt_source}_vs_{base_source}"
            x = paired_vectors[metric][alt_source]
            y = paired_vectors[metric][base_source]

            # Remove NaN pairs
            valid = ~(np.isnan(x) | np.isnan(y))
            x_clean = x[valid]
            y_clean = y[valid]
            n = len(x_clean)

            if n < 3:
                results[metric][key] = {
                    "n_pairs": n,
                    "error": "insufficient data for tests",
                }
                continue

            # Means
            mean_alt = float(np.mean(x_clean))
            mean_base = float(np.mean(y_clean))
            mean_diff = float(np.mean(x_clean - y_clean))
            pct_diff = (mean_diff / abs(mean_base) * 100) if mean_base != 0 else 0.0

            # Wilcoxon signed-rank test
            try:
                w_stat, w_pval = stats.wilcoxon(x_clean, y_clean, alternative="two-sided")
                wilcoxon_result = {
                    "statistic": float(w_stat),
                    "p_value": float(w_pval),
                    "significant_005": bool(w_pval < 0.05),
                    "significant_001": bool(w_pval < 0.01),
                }
            except Exception as e:
                wilcoxon_result = {"error": str(e)}

            # Paired t-test
            try:
                t_stat, t_pval = stats.ttest_rel(x_clean, y_clean)
                ttest_result = {
                    "statistic": float(t_stat),
                    "p_value": float(t_pval),
                    "significant_005": bool(t_pval < 0.05),
                    "significant_001": bool(t_pval < 0.01),
                }
            except Exception as e:
                ttest_result = {"error": str(e)}

            # Cohen's d (paired)
            d = cohens_d(x_clean, y_clean)

            results[metric][key] = {
                "n_pairs": n,
                "mean_alt_source": round(mean_alt, 6),
                "mean_base_source": round(mean_base, 6),
                "mean_difference": round(mean_diff, 6),
                "percent_difference": round(pct_diff, 4),
                "wilcoxon_signed_rank": wilcoxon_result,
                "paired_ttest": ttest_result,
                "cohens_d": round(d, 4),
                "effect_size_interpretation": interpret_effect_size(d),
            }

    return results


def compute_cross_source_cv(prompt_means: dict) -> dict[str, dict[str, float]]:
    """
    For each prompt and metric, compute CV% across the three sources.
    Returns: {prompt: {metric: cv_percent}}.
    """
    result = {}
    for prompt, sources in prompt_means.items():
        result[prompt] = {}
        for metric in METRICS:
            vals = []
            for source in SOURCES:
                if source in sources and not np.isnan(sources[source][metric]):
                    vals.append(sources[source][metric])
            if len(vals) >= 2:
                result[prompt][metric] = round(cv_percent(np.array(vals)), 4)
            else:
                result[prompt][metric] = float("nan")
    return result


def compute_mean_cv(cv_per_prompt: dict) -> dict[str, float]:
    """Compute overall mean CV across all prompts for each metric."""
    result = {}
    for metric in METRICS:
        vals = [
            cv_per_prompt[p][metric]
            for p in cv_per_prompt
            if not np.isnan(cv_per_prompt[p][metric])
        ]
        result[metric] = round(float(np.mean(vals)), 4) if vals else float("nan")
    return result


def compute_single_vs_multi_diversity(data: dict) -> dict:
    """
    Compare word_diversity between single-turn and multi-turn responses.
    """
    # Single-turn word_diversity per source (mean of sample means across prompts)
    st = data.get("single_turn", {})
    single_div = {s: [] for s in SOURCES}
    for prompt, sources in st.items():
        for source in SOURCES:
            if source not in sources:
                continue
            samples = sources[source].get("samples", [])
            vals = [
                safe_float(s["metrics"].get("word_diversity", float("nan")))
                for s in samples
                if "metrics" in s and s["metrics"] is not None
            ]
            if vals:
                single_div[source].append(float(np.mean(vals)))

    # Multi-turn word_diversity per source
    mt = data.get("multi_turn", {})
    multi_div = {s: [] for s in SOURCES}
    for prompt_name, sources in mt.items():
        for source in SOURCES:
            if source not in sources:
                continue
            samples = sources[source]  # list
            for sample in samples:
                turns = sample.get("turns", [])
                for turn in turns:
                    m = turn.get("metrics", {})
                    v = m.get("word_diversity")
                    if v is not None:
                        multi_div[source].append(safe_float(v))

    result = {"single_turn": {}, "multi_turn": {}, "comparison": {}}

    for source in SOURCES:
        s_vals = np.array(single_div[source]) if single_div[source] else np.array([])
        m_vals = np.array(multi_div[source]) if multi_div[source] else np.array([])

        s_mean = float(np.mean(s_vals)) if len(s_vals) > 0 else float("nan")
        m_mean = float(np.mean(m_vals)) if len(m_vals) > 0 else float("nan")

        result["single_turn"][source] = {
            "mean_word_diversity": round(s_mean, 6),
            "n": len(s_vals),
        }
        result["multi_turn"][source] = {
            "mean_word_diversity": round(m_mean, 6),
            "n": len(m_vals),
        }

        diff = m_mean - s_mean if not (np.isnan(s_mean) or np.isnan(m_mean)) else float("nan")
        pct = (diff / s_mean * 100) if s_mean != 0 and not np.isnan(diff) else float("nan")

        # Independent t-test between single and multi
        if len(s_vals) >= 2 and len(m_vals) >= 2:
            t_stat, t_pval = stats.ttest_ind(m_vals, s_vals, equal_var=False)
            d = cohens_d_independent(m_vals, s_vals)
            comparison_entry = {
                "mean_difference": round(float(diff), 6),
                "percent_difference": round(float(pct), 4),
                "ttest_ind_statistic": round(float(t_stat), 4),
                "ttest_ind_p_value": round(float(t_pval), 6),
                "significant_005": bool(t_pval < 0.05),
                "cohens_d": round(d, 4),
                "effect_size_interpretation": interpret_effect_size(d),
                "direction": "multi_turn_higher" if diff > 0 else "single_turn_higher",
            }
        else:
            comparison_entry = {"error": "insufficient data"}

        result["comparison"][source] = comparison_entry

    # Also compute ALL sources combined
    all_single = []
    for source in SOURCES:
        all_single.extend(single_div[source])
    all_multi = []
    for source in SOURCES:
        all_multi.extend(multi_div[source])

    s_all = np.array(all_single)
    m_all = np.array(all_multi)
    result["comparison"]["ALL_SOURCES_COMBINED"] = {
        "single_turn_mean": round(float(np.mean(s_all)), 6) if len(s_all) > 0 else None,
        "multi_turn_mean": round(float(np.mean(m_all)), 6) if len(m_all) > 0 else None,
        "single_turn_n": len(s_all),
        "multi_turn_n": len(m_all),
    }

    if len(s_all) >= 2 and len(m_all) >= 2:
        t_stat, t_pval = stats.ttest_ind(m_all, s_all, equal_var=False)
        d = cohens_d_independent(m_all, s_all)
        result["comparison"]["ALL_SOURCES_COMBINED"].update({
            "mean_difference": round(float(np.mean(m_all) - np.mean(s_all)), 6),
            "ttest_ind_p_value": round(float(t_pval), 6),
            "significant_005": bool(t_pval < 0.05),
            "cohens_d": round(d, 4),
            "effect_size_interpretation": interpret_effect_size(d),
        })

    return result


# ---------------------------------------------------------------------------
# Per-model analysis
# ---------------------------------------------------------------------------
def analyze_model(data: dict) -> dict:
    """Run the full analysis for a single model."""
    model_name = data.get("model", "unknown")
    print(f"\n{'='*60}")
    print(f"Analyzing: {model_name}")
    print(f"{'='*60}")

    # 1. Per-metric means across all prompts for each source
    prompt_means = extract_single_turn_prompt_means(data)
    paired_vectors = extract_paired_vectors(prompt_means)

    grand_means = {}
    for metric in METRICS:
        grand_means[metric] = {}
        for source in SOURCES:
            v = paired_vectors[metric][source]
            valid = v[~np.isnan(v)]
            grand_means[metric][source] = {
                "mean": round(float(np.mean(valid)), 6),
                "std": round(float(np.std(valid, ddof=1)), 6),
                "n_prompts": len(valid),
            }

    print("\n--- Grand Means (single-turn, averaged per prompt then across prompts) ---")
    for metric in METRICS:
        print(f"  {metric}:")
        for source in SOURCES:
            gm = grand_means[metric][source]
            print(f"    {source}: mean={gm['mean']:.6f}, std={gm['std']:.6f}, n={gm['n_prompts']}")

    # 2 & 3 & 4. Wilcoxon, paired t-test, Cohen's d
    test_results = run_paired_tests(paired_vectors)

    print("\n--- Paired Statistical Tests ---")
    for metric in METRICS:
        for key, res in test_results[metric].items():
            if "error" in res:
                print(f"  {metric} | {key}: {res['error']}")
                continue
            w = res["wilcoxon_signed_rank"]
            t = res["paired_ttest"]
            w_p = w.get("p_value", "N/A")
            t_p = t.get("p_value", "N/A")
            d = res["cohens_d"]
            interp = res["effect_size_interpretation"]
            pct = res["percent_difference"]
            print(f"  {metric} | {key}: diff={pct:+.4f}% | Wilcoxon p={w_p:.4f} | t-test p={t_p:.4f} | d={d:.4f} ({interp})")

    # 5 & 6. Cross-source CV
    cv_per_prompt = compute_cross_source_cv(prompt_means)
    mean_cv = compute_mean_cv(cv_per_prompt)

    print("\n--- Cross-Source CV% (per prompt, then mean across prompts) ---")
    for metric in METRICS:
        print(f"  {metric}: mean CV = {mean_cv[metric]:.4f}%")

    # 7. Multi-turn vs single-turn
    st_vs_mt = compute_single_vs_multi_diversity(data)

    print("\n--- Single-Turn vs Multi-Turn Word Diversity ---")
    for source in SOURCES:
        st_mean = st_vs_mt["single_turn"][source]["mean_word_diversity"]
        mt_mean = st_vs_mt["multi_turn"][source]["mean_word_diversity"]
        comp = st_vs_mt["comparison"][source]
        if "error" not in comp:
            print(f"  {source}: single={st_mean:.6f}, multi={mt_mean:.6f}, diff={comp['mean_difference']:.6f} ({comp['direction']}), p={comp['ttest_ind_p_value']:.4f}, d={comp['cohens_d']:.4f}")
        else:
            print(f"  {source}: single={st_mean:.6f}, multi={mt_mean:.6f}, {comp['error']}")

    # Also compute all single-turn sample-level stats for additional context
    all_samples = compute_single_turn_all_samples(data)
    sample_level_stats = {}
    for metric in METRICS:
        sample_level_stats[metric] = {}
        for source in SOURCES:
            vals = np.array(all_samples[metric][source])
            if len(vals) > 0:
                sample_level_stats[metric][source] = {
                    "mean": round(float(np.mean(vals)), 6),
                    "std": round(float(np.std(vals, ddof=1)), 6),
                    "median": round(float(np.median(vals)), 6),
                    "min": round(float(np.min(vals)), 6),
                    "max": round(float(np.max(vals)), 6),
                    "n_samples": len(vals),
                }

    # Assemble output
    return {
        "model": model_name,
        "analysis_type": "comprehensive_entropy_seeding_statistical_tests",
        "design": {
            "single_turn_prompts": len(prompt_means),
            "multi_turn_prompts": len(data.get("multi_turn", {})),
            "sources": SOURCES,
            "samples_per_condition": data.get("num_samples", 5),
            "metrics_analyzed": METRICS,
        },
        "grand_means_per_source": grand_means,
        "sample_level_descriptive_stats": sample_level_stats,
        "paired_tests_by_prompt_mean": test_results,
        "cross_source_cv_per_prompt": cv_per_prompt,
        "mean_cv_across_prompts": mean_cv,
        "single_turn_vs_multi_turn": st_vs_mt,
    }


# ---------------------------------------------------------------------------
# Cross-model comparison
# ---------------------------------------------------------------------------
def cross_model_comparison(results: dict[str, dict]) -> dict:
    """Compare entropy sensitivity between models."""
    print(f"\n{'='*60}")
    print("Cross-Model Comparison")
    print(f"{'='*60}")

    comparison = {}
    model_names = list(results.keys())

    # Collect effect sizes for each model
    for metric in METRICS:
        comparison[metric] = {}
        for comp_key in ["TRNG_vs_PRNG", "QRNG_vs_PRNG"]:
            comparison[metric][comp_key] = {}
            for model_key in model_names:
                tests = results[model_key].get("paired_tests_by_prompt_mean", {})
                if metric in tests and comp_key in tests[metric]:
                    d = tests[metric][comp_key].get("cohens_d", float("nan"))
                    pct = tests[metric][comp_key].get("percent_difference", float("nan"))
                    comparison[metric][comp_key][model_key] = {
                        "cohens_d": d,
                        "percent_difference": pct,
                    }

            # Determine which model is more sensitive
            ds = {
                mk: abs(comparison[metric][comp_key][mk]["cohens_d"])
                for mk in model_names
                if mk in comparison[metric][comp_key]
            }
            if ds:
                most_sensitive = max(ds, key=ds.get)
                comparison[metric][comp_key]["most_sensitive_model"] = most_sensitive
                comparison[metric][comp_key]["sensitivity_ratio"] = round(
                    max(ds.values()) / max(min(ds.values()), 1e-10), 4
                )

    # Overall sensitivity summary
    overall = {}
    for model_key in model_names:
        all_d = []
        for metric in METRICS:
            for comp_key in ["TRNG_vs_PRNG", "QRNG_vs_PRNG"]:
                tests = results[model_key].get("paired_tests_by_prompt_mean", {})
                if metric in tests and comp_key in tests[metric]:
                    d = tests[metric][comp_key].get("cohens_d", float("nan"))
                    if not np.isnan(d):
                        all_d.append(abs(d))
        overall[model_key] = {
            "mean_abs_cohens_d": round(float(np.mean(all_d)), 4) if all_d else float("nan"),
            "max_abs_cohens_d": round(float(np.max(all_d)), 4) if all_d else float("nan"),
            "n_effects": len(all_d),
        }

    # Mean CV comparison
    cv_comparison = {}
    for model_key in model_names:
        cv = results[model_key].get("mean_cv_across_prompts", {})
        cv_comparison[model_key] = cv

    # Multi-turn vs single-turn comparison across models
    mt_comparison = {}
    for model_key in model_names:
        mt_data = results[model_key].get("single_turn_vs_multi_turn", {})
        if "comparison" in mt_data and "ALL_SOURCES_COMBINED" in mt_data["comparison"]:
            mt_comparison[model_key] = mt_data["comparison"]["ALL_SOURCES_COMBINED"]

    # Determine overall winner
    if len(model_names) == 2:
        m1, m2 = model_names
        d1 = overall[m1]["mean_abs_cohens_d"]
        d2 = overall[m2]["mean_abs_cohens_d"]
        if not np.isnan(d1) and not np.isnan(d2):
            more_sensitive = m1 if d1 > d2 else m2
            less_sensitive = m2 if d1 > d2 else m1
        else:
            more_sensitive = "indeterminate"
            less_sensitive = "indeterminate"
    else:
        more_sensitive = max(overall, key=lambda k: overall[k]["mean_abs_cohens_d"])
        less_sensitive = min(overall, key=lambda k: overall[k]["mean_abs_cohens_d"])

    cross_model_result = {
        "per_metric_comparison": comparison,
        "overall_sensitivity": overall,
        "more_sensitive_model": more_sensitive,
        "less_sensitive_model": less_sensitive,
        "mean_cv_comparison": cv_comparison,
        "multi_turn_vs_single_turn_comparison": mt_comparison,
    }

    # Print summary
    print("\n--- Overall Entropy Sensitivity ---")
    for model_key in model_names:
        o = overall[model_key]
        print(f"  {model_key}: mean |d| = {o['mean_abs_cohens_d']:.4f}, max |d| = {o['max_abs_cohens_d']:.4f}")
    print(f"  More sensitive to entropy source: {more_sensitive}")

    print("\n--- Mean CV% Comparison ---")
    for model_key in model_names:
        cv = cv_comparison[model_key]
        for metric in METRICS:
            print(f"  {model_key}/{metric}: CV = {cv.get(metric, 'N/A')}%")

    print("\n--- Per-Metric Effect Sizes ---")
    for metric in METRICS:
        for comp_key in ["TRNG_vs_PRNG", "QRNG_vs_PRNG"]:
            parts = []
            for model_key in model_names:
                if model_key in comparison[metric][comp_key]:
                    d = comparison[metric][comp_key][model_key]["cohens_d"]
                    parts.append(f"{model_key}={d:.4f}")
            ms = comparison[metric][comp_key].get("most_sensitive_model", "N/A")
            print(f"  {metric} | {comp_key}: {', '.join(parts)} -> most sensitive: {ms}")

    return cross_model_result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    all_results = {}

    for model_key, filepath in FILES.items():
        print(f"\nLoading {filepath} ...")
        with open(filepath) as f:
            data = json.load(f)
        result = analyze_model(data)
        all_results[model_key] = result

    # Cross-model comparison
    cross_model = cross_model_comparison(all_results)

    # Write per-model output files
    for model_key, output_path in OUTPUT_FILES.items():
        result = all_results[model_key]
        result["cross_model_comparison"] = cross_model

        # Make output JSON-serializable (handle any NaN)
        output_str = json.dumps(result, indent=2, default=str)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(output_str)
        print(f"\nWrote: {output_path}")

    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()
