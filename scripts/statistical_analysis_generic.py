"""
Generic statistical analysis for comprehensive entropy seeding experiments.

Usage:
    python statistical_analysis_generic.py <input_json> [output_json]

Runs Wilcoxon signed-rank, paired t-test, Cohen's d, CV%, and multi-turn
comparison for any model's comprehensive experiment results.
"""

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats


METRICS = ["shannon_char", "shannon_word", "word_diversity", "length_words"]
SOURCES = ["PRNG", "TRNG", "QRNG"]
PAIRWISE_COMPARISONS = [
    ("TRNG", "PRNG"),
    ("QRNG", "PRNG"),
    ("QRNG", "TRNG"),
]


def safe_float(v: Any) -> float:
    if v is None:
        return float("nan")
    return float(v)


def cohens_d(x: np.ndarray, y: np.ndarray) -> float:
    diff = x - y
    sd = np.std(diff, ddof=1)
    if sd == 0:
        return 0.0
    return float(np.mean(diff) / sd)


def cohens_d_independent(x: np.ndarray, y: np.ndarray) -> float:
    nx, ny = len(x), len(y)
    var_x, var_y = np.var(x, ddof=1), np.var(y, ddof=1)
    pooled_sd = np.sqrt(((nx - 1) * var_x + (ny - 1) * var_y) / (nx + ny - 2))
    if pooled_sd == 0:
        return 0.0
    return float((np.mean(x) - np.mean(y)) / pooled_sd)


def cv_percent(values: np.ndarray) -> float:
    mean = np.mean(values)
    if mean == 0:
        return 0.0
    return float(np.std(values, ddof=1) / abs(mean) * 100)


def interpret_effect_size(d: float) -> str:
    d_abs = abs(d)
    if d_abs < 0.2:
        return "negligible"
    elif d_abs < 0.5:
        return "small"
    elif d_abs < 0.8:
        return "medium"
    else:
        return "large"


def extract_single_turn_prompt_means(data: dict) -> dict:
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


def extract_paired_vectors(prompt_means: dict) -> dict:
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


def run_paired_tests(paired_vectors: dict) -> dict:
    results = {}
    for metric in METRICS:
        results[metric] = {}
        for alt_source, base_source in PAIRWISE_COMPARISONS:
            key = f"{alt_source}_vs_{base_source}"
            x = paired_vectors[metric][alt_source]
            y = paired_vectors[metric][base_source]
            valid = ~(np.isnan(x) | np.isnan(y))
            x_clean = x[valid]
            y_clean = y[valid]
            n = len(x_clean)
            if n < 3:
                results[metric][key] = {"n_pairs": n, "error": "insufficient data"}
                continue
            mean_alt = float(np.mean(x_clean))
            mean_base = float(np.mean(y_clean))
            mean_diff = float(np.mean(x_clean - y_clean))
            pct_diff = (mean_diff / abs(mean_base) * 100) if mean_base != 0 else 0.0
            try:
                w_stat, w_pval = stats.wilcoxon(x_clean, y_clean, alternative="two-sided")
                wilcoxon_result = {
                    "statistic": float(w_stat), "p_value": float(w_pval),
                    "significant_005": bool(w_pval < 0.05), "significant_001": bool(w_pval < 0.01),
                }
            except Exception as e:
                wilcoxon_result = {"error": str(e)}
            try:
                t_stat, t_pval = stats.ttest_rel(x_clean, y_clean)
                ttest_result = {
                    "statistic": float(t_stat), "p_value": float(t_pval),
                    "significant_005": bool(t_pval < 0.05), "significant_001": bool(t_pval < 0.01),
                }
            except Exception as e:
                ttest_result = {"error": str(e)}
            d = cohens_d(x_clean, y_clean)
            results[metric][key] = {
                "n_pairs": n, "mean_alt_source": round(mean_alt, 6),
                "mean_base_source": round(mean_base, 6), "mean_difference": round(mean_diff, 6),
                "percent_difference": round(pct_diff, 4),
                "wilcoxon_signed_rank": wilcoxon_result, "paired_ttest": ttest_result,
                "cohens_d": round(d, 4), "effect_size_interpretation": interpret_effect_size(d),
            }
    return results


def compute_cross_source_cv(prompt_means: dict) -> dict:
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


def compute_mean_cv(cv_per_prompt: dict) -> dict:
    result = {}
    for metric in METRICS:
        vals = [cv_per_prompt[p][metric] for p in cv_per_prompt if not np.isnan(cv_per_prompt[p][metric])]
        result[metric] = round(float(np.mean(vals)), 4) if vals else float("nan")
    return result


def compute_single_turn_all_samples(data: dict) -> dict:
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


def compute_single_vs_multi_diversity(data: dict) -> dict:
    st = data.get("single_turn", {})
    single_div = {s: [] for s in SOURCES}
    for prompt, sources in st.items():
        for source in SOURCES:
            if source not in sources:
                continue
            samples = sources[source].get("samples", [])
            vals = [
                safe_float(s["metrics"].get("word_diversity", float("nan")))
                for s in samples if "metrics" in s and s["metrics"] is not None
            ]
            if vals:
                single_div[source].append(float(np.mean(vals)))

    mt = data.get("multi_turn", {})
    multi_div = {s: [] for s in SOURCES}
    for prompt_name, sources in mt.items():
        for source in SOURCES:
            if source not in sources:
                continue
            samples = sources[source]
            for sample in samples:
                turns = sample.get("turns", [])
                for turn in turns:
                    m = turn.get("metrics", {})
                    if m is None:
                        continue
                    v = m.get("word_diversity")
                    if v is not None:
                        multi_div[source].append(safe_float(v))

    result = {"single_turn": {}, "multi_turn": {}, "comparison": {}}
    for source in SOURCES:
        s_vals = np.array(single_div[source]) if single_div[source] else np.array([])
        m_vals = np.array(multi_div[source]) if multi_div[source] else np.array([])
        s_mean = float(np.mean(s_vals)) if len(s_vals) > 0 else float("nan")
        m_mean = float(np.mean(m_vals)) if len(m_vals) > 0 else float("nan")
        result["single_turn"][source] = {"mean_word_diversity": round(s_mean, 6), "n": len(s_vals)}
        result["multi_turn"][source] = {"mean_word_diversity": round(m_mean, 6), "n": len(m_vals)}
        diff = m_mean - s_mean if not (np.isnan(s_mean) or np.isnan(m_mean)) else float("nan")
        pct = (diff / s_mean * 100) if s_mean != 0 and not np.isnan(diff) else float("nan")
        if len(s_vals) >= 2 and len(m_vals) >= 2:
            t_stat, t_pval = stats.ttest_ind(m_vals, s_vals, equal_var=False)
            d = cohens_d_independent(m_vals, s_vals)
            result["comparison"][source] = {
                "mean_difference": round(float(diff), 6), "percent_difference": round(float(pct), 4),
                "ttest_ind_statistic": round(float(t_stat), 4), "ttest_ind_p_value": round(float(t_pval), 6),
                "significant_005": bool(t_pval < 0.05), "cohens_d": round(d, 4),
                "effect_size_interpretation": interpret_effect_size(d),
                "direction": "multi_turn_higher" if diff > 0 else "single_turn_higher",
            }
        else:
            result["comparison"][source] = {"error": "insufficient data"}

    all_single = [v for s in SOURCES for v in single_div[s]]
    all_multi = [v for s in SOURCES for v in multi_div[s]]
    s_all = np.array(all_single)
    m_all = np.array(all_multi)
    combined = {
        "single_turn_mean": round(float(np.mean(s_all)), 6) if len(s_all) > 0 else None,
        "multi_turn_mean": round(float(np.mean(m_all)), 6) if len(m_all) > 0 else None,
        "single_turn_n": len(s_all), "multi_turn_n": len(m_all),
    }
    if len(s_all) >= 2 and len(m_all) >= 2:
        t_stat, t_pval = stats.ttest_ind(m_all, s_all, equal_var=False)
        d = cohens_d_independent(m_all, s_all)
        combined.update({
            "mean_difference": round(float(np.mean(m_all) - np.mean(s_all)), 6),
            "ttest_ind_p_value": round(float(t_pval), 6), "significant_005": bool(t_pval < 0.05),
            "cohens_d": round(d, 4), "effect_size_interpretation": interpret_effect_size(d),
        })
    result["comparison"]["ALL_SOURCES_COMBINED"] = combined
    return result


def compute_effect_size_summary(test_results: dict) -> dict:
    all_abs_d = []
    per_comparison = {}
    for metric in METRICS:
        for key, res in test_results[metric].items():
            if "error" in res:
                continue
            d = res["cohens_d"]
            if not np.isnan(d):
                all_abs_d.append(abs(d))
                if key not in per_comparison:
                    per_comparison[key] = []
                per_comparison[key].append(abs(d))
    summary = {
        "overall": {
            "mean_abs_cohens_d": round(float(np.mean(all_abs_d)), 4) if all_abs_d else float("nan"),
            "median_abs_cohens_d": round(float(np.median(all_abs_d)), 4) if all_abs_d else float("nan"),
            "max_abs_cohens_d": round(float(np.max(all_abs_d)), 4) if all_abs_d else float("nan"),
            "min_abs_cohens_d": round(float(np.min(all_abs_d)), 4) if all_abs_d else float("nan"),
            "n_effects": len(all_abs_d),
        },
        "per_comparison": {},
    }
    for comp_key, ds in per_comparison.items():
        summary["per_comparison"][comp_key] = {
            "mean_abs_cohens_d": round(float(np.mean(ds)), 4),
            "max_abs_cohens_d": round(float(np.max(ds)), 4),
            "n_effects": len(ds),
        }
    return summary


def count_significant_results(test_results: dict) -> dict:
    counts = {"wilcoxon_p005": 0, "wilcoxon_p001": 0, "ttest_p005": 0, "ttest_p001": 0, "total_tests": 0}
    for metric in METRICS:
        for key, res in test_results[metric].items():
            if "error" in res:
                continue
            counts["total_tests"] += 1
            w = res.get("wilcoxon_signed_rank", {})
            t = res.get("paired_ttest", {})
            if w.get("significant_005"): counts["wilcoxon_p005"] += 1
            if w.get("significant_001"): counts["wilcoxon_p001"] += 1
            if t.get("significant_005"): counts["ttest_p005"] += 1
            if t.get("significant_001"): counts["ttest_p001"] += 1
    return counts


def extract_multi_turn_metrics(data: dict) -> dict:
    result = {}
    mt = data.get("multi_turn", {})
    for prompt_name, sources in mt.items():
        result[prompt_name] = {}
        for source in SOURCES:
            if source not in sources:
                continue
            samples = sources[source]
            all_turn_metrics = []
            for sample in samples:
                turns = sample.get("turns", [])
                for turn in turns:
                    m = turn.get("metrics", {})
                    if m is None:
                        continue
                    all_turn_metrics.append({
                        metric: safe_float(m.get(metric, float("nan"))) for metric in METRICS
                    })
            result[prompt_name][source] = all_turn_metrics
    return result


def compute_multi_turn_means(mt_metrics: dict) -> dict:
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


def analyze(data: dict) -> dict:
    model_name = data.get("model", "unknown")
    print(f"\n{'='*60}")
    print(f"Analyzing: {model_name}")
    print(f"{'='*60}")

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

    print("\n--- Grand Means ---")
    for metric in METRICS:
        print(f"  {metric}:")
        for source in SOURCES:
            gm = grand_means[metric][source]
            print(f"    {source}: mean={gm['mean']:.6f}, std={gm['std']:.6f}, n={gm['n_prompts']}")

    test_results = run_paired_tests(paired_vectors)

    print("\n--- Paired Tests (3 pairwise) ---")
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
            sig = " ***" if w.get("significant_005") or t.get("significant_005") else ""
            print(f"  {metric} | {key}: diff={pct:+.4f}% | W p={w_p:.4f} | t p={t_p:.4f} | d={d:.4f} ({interp}){sig}")

    cv_per_prompt = compute_cross_source_cv(prompt_means)
    mean_cv = compute_mean_cv(cv_per_prompt)
    print("\n--- Cross-Source CV% ---")
    for metric in METRICS:
        print(f"  {metric}: mean CV = {mean_cv[metric]:.4f}%")

    st_vs_mt = compute_single_vs_multi_diversity(data)
    print("\n--- Single vs Multi-Turn Diversity ---")
    for source in SOURCES:
        st_mean = st_vs_mt["single_turn"][source]["mean_word_diversity"]
        mt_mean = st_vs_mt["multi_turn"][source]["mean_word_diversity"]
        comp = st_vs_mt["comparison"][source]
        if "error" not in comp:
            print(f"  {source}: single={st_mean:.6f}, multi={mt_mean:.6f}, d={comp['cohens_d']:.4f} p={comp['ttest_ind_p_value']:.4f}")

    all_samples = compute_single_turn_all_samples(data)
    sample_level_stats = {}
    for metric in METRICS:
        sample_level_stats[metric] = {}
        for source in SOURCES:
            vals = np.array(all_samples[metric][source])
            if len(vals) > 0:
                sample_level_stats[metric][source] = {
                    "mean": round(float(np.mean(vals)), 6), "std": round(float(np.std(vals, ddof=1)), 6),
                    "median": round(float(np.median(vals)), 6), "n_samples": len(vals),
                }

    effect_summary = compute_effect_size_summary(test_results)
    sig_counts = count_significant_results(test_results)
    mt_metrics = extract_multi_turn_metrics(data)
    mt_means = compute_multi_turn_means(mt_metrics)

    print(f"\n--- Summary ---")
    print(f"  Mean |d|: {effect_summary['overall']['mean_abs_cohens_d']:.4f}")
    print(f"  Max |d|: {effect_summary['overall']['max_abs_cohens_d']:.4f}")
    print(f"  Significant (p<0.05): {sig_counts['wilcoxon_p005']}/{sig_counts['total_tests']} Wilcoxon, {sig_counts['ttest_p005']}/{sig_counts['total_tests']} t-test")

    return {
        "model": model_name,
        "analysis_type": "comprehensive_entropy_seeding_statistical_tests",
        "analysis_timestamp": "2026-02-09",
        "design": {
            "single_turn_prompts": len(prompt_means),
            "multi_turn_prompts": len(data.get("multi_turn", {})),
            "sources": SOURCES,
            "pairwise_comparisons": [f"{a}_vs_{b}" for a, b in PAIRWISE_COMPARISONS],
            "samples_per_condition": data.get("num_samples", 5),
            "metrics_analyzed": METRICS,
        },
        "grand_means_per_source": grand_means,
        "sample_level_descriptive_stats": sample_level_stats,
        "paired_tests_by_prompt_mean": test_results,
        "effect_size_summary": effect_summary,
        "significance_counts": sig_counts,
        "cross_source_cv_per_prompt": cv_per_prompt,
        "mean_cv_across_prompts": mean_cv,
        "single_turn_vs_multi_turn": st_vs_mt,
        "multi_turn_means": mt_means,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python statistical_analysis_generic.py <input.json> [output.json]")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)

    print(f"\nLoading {input_file} ...")
    with open(input_file) as f:
        data = json.load(f)

    model_name = data.get("model", "unknown").replace(":", "_").replace("/", "_")

    if len(sys.argv) >= 3:
        output_file = Path(sys.argv[2])
    else:
        output_file = input_file.parent.parent / f"statistical_tests_{model_name}_comprehensive.json"

    result = analyze(data)

    output_str = json.dumps(result, indent=2, default=str)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        f.write(output_str)
    print(f"\nWrote: {output_file}")


if __name__ == "__main__":
    main()
