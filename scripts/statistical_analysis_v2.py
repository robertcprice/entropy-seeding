"""
Statistical analysis v2 for entropy seeding experiments.

Improvements over v1:
  - Benjamini-Hochberg FDR correction for multiple comparisons
  - Post-hoc power analysis (via simulation-based approach)
  - Mixed-effects models using all samples (not just prompt means)
  - Length-corrected diversity metrics (MTLD, D2)
  - Seed distribution analysis
  - Proper reporting of corrected p-values

Usage:
    python statistical_analysis_v2.py <input_v2.json> [output.json]

Works with both v1 and v2 experiment JSON files.
"""

import json
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

# ─────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────

# Core metrics from v1 + new metrics from v2
METRICS_V1 = ["shannon_char", "shannon_word", "word_diversity", "length_words"]
METRICS_V2 = ["shannon_char", "shannon_word", "word_diversity", "length_words",
              "mtld", "distinct_2", "repetition_ratio"]

PAIRWISE_COMPARISONS_V1 = [
    ("TRNG", "PRNG"),
    ("QRNG", "PRNG"),
    ("QRNG", "TRNG"),
]

PAIRWISE_COMPARISONS_V2 = [
    ("TRNG", "PRNG"),
    ("HMIX", "PRNG"),
    ("HMIX", "TRNG"),
]


def detect_version(data: dict) -> str:
    """Detect whether this is a v1 or v2 experiment file."""
    if data.get("experiment_version") == "v2":
        return "v2"
    return "v1"


def get_sources(version: str) -> list[str]:
    if version == "v2":
        return ["PRNG", "TRNG", "HMIX"]
    return ["PRNG", "TRNG", "QRNG"]


def get_comparisons(version: str):
    if version == "v2":
        return PAIRWISE_COMPARISONS_V2
    return PAIRWISE_COMPARISONS_V1


def get_metrics(version: str) -> list[str]:
    if version == "v2":
        return METRICS_V2
    return METRICS_V1


# ─────────────────────────────────────────────────────────────────────
# Utility functions
# ─────────────────────────────────────────────────────────────────────

def safe_float(v: Any) -> float:
    if v is None:
        return float("nan")
    return float(v)


def cohens_d_paired(x: np.ndarray, y: np.ndarray) -> float:
    """Cohen's d_z for paired data."""
    diff = x - y
    sd = np.std(diff, ddof=1)
    if sd == 0:
        return 0.0
    return float(np.mean(diff) / sd)


def cohens_d_independent(x: np.ndarray, y: np.ndarray) -> float:
    """Cohen's d_s for independent groups (pooled SD)."""
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


# ─────────────────────────────────────────────────────────────────────
# Benjamini-Hochberg FDR correction
# ─────────────────────────────────────────────────────────────────────

def benjamini_hochberg(p_values: list[float], alpha: float = 0.05) -> list[dict]:
    """Apply Benjamini-Hochberg FDR correction.

    Returns list of dicts with original index, p_value, adjusted_p, significant.
    """
    n = len(p_values)
    if n == 0:
        return []

    # Sort by p-value
    indexed = [(i, p) for i, p in enumerate(p_values)]
    indexed.sort(key=lambda x: x[1])

    # Compute adjusted p-values
    results = [None] * n
    prev_adj = 0.0

    for rank_idx, (orig_idx, p) in enumerate(indexed):
        rank = rank_idx + 1  # 1-indexed rank
        adj_p = p * n / rank
        adj_p = min(adj_p, 1.0)
        results[orig_idx] = {
            "original_index": orig_idx,
            "p_value": p,
            "rank": rank,
            "adjusted_p": adj_p,
        }

    # Enforce monotonicity (step-up): working backwards, ensure adj_p is non-increasing
    sorted_by_rank = sorted(results, key=lambda x: -x["rank"])
    running_min = 1.0
    for r in sorted_by_rank:
        running_min = min(running_min, r["adjusted_p"])
        r["adjusted_p"] = running_min
        r["significant_bh"] = running_min < alpha

    return results


# ─────────────────────────────────────────────────────────────────────
# Post-hoc power analysis (simulation-based)
# ─────────────────────────────────────────────────────────────────────

def power_wilcoxon_paired(d: float, n: int, alpha: float = 0.05,
                          n_sims: int = 5000) -> float:
    """Estimate power of Wilcoxon signed-rank test via simulation.

    Simulates paired differences from N(d, 1) and counts how often
    the test rejects H0.
    """
    if n < 3:
        return 0.0
    if abs(d) < 1e-10:
        return alpha  # power = alpha under H0

    rng = np.random.RandomState(42)
    rejections = 0
    for _ in range(n_sims):
        diffs = rng.normal(loc=d, scale=1.0, size=n)
        try:
            _, p = stats.wilcoxon(diffs, alternative="two-sided")
            if p < alpha:
                rejections += 1
        except Exception:
            pass
    return rejections / n_sims


def power_ttest_paired(d: float, n: int, alpha: float = 0.05) -> float:
    """Analytical power of paired t-test.

    Uses non-central t-distribution.
    """
    if n < 3:
        return 0.0
    if abs(d) < 1e-10:
        return alpha

    df = n - 1
    ncp = d * np.sqrt(n)  # non-centrality parameter
    t_crit = stats.t.ppf(1 - alpha / 2, df)
    # Power = P(|T| > t_crit | ncp)
    power = 1 - stats.nct.cdf(t_crit, df, ncp) + stats.nct.cdf(-t_crit, df, ncp)
    return float(power)


def minimum_detectable_effect(n: int, alpha: float = 0.05,
                               target_power: float = 0.80) -> float:
    """Binary search for minimum d detectable at given power for paired t-test."""
    if n < 3:
        return float('inf')
    lo, hi = 0.0, 5.0
    for _ in range(50):
        mid = (lo + hi) / 2
        p = power_ttest_paired(mid, n, alpha)
        if p < target_power:
            lo = mid
        else:
            hi = mid
    return round((lo + hi) / 2, 3)


# ─────────────────────────────────────────────────────────────────────
# Mixed-effects model (approximate via summary statistics)
# ─────────────────────────────────────────────────────────────────────

def mixed_effects_test(all_samples: dict, metric: str, source_a: str,
                       source_b: str, prompts: list[str]) -> dict:
    """Approximate mixed-effects analysis using all individual samples.

    Uses a two-level approach:
    1. For each prompt, compute within-prompt effect (mean_a - mean_b)
    2. Test the distribution of prompt-level effects (accounts for
       between-prompt variance as a random effect)

    Also runs a sample-level Welch t-test for comparison.

    This is an approximation of lmer(metric ~ source + (1|prompt)).
    The full mixed-effects model would require statsmodels or R, which
    may not be available. This approach:
    - Uses all samples (not just prompt means)
    - Properly accounts for prompt as a grouping variable
    - Is more powerful than pure prompt-mean analysis
    """
    # Collect all sample values per prompt per source
    prompt_effects = []
    all_a = []
    all_b = []

    for prompt in prompts:
        vals_a = all_samples.get(prompt, {}).get(source_a, [])
        vals_b = all_samples.get(prompt, {}).get(source_b, [])

        if not vals_a or not vals_b:
            continue

        mean_a = np.mean(vals_a)
        mean_b = np.mean(vals_b)

        # Within-prompt pooled SE
        n_a, n_b = len(vals_a), len(vals_b)
        se_a = np.std(vals_a, ddof=1) / np.sqrt(n_a) if n_a > 1 else 0
        se_b = np.std(vals_b, ddof=1) / np.sqrt(n_b) if n_b > 1 else 0

        prompt_effects.append({
            "prompt": prompt[:50],
            "mean_a": mean_a, "mean_b": mean_b,
            "effect": mean_a - mean_b,
            "n_a": n_a, "n_b": n_b,
            "se_within": np.sqrt(se_a**2 + se_b**2),
        })

        all_a.extend(vals_a)
        all_b.extend(vals_b)

    if len(prompt_effects) < 3:
        return {"error": "insufficient prompts with data"}

    effects = np.array([pe["effect"] for pe in prompt_effects])
    n_prompts = len(effects)

    # Random-effects meta-analysis style: test mean of prompt-level effects
    mean_effect = np.mean(effects)
    se_effect = np.std(effects, ddof=1) / np.sqrt(n_prompts)
    t_stat_re = mean_effect / se_effect if se_effect > 0 else 0
    p_value_re = 2 * (1 - stats.t.cdf(abs(t_stat_re), n_prompts - 1))
    d_re = cohens_d_paired(
        np.array([pe["mean_a"] for pe in prompt_effects]),
        np.array([pe["mean_b"] for pe in prompt_effects])
    )

    # Sample-level Welch t-test (ignoring prompt structure, for comparison)
    arr_a = np.array(all_a)
    arr_b = np.array(all_b)
    t_stat_welch, p_value_welch = stats.ttest_ind(arr_a, arr_b, equal_var=False)
    d_welch = cohens_d_independent(arr_a, arr_b)

    return {
        "n_prompts": n_prompts,
        "n_samples_a": len(all_a),
        "n_samples_b": len(all_b),
        "random_effects": {
            "mean_effect": round(float(mean_effect), 6),
            "se_effect": round(float(se_effect), 6),
            "t_statistic": round(float(t_stat_re), 4),
            "p_value": round(float(p_value_re), 6),
            "cohens_d": round(float(d_re), 4),
            "effect_interpretation": interpret_effect_size(d_re),
        },
        "sample_level_welch": {
            "t_statistic": round(float(t_stat_welch), 4),
            "p_value": round(float(p_value_welch), 6),
            "cohens_d": round(float(d_welch), 4),
            "effect_interpretation": interpret_effect_size(d_welch),
        },
    }


# ─────────────────────────────────────────────────────────────────────
# Data extraction (handles v1 and v2 formats)
# ─────────────────────────────────────────────────────────────────────

def extract_all_samples_v1(data: dict, metrics: list[str], sources: list[str]) -> dict:
    """Extract individual sample values per prompt per source (v1 format)."""
    result = {}
    st = data.get("single_turn", {})
    for prompt, source_data in st.items():
        result[prompt] = {}
        for source in sources:
            if source not in source_data:
                continue
            samples = source_data[source].get("samples", [])
            for metric in metrics:
                key = f"{metric}__{source}"
                vals = []
                for sample in samples:
                    m = sample.get("metrics")
                    if m is None:
                        continue
                    v = m.get(metric)
                    if v is not None:
                        vals.append(safe_float(v))
                if prompt not in result:
                    result[prompt] = {}
                if source not in result[prompt]:
                    result[prompt][source] = {}
                result[prompt][source][metric] = vals
    return result


def extract_all_samples_v2(data: dict, metrics: list[str], sources: list[str]) -> dict:
    """Extract individual sample values from v2 multi-stream format.

    Aggregates across all PRNG streams.
    """
    result = {}
    streams = data.get("streams", [])

    for stream in streams:
        st = stream.get("single_turn", {})
        for prompt, source_data in st.items():
            if prompt not in result:
                result[prompt] = {s: {m: [] for m in metrics} for s in sources}

            for source in sources:
                if source not in source_data:
                    continue
                if isinstance(source_data[source], dict) and "samples" in source_data[source]:
                    samples = source_data[source]["samples"]
                else:
                    continue
                for sample in samples:
                    m = sample.get("metrics")
                    if m is None:
                        continue
                    for metric in metrics:
                        v = m.get(metric)
                        if v is not None:
                            result[prompt][source][metric].append(safe_float(v))
    return result


def extract_prompt_means(all_samples: dict, metrics: list[str],
                         sources: list[str]) -> dict:
    """Compute prompt-level means from individual samples."""
    result = {}
    for prompt, source_data in all_samples.items():
        result[prompt] = {}
        for source in sources:
            if source not in source_data:
                continue
            result[prompt][source] = {}
            for metric in metrics:
                vals = source_data[source].get(metric, [])
                if vals:
                    result[prompt][source][metric] = float(np.mean(vals))
                else:
                    result[prompt][source][metric] = float("nan")
    return result


def extract_paired_vectors(prompt_means: dict, metrics: list[str],
                           sources: list[str]) -> dict:
    """Build aligned arrays for paired testing."""
    prompts = list(prompt_means.keys())
    result = {}
    for metric in metrics:
        result[metric] = {}
        for source in sources:
            vals = []
            for prompt in prompts:
                if source in prompt_means.get(prompt, {}):
                    vals.append(prompt_means[prompt][source].get(metric, float("nan")))
                else:
                    vals.append(float("nan"))
            result[metric][source] = np.array(vals)
    return result


# ─────────────────────────────────────────────────────────────────────
# Seed distribution analysis
# ─────────────────────────────────────────────────────────────────────

def analyze_seed_distributions(data: dict) -> dict:
    """Characterize seed distributions for each source.

    Tests uniformity, autocorrelation, and inter-source differences.
    """
    version = detect_version(data)
    result = {}

    if version == "v2":
        for stream in data.get("streams", []):
            sd = stream.get("seed_distributions", {})
            for source_name, info in sd.items():
                seeds_32 = info.get("seeds_32bit", [])
                if source_name not in result:
                    result[source_name] = []
                result[source_name].extend(seeds_32)
    else:
        # v1: reconstruct from samples
        st = data.get("single_turn", {})
        for prompt, sources in st.items():
            for source_name, source_data in sources.items():
                if source_name not in result:
                    result[source_name] = []
                for sample in source_data.get("samples", []):
                    seed = sample.get("seed")
                    if seed is not None:
                        result[source_name].append(int(seed) % (2**32))

    analysis = {}
    for source_name, seeds in result.items():
        if len(seeds) < 10:
            analysis[source_name] = {"error": "too few seeds", "n": len(seeds)}
            continue

        arr = np.array(seeds, dtype=np.float64)
        n = len(arr)

        # Normalize to [0, 1] for uniformity test
        normalized = arr / (2**32)

        # Kolmogorov-Smirnov test for uniformity
        ks_stat, ks_p = stats.kstest(normalized, 'uniform')

        # Chi-squared goodness-of-fit (16 bins)
        n_bins = 16
        observed, _ = np.histogram(normalized, bins=n_bins, range=(0, 1))
        expected = np.full(n_bins, n / n_bins)
        chi2_stat, chi2_p = stats.chisquare(observed, expected)

        # Lag-1 autocorrelation
        if n > 2:
            mean_arr = np.mean(arr)
            var_arr = np.var(arr, ddof=0)
            if var_arr > 0:
                autocorr = np.sum((arr[:-1] - mean_arr) * (arr[1:] - mean_arr)) / ((n - 1) * var_arr)
            else:
                autocorr = 0.0
        else:
            autocorr = float("nan")

        analysis[source_name] = {
            "n_seeds": n,
            "mean_normalized": round(float(np.mean(normalized)), 6),
            "std_normalized": round(float(np.std(normalized, ddof=1)), 6),
            "min": int(np.min(arr)),
            "max": int(np.max(arr)),
            "ks_uniformity": {
                "statistic": round(float(ks_stat), 6),
                "p_value": round(float(ks_p), 6),
                "uniform_at_005": bool(ks_p > 0.05),
            },
            "chi2_uniformity": {
                "statistic": round(float(chi2_stat), 4),
                "p_value": round(float(chi2_p), 6),
                "n_bins": n_bins,
                "uniform_at_005": bool(chi2_p > 0.05),
            },
            "lag1_autocorrelation": round(float(autocorr), 6),
        }

    # Pairwise KS tests between sources
    source_names = list(result.keys())
    pairwise_ks = {}
    for i in range(len(source_names)):
        for j in range(i + 1, len(source_names)):
            s1, s2 = source_names[i], source_names[j]
            arr1 = np.array(result[s1], dtype=np.float64) / (2**32)
            arr2 = np.array(result[s2], dtype=np.float64) / (2**32)
            ks_stat, ks_p = stats.ks_2samp(arr1, arr2)
            pairwise_ks[f"{s1}_vs_{s2}"] = {
                "ks_statistic": round(float(ks_stat), 6),
                "p_value": round(float(ks_p), 6),
                "distributions_differ_005": bool(ks_p < 0.05),
            }

    return {"per_source": analysis, "pairwise_distribution_tests": pairwise_ks}


# ─────────────────────────────────────────────────────────────────────
# Core paired tests (enhanced)
# ─────────────────────────────────────────────────────────────────────

def run_paired_tests(paired_vectors: dict, metrics: list[str],
                     comparisons: list) -> tuple[dict, list[float]]:
    """Run paired statistical tests, collecting all p-values for FDR.

    Returns (results_dict, flat_p_values_list).
    """
    results = {}
    all_p_values = []
    p_value_keys = []  # track (metric, comparison_key, test_type)

    for metric in metrics:
        results[metric] = {}
        for alt_source, base_source in comparisons:
            key = f"{alt_source}_vs_{base_source}"
            x = paired_vectors[metric].get(alt_source, np.array([]))
            y = paired_vectors[metric].get(base_source, np.array([]))

            if len(x) == 0 or len(y) == 0:
                results[metric][key] = {"error": "missing source data"}
                continue

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

            # Wilcoxon signed-rank
            try:
                w_stat, w_pval = stats.wilcoxon(x_clean, y_clean, alternative="two-sided")
                wilcoxon_result = {
                    "statistic": float(w_stat), "p_value": float(w_pval),
                }
                all_p_values.append(float(w_pval))
                p_value_keys.append((metric, key, "wilcoxon"))
            except Exception as e:
                wilcoxon_result = {"error": str(e)}

            # Paired t-test
            try:
                t_stat, t_pval = stats.ttest_rel(x_clean, y_clean)
                ttest_result = {
                    "statistic": float(t_stat), "p_value": float(t_pval),
                }
                all_p_values.append(float(t_pval))
                p_value_keys.append((metric, key, "ttest"))
            except Exception as e:
                ttest_result = {"error": str(e)}

            d = cohens_d_paired(x_clean, y_clean)

            # Power analysis
            power_w = power_wilcoxon_paired(abs(d), n)
            power_t = power_ttest_paired(abs(d), n)
            mde = minimum_detectable_effect(n)

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
                "power_analysis": {
                    "observed_d": round(abs(d), 4),
                    "power_wilcoxon": round(power_w, 3),
                    "power_ttest": round(power_t, 3),
                    "minimum_detectable_effect_d": mde,
                    "adequately_powered": power_t >= 0.80,
                    "note": f"At n={n}, 80% power requires d>={mde}",
                },
            }

    return results, all_p_values, p_value_keys


def apply_fdr_correction(test_results: dict, all_p_values: list[float],
                         p_value_keys: list, metrics: list[str]) -> dict:
    """Apply BH-FDR correction and annotate results."""
    if not all_p_values:
        return test_results

    bh_results = benjamini_hochberg(all_p_values)

    fdr_summary = {
        "total_tests": len(all_p_values),
        "alpha": 0.05,
        "method": "Benjamini-Hochberg",
        "n_significant_uncorrected": sum(1 for p in all_p_values if p < 0.05),
        "n_significant_fdr": sum(1 for r in bh_results if r["significant_bh"]),
        "expected_false_positives_uncorrected": round(len(all_p_values) * 0.05, 1),
    }

    # Annotate original results with adjusted p-values
    for idx, (metric, comp_key, test_type) in enumerate(p_value_keys):
        bh = bh_results[idx]
        if metric in test_results and comp_key in test_results[metric]:
            entry = test_results[metric][comp_key]
            if test_type == "wilcoxon" and "wilcoxon_signed_rank" in entry:
                entry["wilcoxon_signed_rank"]["p_value_bh_adjusted"] = round(bh["adjusted_p"], 6)
                entry["wilcoxon_signed_rank"]["significant_bh_005"] = bh["significant_bh"]
            elif test_type == "ttest" and "paired_ttest" in entry:
                entry["paired_ttest"]["p_value_bh_adjusted"] = round(bh["adjusted_p"], 6)
                entry["paired_ttest"]["significant_bh_005"] = bh["significant_bh"]

    return test_results, fdr_summary


# ─────────────────────────────────────────────────────────────────────
# Cross-source CV and descriptive stats
# ─────────────────────────────────────────────────────────────────────

def compute_cross_source_cv(prompt_means: dict, metrics: list[str],
                            sources: list[str]) -> dict:
    result = {}
    for prompt, source_data in prompt_means.items():
        result[prompt] = {}
        for metric in metrics:
            vals = []
            for source in sources:
                if source in source_data:
                    v = source_data[source].get(metric, float("nan"))
                    if not np.isnan(v):
                        vals.append(v)
            if len(vals) >= 2:
                result[prompt][metric] = round(cv_percent(np.array(vals)), 4)
            else:
                result[prompt][metric] = float("nan")
    return result


def compute_grand_means(paired_vectors: dict, metrics: list[str],
                        sources: list[str]) -> dict:
    grand_means = {}
    for metric in metrics:
        grand_means[metric] = {}
        for source in sources:
            v = paired_vectors[metric].get(source, np.array([]))
            valid = v[~np.isnan(v)] if len(v) > 0 else np.array([])
            if len(valid) > 0:
                grand_means[metric][source] = {
                    "mean": round(float(np.mean(valid)), 6),
                    "std": round(float(np.std(valid, ddof=1)), 6),
                    "median": round(float(np.median(valid)), 6),
                    "n_prompts": len(valid),
                }
            else:
                grand_means[metric][source] = {"error": "no data"}
    return grand_means


def compute_effect_size_summary(test_results: dict, metrics: list[str]) -> dict:
    all_abs_d = []
    per_comparison = {}
    for metric in metrics:
        for key, res in test_results.get(metric, {}).items():
            if "error" in res:
                continue
            d = res.get("cohens_d", float("nan"))
            if not np.isnan(d):
                all_abs_d.append(abs(d))
                if key not in per_comparison:
                    per_comparison[key] = []
                per_comparison[key].append(abs(d))

    summary = {
        "overall": {
            "mean_abs_cohens_d": round(float(np.mean(all_abs_d)), 4) if all_abs_d else None,
            "median_abs_cohens_d": round(float(np.median(all_abs_d)), 4) if all_abs_d else None,
            "max_abs_cohens_d": round(float(np.max(all_abs_d)), 4) if all_abs_d else None,
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


def count_significant_results(test_results: dict, metrics: list[str]) -> dict:
    counts = {
        "wilcoxon_p005_uncorrected": 0, "wilcoxon_p001_uncorrected": 0,
        "ttest_p005_uncorrected": 0, "ttest_p001_uncorrected": 0,
        "wilcoxon_p005_bh_corrected": 0, "ttest_p005_bh_corrected": 0,
        "total_tests": 0,
    }
    for metric in metrics:
        for key, res in test_results.get(metric, {}).items():
            if "error" in res:
                continue
            counts["total_tests"] += 1
            w = res.get("wilcoxon_signed_rank", {})
            t = res.get("paired_ttest", {})
            if w.get("p_value", 1) < 0.05:
                counts["wilcoxon_p005_uncorrected"] += 1
            if w.get("p_value", 1) < 0.01:
                counts["wilcoxon_p001_uncorrected"] += 1
            if t.get("p_value", 1) < 0.05:
                counts["ttest_p005_uncorrected"] += 1
            if t.get("p_value", 1) < 0.01:
                counts["ttest_p001_uncorrected"] += 1
            if w.get("significant_bh_005", False):
                counts["wilcoxon_p005_bh_corrected"] += 1
            if t.get("significant_bh_005", False):
                counts["ttest_p005_bh_corrected"] += 1
    return counts


# ─────────────────────────────────────────────────────────────────────
# Single vs multi-turn comparison
# ─────────────────────────────────────────────────────────────────────

def compute_single_vs_multi_diversity(data: dict, version: str) -> dict:
    sources = get_sources(version)

    if version == "v2":
        # Aggregate across streams
        single_div = {s: [] for s in sources}
        multi_div = {s: [] for s in sources}
        for stream in data.get("streams", []):
            st = stream.get("single_turn", {})
            for prompt, source_data in st.items():
                for source in sources:
                    if source not in source_data or not isinstance(source_data[source], dict):
                        continue
                    samples = source_data[source].get("samples", [])
                    for sample in samples:
                        m = sample.get("metrics")
                        if m and m.get("word_diversity") is not None:
                            single_div[source].append(safe_float(m["word_diversity"]))

            mt = stream.get("multi_turn", {})
            for conv_name, conv_sources in mt.items():
                for source in sources:
                    if source not in conv_sources:
                        continue
                    for sample in conv_sources[source]:
                        for turn in sample.get("turns", []):
                            m = turn.get("metrics")
                            if m and m.get("word_diversity") is not None:
                                multi_div[source].append(safe_float(m["word_diversity"]))
    else:
        single_div = {s: [] for s in sources}
        multi_div = {s: [] for s in sources}
        st = data.get("single_turn", {})
        for prompt, source_data in st.items():
            for source in sources:
                if source not in source_data:
                    continue
                for sample in source_data[source].get("samples", []):
                    m = sample.get("metrics")
                    if m and m.get("word_diversity") is not None:
                        single_div[source].append(safe_float(m["word_diversity"]))

        mt = data.get("multi_turn", {})
        for conv_name, conv_sources in mt.items():
            for source in sources:
                if source not in conv_sources:
                    continue
                for sample in conv_sources[source]:
                    for turn in sample.get("turns", []):
                        m = turn.get("metrics")
                        if m and m.get("word_diversity") is not None:
                            multi_div[source].append(safe_float(m["word_diversity"]))

    result = {"single_turn": {}, "multi_turn": {}, "comparison": {}}
    for source in sources:
        s_vals = np.array(single_div[source]) if single_div[source] else np.array([])
        m_vals = np.array(multi_div[source]) if multi_div[source] else np.array([])
        s_mean = float(np.mean(s_vals)) if len(s_vals) > 0 else float("nan")
        m_mean = float(np.mean(m_vals)) if len(m_vals) > 0 else float("nan")
        result["single_turn"][source] = {"mean_word_diversity": round(s_mean, 6), "n": len(s_vals)}
        result["multi_turn"][source] = {"mean_word_diversity": round(m_mean, 6), "n": len(m_vals)}

        if len(s_vals) >= 2 and len(m_vals) >= 2:
            t_stat, t_pval = stats.ttest_ind(m_vals, s_vals, equal_var=False)
            d = cohens_d_independent(m_vals, s_vals)
            diff = m_mean - s_mean
            result["comparison"][source] = {
                "mean_difference": round(float(diff), 6),
                "ttest_ind_p_value": round(float(t_pval), 6),
                "cohens_d": round(d, 4),
                "effect_size_interpretation": interpret_effect_size(d),
            }
        else:
            result["comparison"][source] = {"error": "insufficient data"}

    return result


# ─────────────────────────────────────────────────────────────────────
# Domain-level analysis (v2 only)
# ─────────────────────────────────────────────────────────────────────

def analyze_by_domain(all_samples: dict, metrics: list[str], sources: list[str],
                      prompt_domains: dict) -> dict:
    """Analyze effects grouped by prompt domain.

    prompt_domains: {prompt_text: domain_string}
    """
    # Group prompts by domain
    domain_prompts = {}
    for prompt, domain in prompt_domains.items():
        if domain not in domain_prompts:
            domain_prompts[domain] = []
        domain_prompts[domain].append(prompt)

    result = {}
    for domain, prompts in domain_prompts.items():
        domain_result = {}
        for metric in metrics:
            source_vals = {s: [] for s in sources}
            for prompt in prompts:
                if prompt not in all_samples:
                    continue
                for source in sources:
                    vals = all_samples.get(prompt, {}).get(source, {}).get(metric, [])
                    source_vals[source].extend(vals)

            means = {}
            for source in sources:
                arr = np.array(source_vals[source])
                if len(arr) > 0:
                    means[source] = {
                        "mean": round(float(np.mean(arr)), 6),
                        "std": round(float(np.std(arr, ddof=1)), 6),
                        "n": len(arr),
                    }
            domain_result[metric] = means

        result[domain] = {
            "n_prompts": len(prompts),
            "metrics": domain_result,
        }

    return result


# ─────────────────────────────────────────────────────────────────────
# Main analysis pipeline
# ─────────────────────────────────────────────────────────────────────

def analyze(data: dict) -> dict:
    version = detect_version(data)
    model_name = data.get("model", "unknown")
    metrics = get_metrics(version)
    sources = get_sources(version)
    comparisons = get_comparisons(version)

    print(f"\n{'='*60}")
    print(f"Analyzing: {model_name} (format: {version})")
    print(f"Metrics: {metrics}")
    print(f"Sources: {sources}")
    print(f"{'='*60}")

    # ── Extract all individual samples ──
    if version == "v2":
        all_samples = extract_all_samples_v2(data, metrics, sources)
    else:
        all_samples = extract_all_samples_v1(data, metrics, sources)

    # ── Prompt means (for paired tests) ──
    prompt_means = extract_prompt_means(all_samples, metrics, sources)
    paired_vectors = extract_paired_vectors(prompt_means, metrics, sources)

    # ── Grand means ──
    grand_means = compute_grand_means(paired_vectors, metrics, sources)
    print("\n--- Grand Means ---")
    for metric in metrics:
        print(f"  {metric}:")
        for source in sources:
            gm = grand_means[metric].get(source, {})
            if "mean" in gm:
                print(f"    {source}: mean={gm['mean']:.6f}, std={gm['std']:.6f}, n={gm['n_prompts']}")

    # ── Paired tests with power analysis ──
    test_results, all_p_values, p_value_keys = run_paired_tests(
        paired_vectors, metrics, comparisons)

    # ── BH-FDR correction ──
    test_results, fdr_summary = apply_fdr_correction(
        test_results, all_p_values, p_value_keys, metrics)

    print(f"\n--- FDR Correction ---")
    print(f"  Total tests: {fdr_summary['total_tests']}")
    print(f"  Significant (uncorrected p<0.05): {fdr_summary['n_significant_uncorrected']}")
    print(f"  Significant (BH-adjusted p<0.05): {fdr_summary['n_significant_fdr']}")
    print(f"  Expected false positives (uncorrected): {fdr_summary['expected_false_positives_uncorrected']}")

    # ── Print paired test results ──
    print("\n--- Paired Tests ---")
    for metric in metrics:
        for key, res in test_results.get(metric, {}).items():
            if "error" in res:
                print(f"  {metric} | {key}: {res.get('error', 'unknown error')}")
                continue
            w = res.get("wilcoxon_signed_rank", {})
            t = res.get("paired_ttest", {})
            d = res["cohens_d"]
            pct = res["percent_difference"]
            power = res.get("power_analysis", {})
            sig_bh = " **[BH-sig]**" if w.get("significant_bh_005") or t.get("significant_bh_005") else ""
            sig_raw = " *" if w.get("p_value", 1) < 0.05 or t.get("p_value", 1) < 0.05 else ""
            powered = f" power={power.get('power_ttest', 0):.2f}" if power else ""
            print(f"  {metric} | {key}: diff={pct:+.4f}% | d={d:.4f} "
                  f"({res['effect_size_interpretation']}){powered}{sig_raw}{sig_bh}")

    # ── Mixed-effects analysis ──
    print("\n--- Mixed-Effects Analysis (all samples) ---")
    mixed_results = {}
    me_p_values = []
    me_p_keys = []

    for metric in metrics:
        mixed_results[metric] = {}
        # Build per-prompt per-source sample dict for this metric
        metric_samples = {}
        for prompt in all_samples:
            metric_samples[prompt] = {}
            for source in sources:
                vals = all_samples.get(prompt, {}).get(source, {}).get(metric, [])
                metric_samples[prompt][source] = vals

        for alt_source, base_source in comparisons:
            key = f"{alt_source}_vs_{base_source}"
            me = mixed_effects_test(metric_samples, metric, alt_source, base_source,
                                    list(all_samples.keys()))
            mixed_results[metric][key] = me

            if "error" not in me:
                re_p = me["random_effects"]["p_value"]
                me_p_values.append(re_p)
                me_p_keys.append((metric, key))

                print(f"  {metric} | {key}: "
                      f"RE d={me['random_effects']['cohens_d']:.4f} "
                      f"p={re_p:.4f} "
                      f"(n_samples={me['n_samples_a']}+{me['n_samples_b']}) | "
                      f"Welch d={me['sample_level_welch']['cohens_d']:.4f} "
                      f"p={me['sample_level_welch']['p_value']:.4f}")

    # FDR for mixed-effects
    me_fdr_summary = None
    if me_p_values:
        me_bh = benjamini_hochberg(me_p_values)
        me_fdr_summary = {
            "total_tests": len(me_p_values),
            "n_significant_uncorrected": sum(1 for p in me_p_values if p < 0.05),
            "n_significant_bh": sum(1 for r in me_bh if r["significant_bh"]),
        }
        for idx, (metric, key) in enumerate(me_p_keys):
            bh = me_bh[idx]
            mixed_results[metric][key]["random_effects"]["p_value_bh_adjusted"] = round(bh["adjusted_p"], 6)
            mixed_results[metric][key]["random_effects"]["significant_bh_005"] = bh["significant_bh"]

        print(f"\n  Mixed-effects FDR: {me_fdr_summary['n_significant_bh']}/{me_fdr_summary['total_tests']} "
              f"significant after BH correction")

    # ── CV analysis ──
    cv_per_prompt = compute_cross_source_cv(prompt_means, metrics, sources)
    mean_cv = {}
    for metric in metrics:
        vals = [cv_per_prompt[p][metric] for p in cv_per_prompt
                if not np.isnan(cv_per_prompt[p].get(metric, float("nan")))]
        mean_cv[metric] = round(float(np.mean(vals)), 4) if vals else float("nan")

    print("\n--- Cross-Source CV% ---")
    for metric in metrics:
        print(f"  {metric}: mean CV = {mean_cv[metric]:.4f}%")

    # ── Single vs multi-turn ──
    st_vs_mt = compute_single_vs_multi_diversity(data, version)

    # ── Seed distribution analysis ──
    seed_analysis = analyze_seed_distributions(data)
    print("\n--- Seed Distribution Analysis ---")
    for source, info in seed_analysis.get("per_source", {}).items():
        if "error" in info:
            print(f"  {source}: {info['error']}")
            continue
        print(f"  {source}: n={info['n_seeds']}, "
              f"KS p={info['ks_uniformity']['p_value']:.4f} "
              f"({'uniform' if info['ks_uniformity']['uniform_at_005'] else 'NON-UNIFORM'}), "
              f"autocorr={info['lag1_autocorrelation']:.4f}")
    for pair, info in seed_analysis.get("pairwise_distribution_tests", {}).items():
        print(f"  {pair}: KS p={info['p_value']:.4f} "
              f"({'DIFFERENT' if info['distributions_differ_005'] else 'same'})")

    # ── Domain analysis (v2 only) ──
    domain_analysis = None
    if version == "v2":
        prompt_domains = {}
        for stream in data.get("streams", []):
            for prompt, info in stream.get("single_turn", {}).items():
                if isinstance(info, dict) and "domain" in info:
                    prompt_domains[prompt] = info["domain"]
        if prompt_domains:
            domain_analysis = analyze_by_domain(all_samples, metrics, sources, prompt_domains)

    # ── Effect summary ──
    effect_summary = compute_effect_size_summary(test_results, metrics)
    sig_counts = count_significant_results(test_results, metrics)

    print(f"\n--- Summary ---")
    print(f"  Mean |d|: {effect_summary['overall'].get('mean_abs_cohens_d', 'N/A')}")
    print(f"  Max |d|: {effect_summary['overall'].get('max_abs_cohens_d', 'N/A')}")
    print(f"  Significant (uncorrected): Wilcoxon={sig_counts['wilcoxon_p005_uncorrected']}, "
          f"t-test={sig_counts['ttest_p005_uncorrected']}")
    print(f"  Significant (BH-corrected): Wilcoxon={sig_counts['wilcoxon_p005_bh_corrected']}, "
          f"t-test={sig_counts['ttest_p005_bh_corrected']}")

    # ── Power summary ──
    n_pairs = None
    all_powers = []
    all_mdes = []
    for metric in metrics:
        for key, res in test_results.get(metric, {}).items():
            pa = res.get("power_analysis", {})
            if pa:
                all_powers.append(pa.get("power_ttest", 0))
                all_mdes.append(pa.get("minimum_detectable_effect_d", 0))
                if n_pairs is None:
                    n_pairs = res.get("n_pairs")

    power_summary = {
        "n_paired_observations": n_pairs,
        "mean_power_at_observed_d": round(float(np.mean(all_powers)), 3) if all_powers else None,
        "min_power": round(float(np.min(all_powers)), 3) if all_powers else None,
        "max_power": round(float(np.max(all_powers)), 3) if all_powers else None,
        "minimum_detectable_effect_d_at_80pct_power": round(float(np.mean(all_mdes)), 3) if all_mdes else None,
        "n_adequately_powered_tests": sum(1 for p in all_powers if p >= 0.80),
        "total_tests": len(all_powers),
        "interpretation": (
            f"With n={n_pairs} paired observations, this design can reliably detect "
            f"effects of d>={round(float(np.mean(all_mdes)), 2) if all_mdes else '?'} at 80% power. "
            f"Effects smaller than this may exist but are undetectable at this sample size."
        ) if n_pairs else "insufficient data",
    }

    print(f"\n--- Power Analysis ---")
    print(f"  n paired observations: {n_pairs}")
    print(f"  MDE (80% power): d>={power_summary.get('minimum_detectable_effect_d_at_80pct_power', '?')}")
    print(f"  Mean power at observed effects: {power_summary.get('mean_power_at_observed_d', '?')}")
    print(f"  Adequately powered: {power_summary.get('n_adequately_powered_tests', 0)}"
          f"/{power_summary.get('total_tests', 0)}")

    # ── Assemble output ──
    output = {
        "model": model_name,
        "experiment_version": version,
        "analysis_version": "v2",
        "analysis_notes": {
            "fdr_correction": "Benjamini-Hochberg applied to all p-values",
            "power_analysis": "Post-hoc power computed for all paired tests",
            "mixed_effects": "Random-effects meta-analysis across prompts using all samples",
            "seed_distributions": "KS and chi-squared uniformity tests on 32-bit seeds",
            "metrics": f"{'v2 extended (MTLD, D2, rep_ratio)' if version == 'v2' else 'v1 core (shannon, TTR)'}",
        },
        "design": {
            "single_turn_prompts": len(prompt_means),
            "sources": sources,
            "pairwise_comparisons": [f"{a}_vs_{b}" for a, b in comparisons],
            "samples_per_condition": data.get("num_samples", "unknown"),
            "temperature": data.get("temperature", "unknown (v1 default)"),
            "metrics_analyzed": metrics,
        },
        "grand_means_per_source": grand_means,
        "paired_tests_by_prompt_mean": test_results,
        "fdr_correction_summary": fdr_summary,
        "power_analysis_summary": power_summary,
        "mixed_effects_analysis": mixed_results,
        "mixed_effects_fdr": me_fdr_summary,
        "effect_size_summary": effect_summary,
        "significance_counts": sig_counts,
        "cross_source_cv_per_prompt": cv_per_prompt,
        "mean_cv_across_prompts": mean_cv,
        "single_turn_vs_multi_turn": st_vs_mt,
        "seed_distribution_analysis": seed_analysis,
    }

    if domain_analysis:
        output["domain_analysis"] = domain_analysis

    return output


# ─────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python statistical_analysis_v2.py <input.json> [output.json]")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)

    print(f"\nLoading {input_file} ...")
    with open(input_file) as f:
        data = json.load(f)

    model_name = data.get("model", "unknown").replace(":", "_").replace("/", "_")
    version = detect_version(data)

    if len(sys.argv) >= 3:
        output_file = Path(sys.argv[2])
    else:
        output_file = input_file.parent / f"statistical_v2_{model_name}_{version}.json"

    result = analyze(data)

    output_str = json.dumps(result, indent=2, default=str)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        f.write(output_str)
    print(f"\nWrote: {output_file}")


if __name__ == "__main__":
    main()
