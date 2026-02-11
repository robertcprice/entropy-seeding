#!/usr/bin/env python3
"""
Seed distribution analysis utility.

Characterizes the 32-bit seed distributions for each entropy source
independently of any LLM generation. This tests the actual mechanism:
are the seed distributions statistically different?

Tests:
  - Kolmogorov-Smirnov uniformity test
  - Chi-squared goodness-of-fit (256 bins)
  - Anderson-Darling test
  - Lag-1 through lag-5 autocorrelation
  - Runs test for randomness
  - Inter-source 2-sample KS test
  - Bit-level analysis (per-bit bias)

Usage:
    python analyze_seed_distributions.py --n 10000
    python analyze_seed_distributions.py --n 10000 --from-experiment results/v2.json
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import argparse
import hashlib
import json
import random
import secrets
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
from scipy import stats

OUTPUT_DIR = Path(__file__).parent.parent / "results" / "seed_analysis"


# ─────────────────────────────────────────────────────────────────────
# Seed generators (matching experiment v2)
# ─────────────────────────────────────────────────────────────────────

def generate_prng_seeds(n: int, stream_seed: int = 42) -> list[int]:
    rng = random.Random(stream_seed)
    return [rng.getrandbits(64) % (2**32) for _ in range(n)]


def generate_trng_seeds(n: int) -> list[int]:
    return [int.from_bytes(secrets.token_bytes(8), 'big') % (2**32) for _ in range(n)]


def generate_hmix_seeds(n: int) -> list[int]:
    seeds = []
    for i in range(n):
        data = f"{time.time_ns()}-{secrets.token_hex(16)}-{i}"
        h = hashlib.sha256(data.encode()).digest()
        seeds.append(int.from_bytes(h[:8], 'big') % (2**32))
    return seeds


# ─────────────────────────────────────────────────────────────────────
# Statistical tests
# ─────────────────────────────────────────────────────────────────────

def test_uniformity(seeds: list[int], n_bins: int = 256) -> dict:
    """Comprehensive uniformity testing."""
    arr = np.array(seeds, dtype=np.float64)
    n = len(arr)
    normalized = arr / (2**32)

    # KS test
    ks_stat, ks_p = stats.kstest(normalized, 'uniform')

    # Chi-squared (multiple bin sizes)
    chi2_results = {}
    for bins in [16, 64, 256]:
        observed, _ = np.histogram(normalized, bins=bins, range=(0, 1))
        expected = np.full(bins, n / bins)
        chi2_stat, chi2_p = stats.chisquare(observed, expected)
        chi2_results[f"{bins}_bins"] = {
            "statistic": round(float(chi2_stat), 4),
            "p_value": round(float(chi2_p), 6),
            "uniform": bool(chi2_p > 0.05),
        }

    # Anderson-Darling: transform uniform to normal via inverse CDF, test normality
    normal_transformed = stats.norm.ppf(np.clip(normalized, 1e-10, 1 - 1e-10))
    try:
        ad_result = stats.anderson(normal_transformed, dist='norm')
        ad_stat_u = ad_result.statistic
        ad_crit_u = ad_result.critical_values
        ad_sig_u = ad_result.significance_level
    except Exception:
        ad_stat_u, ad_crit_u, ad_sig_u = 0, [0], [0]

    return {
        "n": n,
        "mean": round(float(np.mean(normalized)), 6),
        "std": round(float(np.std(normalized, ddof=1)), 6),
        "expected_mean": 0.5,
        "expected_std": round(1 / np.sqrt(12), 6),  # std of Uniform(0,1)
        "ks_test": {
            "statistic": round(float(ks_stat), 6),
            "p_value": round(float(ks_p), 6),
            "uniform": bool(ks_p > 0.05),
        },
        "chi_squared": chi2_results,
        "anderson_darling": {
            "statistic": round(float(ad_stat_u), 4),
            "critical_values": {f"{s}%": round(float(c), 4) for c, s in zip(ad_crit_u, ad_sig_u)},
        },
    }


def test_autocorrelation(seeds: list[int], max_lag: int = 10) -> dict:
    """Test serial correlation at multiple lags."""
    arr = np.array(seeds, dtype=np.float64)
    n = len(arr)
    mean = np.mean(arr)
    var = np.var(arr, ddof=0)

    if var == 0:
        return {"error": "zero variance"}

    results = {}
    for lag in range(1, min(max_lag + 1, n)):
        autocorr = np.sum((arr[:-lag] - mean) * (arr[lag:] - mean)) / ((n - lag) * var)
        # Under H0 (independence), autocorr ~ N(0, 1/n) for large n
        z = autocorr * np.sqrt(n)
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))
        results[f"lag_{lag}"] = {
            "autocorrelation": round(float(autocorr), 6),
            "z_statistic": round(float(z), 4),
            "p_value": round(float(p_value), 6),
            "significant": bool(p_value < 0.05),
        }

    return results


def test_runs(seeds: list[int]) -> dict:
    """Wald-Wolfowitz runs test for randomness."""
    arr = np.array(seeds, dtype=np.float64)
    median = np.median(arr)
    binary = (arr > median).astype(int)

    # Count runs
    runs = 1
    for i in range(1, len(binary)):
        if binary[i] != binary[i - 1]:
            runs += 1

    n1 = int(np.sum(binary))
    n0 = len(binary) - n1
    n = n0 + n1

    if n0 == 0 or n1 == 0:
        return {"error": "all values on same side of median"}

    # Expected runs and variance under H0
    expected_runs = (2 * n0 * n1) / n + 1
    var_runs = (2 * n0 * n1 * (2 * n0 * n1 - n)) / (n**2 * (n - 1))

    if var_runs <= 0:
        return {"error": "zero variance in runs"}

    z = (runs - expected_runs) / np.sqrt(var_runs)
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    return {
        "observed_runs": runs,
        "expected_runs": round(float(expected_runs), 2),
        "z_statistic": round(float(z), 4),
        "p_value": round(float(p_value), 6),
        "random": bool(p_value > 0.05),
    }


def test_bit_bias(seeds: list[int], n_bits: int = 32) -> dict:
    """Test per-bit bias across all seeds."""
    n = len(seeds)
    bit_counts = np.zeros(n_bits)

    for seed in seeds:
        for bit in range(n_bits):
            if seed & (1 << bit):
                bit_counts[bit] += 1

    # Each bit should be 1 approximately n/2 times
    expected = n / 2
    results = {}
    biased_bits = 0

    for bit in range(n_bits):
        count = int(bit_counts[bit])
        proportion = count / n
        p_value = stats.binomtest(count, n, 0.5).pvalue
        is_biased = p_value < 0.05 / n_bits  # Bonferroni-corrected
        if is_biased:
            biased_bits += 1
        results[f"bit_{bit}"] = {
            "count_1": count,
            "proportion": round(proportion, 4),
            "p_value": round(float(p_value), 6),
            "biased": is_biased,
        }

    return {
        "n_seeds": n,
        "n_bits_tested": n_bits,
        "n_biased_bits": biased_bits,
        "overall_proportion_1": round(float(np.mean(bit_counts) / n), 6),
        "per_bit": results,
    }


def test_pairwise_distribution(seeds_a: list[int], seeds_b: list[int],
                                name: str) -> dict:
    """Two-sample tests between source distributions."""
    arr_a = np.array(seeds_a, dtype=np.float64) / (2**32)
    arr_b = np.array(seeds_b, dtype=np.float64) / (2**32)

    # KS 2-sample
    ks_stat, ks_p = stats.ks_2samp(arr_a, arr_b)

    # Mann-Whitney U
    u_stat, u_p = stats.mannwhitneyu(arr_a, arr_b, alternative='two-sided')

    # Welch t-test
    t_stat, t_p = stats.ttest_ind(arr_a, arr_b, equal_var=False)

    return {
        "comparison": name,
        "n_a": len(seeds_a),
        "n_b": len(seeds_b),
        "mean_a": round(float(np.mean(arr_a)), 6),
        "mean_b": round(float(np.mean(arr_b)), 6),
        "ks_2sample": {
            "statistic": round(float(ks_stat), 6),
            "p_value": round(float(ks_p), 6),
            "different": bool(ks_p < 0.05),
        },
        "mann_whitney_u": {
            "statistic": round(float(u_stat), 4),
            "p_value": round(float(u_p), 6),
            "different": bool(u_p < 0.05),
        },
        "welch_t": {
            "statistic": round(float(t_stat), 4),
            "p_value": round(float(t_p), 6),
            "different": bool(t_p < 0.05),
        },
    }


# ─────────────────────────────────────────────────────────────────────
# Main analysis
# ─────────────────────────────────────────────────────────────────────

def analyze_from_generators(n: int, prng_seeds_list: list[int] = None) -> dict:
    """Generate seeds and run full analysis suite."""
    if prng_seeds_list is None:
        prng_seeds_list = [42, 123, 7, 999, 314]

    print(f"Generating {n} seeds per source...")

    all_seeds = {}

    # Multiple PRNG streams
    for ps in prng_seeds_list:
        key = f"PRNG_stream_{ps}"
        all_seeds[key] = generate_prng_seeds(n, stream_seed=ps)

    # Aggregate PRNG (all streams combined)
    all_seeds["PRNG_combined"] = []
    for ps in prng_seeds_list:
        all_seeds["PRNG_combined"].extend(all_seeds[f"PRNG_stream_{ps}"])

    all_seeds["TRNG"] = generate_trng_seeds(n)
    all_seeds["HMIX"] = generate_hmix_seeds(n)

    results = {
        "analysis_type": "seed_distribution_characterization",
        "timestamp": datetime.now().isoformat(),
        "n_per_source": n,
        "prng_streams": prng_seeds_list,
        "per_source": {},
        "pairwise_comparisons": {},
        "summary": {},
    }

    # Per-source analysis
    for source_name, seeds in all_seeds.items():
        print(f"\nAnalyzing {source_name} ({len(seeds)} seeds)...")
        results["per_source"][source_name] = {
            "uniformity": test_uniformity(seeds),
            "autocorrelation": test_autocorrelation(seeds),
            "runs_test": test_runs(seeds),
            "bit_bias": test_bit_bias(seeds),
        }

    # Pairwise comparisons (main sources only)
    main_sources = ["PRNG_combined", "TRNG", "HMIX"]
    for i in range(len(main_sources)):
        for j in range(i + 1, len(main_sources)):
            name = f"{main_sources[i]}_vs_{main_sources[j]}"
            print(f"\nComparing {name}...")
            results["pairwise_comparisons"][name] = test_pairwise_distribution(
                all_seeds[main_sources[i]], all_seeds[main_sources[j]], name)

    # Cross-stream PRNG comparisons
    for i in range(len(prng_seeds_list)):
        for j in range(i + 1, len(prng_seeds_list)):
            s1, s2 = prng_seeds_list[i], prng_seeds_list[j]
            name = f"PRNG_{s1}_vs_PRNG_{s2}"
            results["pairwise_comparisons"][name] = test_pairwise_distribution(
                all_seeds[f"PRNG_stream_{s1}"], all_seeds[f"PRNG_stream_{s2}"], name)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    uniform_results = {}
    for source, analysis in results["per_source"].items():
        u = analysis["uniformity"]
        ks_p = u["ks_test"]["p_value"]
        auto = analysis["autocorrelation"].get("lag_1", {}).get("autocorrelation", "N/A")
        runs_p = analysis["runs_test"].get("p_value", "N/A")
        n_biased = analysis["bit_bias"]["n_biased_bits"]
        uniform_results[source] = {
            "ks_uniform": u["ks_test"]["uniform"],
            "lag1_autocorr": auto,
            "runs_random": analysis["runs_test"].get("random", "N/A"),
            "biased_bits": n_biased,
        }
        status = "PASS" if u["ks_test"]["uniform"] else "FAIL"
        print(f"  {source}: KS uniform={status} (p={ks_p:.4f}), "
              f"autocorr={auto}, runs={'random' if analysis['runs_test'].get('random') else 'NOT random'}, "
              f"biased_bits={n_biased}/32")

    print("\nPairwise distribution differences:")
    for name, comp in results["pairwise_comparisons"].items():
        ks = comp["ks_2sample"]
        print(f"  {name}: {'DIFFERENT' if ks['different'] else 'SAME'} (KS p={ks['p_value']:.4f})")

    results["summary"] = uniform_results

    return results


def analyze_from_experiment(filepath: str) -> dict:
    """Extract and analyze seeds from an experiment JSON file."""
    with open(filepath) as f:
        data = json.load(f)

    all_seeds = {}

    if data.get("experiment_version") == "v2":
        for stream in data.get("streams", []):
            sd = stream.get("seed_distributions", {})
            for source, info in sd.items():
                if source not in all_seeds:
                    all_seeds[source] = []
                all_seeds[source].extend(info.get("seeds_32bit", []))
    else:
        st = data.get("single_turn", {})
        for prompt, sources in st.items():
            for source, sdata in sources.items():
                if source not in all_seeds:
                    all_seeds[source] = []
                for sample in sdata.get("samples", []):
                    seed = sample.get("seed")
                    if seed is not None:
                        all_seeds[source].append(int(seed) % (2**32))

    results = {
        "analysis_type": "seed_distribution_from_experiment",
        "source_file": filepath,
        "timestamp": datetime.now().isoformat(),
        "per_source": {},
        "pairwise_comparisons": {},
    }

    for source, seeds in all_seeds.items():
        if len(seeds) < 10:
            results["per_source"][source] = {"error": f"only {len(seeds)} seeds"}
            continue
        print(f"\nAnalyzing {source} ({len(seeds)} seeds from experiment)...")
        results["per_source"][source] = {
            "uniformity": test_uniformity(seeds),
            "autocorrelation": test_autocorrelation(seeds, max_lag=5),
            "runs_test": test_runs(seeds),
            "bit_bias": test_bit_bias(seeds),
        }

    sources = [s for s in all_seeds if len(all_seeds[s]) >= 10]
    for i in range(len(sources)):
        for j in range(i + 1, len(sources)):
            name = f"{sources[i]}_vs_{sources[j]}"
            results["pairwise_comparisons"][name] = test_pairwise_distribution(
                all_seeds[sources[i]], all_seeds[sources[j]], name)

    return results


def main():
    parser = argparse.ArgumentParser(description="Seed distribution analysis")
    parser.add_argument("--n", type=int, default=10000,
                        help="Number of seeds to generate per source (default: 10000)")
    parser.add_argument("--from-experiment", type=str, default=None,
                        help="Analyze seeds from an experiment JSON file")
    parser.add_argument("--prng-seeds", type=str, default="42,123,7,999,314",
                        help="PRNG stream seeds")

    args = parser.parse_args()

    if args.from_experiment:
        results = analyze_from_experiment(args.from_experiment)
        suffix = Path(args.from_experiment).stem
    else:
        prng_seeds = [int(s) for s in args.prng_seeds.split(",")]
        results = analyze_from_generators(args.n, prng_seeds)
        suffix = f"n{args.n}"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = OUTPUT_DIR / f"seed_analysis_{suffix}_{timestamp}.json"

    with open(filepath, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved: {filepath}")


if __name__ == "__main__":
    main()
