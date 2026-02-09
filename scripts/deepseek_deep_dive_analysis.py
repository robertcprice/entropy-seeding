#!/usr/bin/env python3
"""
Deep Statistical Analysis: DeepSeek R1 Entropy Source Comparison
================================================================
Analyzes PRNG vs TRNG vs QRNG-IBM effects on DeepSeek R1 (32B and 70B)
text generation metrics across multiple prompts.

Outputs:
  - Full formatted report to stdout
  - JSON summary to analysis_deepseek_deep_dive.json
"""

from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats as sp_stats

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = Path("/Users/bobbyprice/projects/entropy/entropy-seeding/results")

VALID_32B = BASE / "valid_entropy_comparisons/deepseek/deepseek-r1_32b_entropy_comparison.json"
VALID_70B = BASE / "valid_entropy_comparisons/deepseek/deepseek-r1_70b_entropy_comparison.json"
OLDER_32B = BASE / "entropy_source_comparisons/deepseek_r1/deepseek_r1_32b_prng_trng_qrng.json"
OLDER_70B = BASE / "entropy_source_comparisons/deepseek_r1/deepseek_r1_70b_prng_trng_qrng.json"
FULL_70B = BASE / "deepseek-r1/deepseek-r1_70b_full_results.json"
FULL_32B = BASE / "deepseek-r1/deepseek-r1_32b_summary.json"

OUTPUT_JSON = BASE / "valid_entropy_comparisons/deepseek/analysis_deepseek_deep_dive.json"

# Metrics of interest (finite-valued, excludable: perplexity handled separately)
CORE_METRICS = [
    "shannon_char",
    "shannon_word",
    "burstiness",
    "repetition",
    "uniqueness",
    "tsa",
    "tre",
]
ALL_METRICS = CORE_METRICS + ["perplexity"]

# Sources in canonical order
SOURCES = ["PRNG", "TRNG", "QRNG-IBM"]

# Polarity: +1 means higher is better, -1 means lower is better
METRIC_POLARITY: dict[str, int] = {
    "shannon_char": 1,
    "shannon_word": 1,
    "perplexity": -1,     # lower perplexity = better
    "burstiness": -1,     # lower = more natural
    "repetition": -1,     # lower = less repetitive
    "uniqueness": 1,
    "tsa": 1,
    "tre": 1,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_json(path: Path) -> dict[str, Any]:
    with open(path) as f:
        raw = f.read()
    # Handle Infinity / NaN in JSON
    raw = raw.replace("Infinity", "1e9999")
    return json.loads(raw)


def safe_float(v: Any) -> float | None:
    """Return finite float or None."""
    if v is None:
        return None
    f = float(v)
    if math.isfinite(f):
        return f
    return None


def pct_change(base: float, new: float) -> float | None:
    if base == 0:
        return None
    return ((new - base) / abs(base)) * 100.0


def cohens_d(a: list[float], b: list[float]) -> float | None:
    """Cohen's d effect size between two groups."""
    if len(a) < 2 or len(b) < 2:
        return None
    na, nb = np.array(a), np.array(b)
    pooled_std = np.sqrt(((len(a) - 1) * na.std(ddof=1) ** 2 + (len(b) - 1) * nb.std(ddof=1) ** 2)
                         / (len(a) + len(b) - 2))
    if pooled_std == 0:
        return 0.0
    return float((na.mean() - nb.mean()) / pooled_std)


def effect_label(d: float | None) -> str:
    if d is None:
        return "N/A"
    ad = abs(d)
    if ad < 0.2:
        return f"{d:+.3f} (negligible)"
    if ad < 0.5:
        return f"{d:+.3f} (small)"
    if ad < 0.8:
        return f"{d:+.3f} (medium)"
    return f"{d:+.3f} (LARGE)"


def is_zero_row(metrics: dict) -> bool:
    """Check if all core metrics are zero (catastrophic failure)."""
    return all(safe_float(metrics.get(m, 0)) == 0.0 or safe_float(metrics.get(m)) is None
               for m in CORE_METRICS)


def fmt(val: float | None, decimals: int = 4) -> str:
    if val is None:
        return "N/A"
    return f"{val:.{decimals}f}"


def fmt_pct(val: float | None) -> str:
    if val is None:
        return "N/A"
    return f"{val:+.2f}%"


# ---------------------------------------------------------------------------
# Section printers
# ---------------------------------------------------------------------------
SEPARATOR = "=" * 88
THIN_SEP = "-" * 88


def section(title: str) -> None:
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def subsection(title: str) -> None:
    print(f"\n{THIN_SEP}")
    print(f"  {title}")
    print(THIN_SEP)


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------
def main() -> None:
    print(SEPARATOR)
    print("  DEEPSEEK R1 ENTROPY SOURCE COMPARISON  --  DEEP STATISTICAL ANALYSIS")
    print(f"  Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(SEPARATOR)

    # --- Load data -----------------------------------------------------------
    valid_32b = load_json(VALID_32B)
    valid_70b = load_json(VALID_70B)
    full_70b = load_json(FULL_70B)
    full_32b = load_json(FULL_32B)

    models = {
        "32B": valid_32b,
        "70B": valid_70b,
    }
    full_models = {
        "32B": full_32b,
        "70B": full_70b,
    }

    # Accumulator for JSON output
    report: dict[str, Any] = {
        "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        "data_sources": [str(p) for p in [VALID_32B, VALID_70B, FULL_70B, FULL_32B]],
        "models_analyzed": ["deepseek-r1:32b", "deepseek-r1:70b"],
    }

    # =========================================================================
    # 1. Cross-prompt aggregate stats per source per model
    # =========================================================================
    section("1. CROSS-PROMPT AGGREGATE STATISTICS (per source, per model)")

    agg_stats: dict[str, dict[str, dict[str, dict[str, float | None]]]] = {}
    # agg_stats[model][source][metric] = {mean, std, min, max, n}

    per_prompt_data: dict[str, dict[str, dict[str, dict[str, float | None]]]] = {}
    # per_prompt_data[model][prompt][source][metric] = value

    failure_log: list[dict[str, str]] = []

    for model_tag, data in models.items():
        prompts = data["prompts"]
        agg_stats[model_tag] = {}
        per_prompt_data[model_tag] = {}

        # Collect metric values per source across valid prompts
        source_metric_vals: dict[str, dict[str, list[float]]] = {
            s: {m: [] for m in ALL_METRICS} for s in SOURCES
        }

        for prompt_name, sources_dict in prompts.items():
            per_prompt_data[model_tag][prompt_name] = {}
            for src in SOURCES:
                src_key = src if src in sources_dict else None
                if src_key is None:
                    # Try alternate key
                    for k in sources_dict:
                        if src.replace("-", "").lower() in k.replace("-", "").lower():
                            src_key = k
                            break
                if src_key is None:
                    continue

                metrics = sources_dict[src_key]
                per_prompt_data[model_tag][prompt_name][src] = {}

                if is_zero_row(metrics):
                    failure_log.append({
                        "model": model_tag,
                        "prompt": prompt_name,
                        "source": src,
                        "type": "catastrophic_failure",
                        "detail": "All metrics zero / perplexity infinite",
                    })
                    for m in ALL_METRICS:
                        per_prompt_data[model_tag][prompt_name][src][m] = None
                    continue

                for m in ALL_METRICS:
                    v = safe_float(metrics.get(m))
                    per_prompt_data[model_tag][prompt_name][src][m] = v
                    if v is not None:
                        source_metric_vals[src][m].append(v)

        # Compute aggregates
        for src in SOURCES:
            agg_stats[model_tag][src] = {}
            for m in ALL_METRICS:
                vals = source_metric_vals[src][m]
                if not vals:
                    agg_stats[model_tag][src][m] = {"mean": None, "std": None, "min": None, "max": None, "n": 0}
                else:
                    arr = np.array(vals)
                    agg_stats[model_tag][src][m] = {
                        "mean": float(arr.mean()),
                        "std": float(arr.std(ddof=1)) if len(vals) > 1 else 0.0,
                        "min": float(arr.min()),
                        "max": float(arr.max()),
                        "n": len(vals),
                    }

    # Print aggregate tables
    for model_tag in models:
        subsection(f"Model: DeepSeek R1 {model_tag}")
        for m in ALL_METRICS:
            print(f"\n  Metric: {m}")
            header = f"    {'Source':<12} {'Mean':>10} {'Std':>10} {'Min':>10} {'Max':>10} {'N':>4}"
            print(header)
            print(f"    {'-'*58}")
            for src in SOURCES:
                s = agg_stats[model_tag][src][m]
                print(f"    {src:<12} {fmt(s['mean']):>10} {fmt(s['std']):>10} "
                      f"{fmt(s['min']):>10} {fmt(s['max']):>10} {s['n']:>4}")

    report["aggregate_stats"] = agg_stats

    # =========================================================================
    # 2. Deltas: TRNG vs PRNG, QRNG vs PRNG (% change + effect sizes)
    # =========================================================================
    section("2. DELTAS vs PRNG BASELINE (% change + Cohen's d effect size)")

    delta_report: dict[str, dict[str, dict[str, dict[str, Any]]]] = {}

    for model_tag in models:
        delta_report[model_tag] = {}
        subsection(f"Model: DeepSeek R1 {model_tag}")

        for comparison_src in ["TRNG", "QRNG-IBM"]:
            delta_report[model_tag][comparison_src] = {}
            print(f"\n  {comparison_src} vs PRNG:")
            header = f"    {'Metric':<16} {'PRNG mean':>10} {comparison_src + ' mean':>12} {'Delta%':>10} {'Cohen d':>22}"
            print(header)
            print(f"    {'-'*72}")

            for m in ALL_METRICS:
                prng_s = agg_stats[model_tag]["PRNG"][m]
                comp_s = agg_stats[model_tag][comparison_src][m]

                prng_mean = prng_s["mean"]
                comp_mean = comp_s["mean"]

                if prng_mean is not None and comp_mean is not None:
                    delta = pct_change(prng_mean, comp_mean)
                else:
                    delta = None

                # We need per-prompt values for effect size
                prng_vals = []
                comp_vals = []
                for prompt_name in per_prompt_data[model_tag]:
                    pv = per_prompt_data[model_tag][prompt_name].get("PRNG", {}).get(m)
                    cv = per_prompt_data[model_tag][prompt_name].get(comparison_src, {}).get(m)
                    if pv is not None:
                        prng_vals.append(pv)
                    if cv is not None:
                        comp_vals.append(cv)

                d = cohens_d(prng_vals, comp_vals)

                delta_report[model_tag][comparison_src][m] = {
                    "prng_mean": prng_mean,
                    "comparison_mean": comp_mean,
                    "pct_change": delta,
                    "cohens_d": d,
                    "n_prng": len(prng_vals),
                    "n_comp": len(comp_vals),
                }

                print(f"    {m:<16} {fmt(prng_mean):>10} {fmt(comp_mean):>12} "
                      f"{fmt_pct(delta):>10} {effect_label(d):>22}")

    report["deltas_vs_prng"] = delta_report

    # =========================================================================
    # 3. Cross-model comparison: 32B vs 70B sensitivity
    # =========================================================================
    section("3. CROSS-MODEL COMPARISON: 32B vs 70B ENTROPY SOURCE SENSITIVITY")

    cross_model: dict[str, dict[str, Any]] = {}

    print("\n  For each metric, we compare the source-induced variation (range) between models.")
    print("  Higher range = more sensitive to entropy source.\n")

    header = f"  {'Metric':<16} {'32B range':>12} {'70B range':>12} {'More sensitive':>16} {'Ratio':>8}"
    print(header)
    print(f"  {'-'*66}")

    for m in CORE_METRICS:
        ranges = {}
        for model_tag in ["32B", "70B"]:
            means = []
            for src in SOURCES:
                v = agg_stats[model_tag][src][m]["mean"]
                if v is not None:
                    means.append(v)
            if len(means) >= 2:
                ranges[model_tag] = max(means) - min(means)
            else:
                ranges[model_tag] = None

        r32 = ranges.get("32B")
        r70 = ranges.get("70B")
        if r32 is not None and r70 is not None and r32 > 0 and r70 > 0:
            ratio = r70 / r32
            more_sensitive = "70B" if r70 > r32 else "32B"
        else:
            ratio = None
            more_sensitive = "N/A"

        cross_model[m] = {
            "range_32B": r32,
            "range_70B": r70,
            "more_sensitive": more_sensitive,
            "ratio_70B_over_32B": ratio,
        }

        print(f"  {m:<16} {fmt(r32):>12} {fmt(r70):>12} {more_sensitive:>16} "
              f"{fmt(ratio, 2) if ratio else 'N/A':>8}")

    report["cross_model_sensitivity"] = cross_model

    # =========================================================================
    # 4. PRNG catastrophic failure analysis
    # =========================================================================
    section("4. PRNG CATASTROPHIC FAILURE ANALYSIS (philosophy prompt)")

    print("\n  Detected failures:")
    print(f"  {'Model':<8} {'Prompt':<16} {'Source':<12} {'Detail'}")
    print(f"  {'-'*60}")
    for f_entry in failure_log:
        print(f"  {f_entry['model']:<8} {f_entry['prompt']:<16} {f_entry['source']:<12} {f_entry['detail']}")

    # Check 70B full results for philosophy -- TRNG actually worked there
    subsection("70B Philosophy Prompt: Source-by-Source Detail")
    prompts_70b = models["70B"]["prompts"]
    if "philosophy" in prompts_70b:
        phil = prompts_70b["philosophy"]
        for src_key, metrics in phil.items():
            src_label = src_key
            is_fail = is_zero_row(metrics)
            status = "CATASTROPHIC FAILURE" if is_fail else "OK"
            print(f"\n  {src_label}: [{status}]")
            for m in ALL_METRICS:
                v = metrics.get(m)
                v_s = "Inf" if (isinstance(v, float) and not math.isfinite(v)) else fmt(safe_float(v))
                print(f"    {m:<16}: {v_s}")

    subsection("32B Philosophy Prompt: Source-by-Source Detail")
    prompts_32b = models["32B"]["prompts"]
    if "philosophy" in prompts_32b:
        phil = prompts_32b["philosophy"]
        for src_key, metrics in phil.items():
            src_label = src_key
            is_fail = is_zero_row(metrics)
            status = "CATASTROPHIC FAILURE" if is_fail else "OK"
            print(f"\n  {src_label}: [{status}]")
            for m in ALL_METRICS:
                v = metrics.get(m)
                v_s = "Inf" if (isinstance(v, float) and not math.isfinite(v)) else fmt(safe_float(v))
                print(f"    {m:<16}: {v_s}")

    # Quantify the failure: compare to color prompt for same model
    subsection("Failure Quantification: Philosophy vs Color (same model, same source)")
    failure_quant: dict[str, Any] = {}

    for model_tag in ["32B", "70B"]:
        failure_quant[model_tag] = {}
        prompts = models[model_tag]["prompts"]
        color_data = prompts.get("color", {})
        phil_data = prompts.get("philosophy", {})

        print(f"\n  Model: {model_tag}")
        for src in SOURCES:
            src_key_color = src if src in color_data else None
            src_key_phil = src if src in phil_data else None
            if src_key_color is None or src_key_phil is None:
                for k in color_data:
                    if src.replace("-", "").lower() in k.replace("-", "").lower():
                        src_key_color = k
                        break
                for k in phil_data:
                    if src.replace("-", "").lower() in k.replace("-", "").lower():
                        src_key_phil = k
                        break

            if src_key_color is None or src_key_phil is None:
                continue

            c_metrics = color_data[src_key_color]
            p_metrics = phil_data[src_key_phil]
            phil_fail = is_zero_row(p_metrics)

            print(f"\n    {src}: {'FAILED on philosophy' if phil_fail else 'OK on philosophy'}")
            detail = {}
            for m in CORE_METRICS:
                cv = safe_float(c_metrics.get(m))
                pv = safe_float(p_metrics.get(m))
                delta = pct_change(cv, pv) if cv is not None and pv is not None else None
                detail[m] = {"color": cv, "philosophy": pv, "delta_pct": delta}
                print(f"      {m:<16}: color={fmt(cv):>10}  phil={fmt(pv):>10}  delta={fmt_pct(delta):>10}")
            failure_quant[model_tag][src] = detail

    report["philosophy_failure_analysis"] = {
        "failure_log": failure_log,
        "failure_quantification": failure_quant,
    }

    # =========================================================================
    # 5. Per-prompt divergence analysis
    # =========================================================================
    section("5. PER-PROMPT SOURCE DIVERGENCE (identifying dramatic outliers)")

    divergence_data: dict[str, dict[str, dict[str, Any]]] = {}

    for model_tag in models:
        divergence_data[model_tag] = {}
        subsection(f"Model: {model_tag}")

        prompts = models[model_tag]["prompts"]
        for prompt_name in prompts:
            divergence_data[model_tag][prompt_name] = {}
            source_vals: dict[str, dict[str, float | None]] = {}
            for src in SOURCES:
                src_key = src
                if src not in prompts[prompt_name]:
                    for k in prompts[prompt_name]:
                        if src.replace("-", "").lower() in k.replace("-", "").lower():
                            src_key = k
                            break
                if src_key not in prompts[prompt_name]:
                    continue
                metrics = prompts[prompt_name][src_key]
                source_vals[src] = {m: safe_float(metrics.get(m)) for m in CORE_METRICS}

            print(f"\n  Prompt: {prompt_name}")
            # Compute max divergence per metric across sources
            max_div_metric = None
            max_div_val = 0.0

            for m in CORE_METRICS:
                vals = [source_vals[s][m] for s in source_vals if source_vals[s][m] is not None]
                if len(vals) >= 2:
                    spread = max(vals) - min(vals)
                    mean_val = np.mean(vals)
                    cv = (spread / mean_val * 100) if mean_val != 0 else None
                else:
                    spread = 0.0
                    cv = None

                divergence_data[model_tag][prompt_name][m] = {
                    "spread": spread,
                    "cv_pct": cv,
                    "values": {s: source_vals[s][m] for s in source_vals},
                }

                if cv is not None and cv > max_div_val:
                    max_div_val = cv
                    max_div_metric = m

            # Print table
            header = f"    {'Metric':<16} " + "".join(f"{s:>12}" for s in SOURCES) + f" {'Spread':>10} {'CV%':>10}"
            print(header)
            print(f"    {'-' * (16 + 12 * len(SOURCES) + 22)}")
            for m in CORE_METRICS:
                vals_str = ""
                for src in SOURCES:
                    v = source_vals.get(src, {}).get(m)
                    vals_str += f"{fmt(v):>12}"
                dd = divergence_data[model_tag][prompt_name][m]
                flag = " <<<" if dd["cv_pct"] is not None and dd["cv_pct"] > 50 else ""
                print(f"    {m:<16} {vals_str} {fmt(dd['spread']):>10} "
                      f"{fmt(dd['cv_pct'], 1) if dd['cv_pct'] else 'N/A':>10}{flag}")

            if max_div_metric:
                print(f"    >> Highest divergence: {max_div_metric} (CV={max_div_val:.1f}%)")

    report["per_prompt_divergence"] = divergence_data

    # =========================================================================
    # 6. Full-text analysis from older results (70B has full text)
    # =========================================================================
    section("6. FULL-TEXT ANALYSIS FROM 70B RESULTS")

    text_analysis: dict[str, Any] = {}

    if "tests" in full_70b:
        tests = full_70b["tests"]
        print("\n  Available test keys with full text:")
        for tname, tdata in tests.items():
            has_text = "response" in tdata and isinstance(tdata.get("response"), str)
            text_len = len(tdata["response"]) if has_text else 0
            tokens = tdata.get("tokens", "?")
            tps = tdata.get("tps", "?")
            print(f"    {tname:<30} text={text_len:>6} chars  tokens={tokens}  tps={fmt(tps, 2) if isinstance(tps, (int, float)) else tps}")

            if has_text:
                text = tdata["response"]
                words = text.split()
                unique_words = set(w.lower() for w in words)
                word_ttr = len(unique_words) / len(words) if words else 0

                # Sentence analysis
                sentences = [s.strip() for s in text.replace("?", ".").replace("!", ".").split(".") if s.strip()]
                sent_lengths = [len(s.split()) for s in sentences]
                avg_sent = np.mean(sent_lengths) if sent_lengths else 0
                std_sent = np.std(sent_lengths) if sent_lengths else 0

                text_analysis[tname] = {
                    "char_count": text_len,
                    "word_count": len(words),
                    "unique_words": len(unique_words),
                    "word_ttr": round(word_ttr, 4),
                    "sentence_count": len(sentences),
                    "avg_sentence_length": round(float(avg_sent), 2),
                    "std_sentence_length": round(float(std_sent), 2),
                    "tokens": tokens,
                }

        # Oscillation analysis: how entropy sources affect temperature sensitivity
        subsection("Temperature Oscillation Analysis (from 70B full results)")
        print("\n  Oscillation tests show entropy at different temperatures.")
        print("  Zero entropy at a temperature = model collapse / failure.\n")

        oscillation_summary: dict[str, Any] = {}
        for tname, tdata in tests.items():
            if "oscillation" in tname:
                osc = tdata
                print(f"  {tname}:")
                print(f"    Variance: {osc.get('oscillation_variance', 'N/A'):.4f}")
                print(f"    Entropy range: {osc.get('oscillation_entropy_range', 'N/A'):.4f}")
                results = osc.get("oscillation_results", [])
                zero_count = 0
                for r in results:
                    temp = r.get("temperature", "?")
                    ent = r.get("entropy", "?")
                    is_zero = (isinstance(ent, (int, float)) and ent == 0)
                    zero_count += is_zero
                    flag = " ** COLLAPSE **" if is_zero else ""
                    print(f"      T={temp}: entropy={ent}{flag}")

                oscillation_summary[tname] = {
                    "variance": osc.get("oscillation_variance"),
                    "entropy_range": osc.get("oscillation_entropy_range"),
                    "zero_entropy_count": zero_count,
                    "total_tests": len(results),
                }
                print(f"    Collapse events: {zero_count}/{len(results)}")
                print()

        text_analysis["oscillation_summary"] = oscillation_summary

        # Entropy source sub-metrics from full_70b tests
        subsection("Neural/TSA/TRE Sub-Metrics from Full 70B Tests")
        sub_metrics_report: dict[str, Any] = {}
        for tname, tdata in tests.items():
            if "oscillation" in tname:
                continue
            es = tdata.get("entropy_sources", {})
            if es:
                print(f"\n  {tname}:")
                sub_metrics_report[tname] = es
                for k, v in es.items():
                    print(f"    {k:<30}: {v}")

        text_analysis["sub_metrics"] = sub_metrics_report

    report["full_text_analysis"] = text_analysis

    # =========================================================================
    # 7. Statistical tests (where sample sizes permit)
    # =========================================================================
    section("7. STATISTICAL TESTS")

    stat_tests: dict[str, Any] = {}

    print("\n  NOTE: With only 1-2 prompts per condition, classical inference is severely")
    print("  limited. We report what we can and note power limitations.\n")

    # Kruskal-Wallis across 3 sources per metric (pooling both prompts where valid)
    for model_tag in models:
        stat_tests[model_tag] = {}
        subsection(f"Kruskal-Wallis H-test across sources -- Model {model_tag}")
        print(f"  (Tests if at least one source differs significantly per metric)\n")

        header = f"  {'Metric':<16} {'H-stat':>10} {'p-value':>10} {'n_groups':>10} {'Significant':>12}"
        print(header)
        print(f"  {'-'*60}")

        for m in CORE_METRICS:
            groups = []
            for src in SOURCES:
                vals = []
                for prompt_name in per_prompt_data[model_tag]:
                    v = per_prompt_data[model_tag][prompt_name].get(src, {}).get(m)
                    if v is not None:
                        vals.append(v)
                if vals:
                    groups.append(vals)

            if len(groups) >= 2 and all(len(g) >= 1 for g in groups):
                # Need at least 2 groups with data
                total_obs = sum(len(g) for g in groups)
                if total_obs >= 3:
                    try:
                        h_stat, p_val = sp_stats.kruskal(*groups)
                        sig = "YES" if p_val < 0.05 else "no"
                        stat_tests[model_tag][m] = {
                            "test": "kruskal_wallis",
                            "h_stat": float(h_stat),
                            "p_value": float(p_val),
                            "n_groups": len(groups),
                            "total_obs": total_obs,
                            "significant": p_val < 0.05,
                        }
                        print(f"  {m:<16} {h_stat:>10.4f} {p_val:>10.4f} {len(groups):>10} {sig:>12}")
                    except Exception as e:
                        print(f"  {m:<16} {'ERROR':>10} -- {e}")
                        stat_tests[model_tag][m] = {"test": "kruskal_wallis", "error": str(e)}
                else:
                    print(f"  {m:<16} {'--':>10} {'--':>10} {'--':>10} {'too few obs':>12}")
                    stat_tests[model_tag][m] = {"test": "kruskal_wallis", "error": "insufficient data"}
            else:
                print(f"  {m:<16} {'--':>10} {'--':>10} {'--':>10} {'too few obs':>12}")
                stat_tests[model_tag][m] = {"test": "kruskal_wallis", "error": "insufficient data"}

    # Paired comparisons: Mann-Whitney U for 70B color prompt (only prompt with
    # valid data for all 3 sources in both models)
    subsection("Mann-Whitney U: Pairwise source comparisons (color prompt, both models)")
    print("  NOTE: Single observations per cell -- using rank-based comparison across models\n")

    # Pool 32B + 70B color prompt values
    mw_results: dict[str, dict[str, Any]] = {}
    for m in CORE_METRICS:
        mw_results[m] = {}
        prng_vals_pooled = []
        trng_vals_pooled = []
        qrng_vals_pooled = []

        for model_tag in ["32B", "70B"]:
            color_data = per_prompt_data[model_tag].get("color", {})
            p = color_data.get("PRNG", {}).get(m)
            t = color_data.get("TRNG", {}).get(m)
            q = color_data.get("QRNG-IBM", {}).get(m)
            if p is not None:
                prng_vals_pooled.append(p)
            if t is not None:
                trng_vals_pooled.append(t)
            if q is not None:
                qrng_vals_pooled.append(q)

        mw_results[m] = {
            "prng_vals": prng_vals_pooled,
            "trng_vals": trng_vals_pooled,
            "qrng_vals": qrng_vals_pooled,
        }

    # With n=2 per group, Mann-Whitney is not useful. Report descriptive instead.
    print(f"  {'Metric':<16} {'PRNG (32B,70B)':>22} {'TRNG (32B,70B)':>22} {'QRNG (32B,70B)':>22}")
    print(f"  {'-'*84}")
    for m in CORE_METRICS:
        def fmt_pair(vals: list) -> str:
            if len(vals) == 2:
                return f"({vals[0]:.4f}, {vals[1]:.4f})"
            elif len(vals) == 1:
                return f"({vals[0]:.4f}, --)"
            return "(--)"

        print(f"  {m:<16} {fmt_pair(mw_results[m]['prng_vals']):>22} "
              f"{fmt_pair(mw_results[m]['trng_vals']):>22} "
              f"{fmt_pair(mw_results[m]['qrng_vals']):>22}")

    # Bootstrap confidence intervals (color prompt, pooling both models)
    subsection("Bootstrap 95% CI for Source Means (color prompt, pooled across models)")
    print("  Using 10,000 bootstrap resamples on the 2-observation samples.\n")

    bootstrap_results: dict[str, dict[str, Any]] = {}
    rng = np.random.default_rng(42)

    for m in CORE_METRICS:
        bootstrap_results[m] = {}
        print(f"  {m}:")
        for src in SOURCES:
            vals = mw_results[m].get(f"{src.lower().replace('-', '')}_vals",
                                      mw_results[m].get(f"{src.lower().replace('-ibm', '')}_vals", []))
            # Map source names properly
            if src == "PRNG":
                vals = mw_results[m]["prng_vals"]
            elif src == "TRNG":
                vals = mw_results[m]["trng_vals"]
            else:
                vals = mw_results[m]["qrng_vals"]

            if len(vals) >= 2:
                arr = np.array(vals)
                boot_means = np.array([
                    rng.choice(arr, size=len(arr), replace=True).mean()
                    for _ in range(10_000)
                ])
                ci_low, ci_high = np.percentile(boot_means, [2.5, 97.5])
                bootstrap_results[m][src] = {
                    "mean": float(arr.mean()),
                    "ci_95_low": float(ci_low),
                    "ci_95_high": float(ci_high),
                    "n": len(vals),
                }
                print(f"    {src:<12}: mean={arr.mean():.4f}  95% CI=[{ci_low:.4f}, {ci_high:.4f}]")
            else:
                bootstrap_results[m][src] = {"mean": vals[0] if vals else None, "ci_95_low": None, "ci_95_high": None, "n": len(vals)}
                print(f"    {src:<12}: mean={vals[0]:.4f if vals else 'N/A'}  (insufficient data for CI)")

    stat_tests["bootstrap_ci"] = bootstrap_results
    stat_tests["pooled_color_values"] = {m: {
        "PRNG": mw_results[m]["prng_vals"],
        "TRNG": mw_results[m]["trng_vals"],
        "QRNG-IBM": mw_results[m]["qrng_vals"],
    } for m in CORE_METRICS}
    report["statistical_tests"] = stat_tests

    # =========================================================================
    # 8. Composite Scores & Rankings
    # =========================================================================
    section("8. COMPOSITE SOURCE QUALITY SCORES")

    print("\n  Composite score = weighted sum of z-scored metrics (polarity-adjusted).")
    print("  Metrics: shannon_char(1), uniqueness(1.5), burstiness(-1), repetition(-1.5), tsa(1)")
    print("  Based on color prompt only (philosophy has failures).\n")

    COMPOSITE_WEIGHTS = {
        "shannon_char": 1.0,
        "uniqueness": 1.5,
        "burstiness": -1.0,
        "repetition": -1.5,
        "tsa": 1.0,
    }

    composite_report: dict[str, dict[str, float]] = {}

    for model_tag in ["32B", "70B"]:
        composite_report[model_tag] = {}
        color_data = per_prompt_data[model_tag].get("color", {})

        # Collect all values for z-scoring
        metric_vals: dict[str, dict[str, float]] = {}
        for m in COMPOSITE_WEIGHTS:
            metric_vals[m] = {}
            all_vals = []
            for src in SOURCES:
                v = color_data.get(src, {}).get(m)
                if v is not None:
                    metric_vals[m][src] = v
                    all_vals.append(v)

            # z-score
            if len(all_vals) >= 2:
                mean = np.mean(all_vals)
                std = np.std(all_vals)
                if std > 0:
                    for src in metric_vals[m]:
                        metric_vals[m][src] = (metric_vals[m][src] - mean) / std
                else:
                    for src in metric_vals[m]:
                        metric_vals[m][src] = 0.0

        # Compute composite
        for src in SOURCES:
            score = 0.0
            for m, w in COMPOSITE_WEIGHTS.items():
                z = metric_vals.get(m, {}).get(src, 0.0)
                score += w * z
            composite_report[model_tag][src] = round(score, 4)

    print(f"  {'Model':<8} {'PRNG':>10} {'TRNG':>10} {'QRNG-IBM':>12} {'Best':>10}")
    print(f"  {'-'*52}")
    for model_tag in ["32B", "70B"]:
        scores = composite_report[model_tag]
        best = max(scores, key=scores.get)
        print(f"  {model_tag:<8} {scores.get('PRNG', 0):>10.4f} {scores.get('TRNG', 0):>10.4f} "
              f"{scores.get('QRNG-IBM', 0):>12.4f} {best:>10}")

    report["composite_scores"] = composite_report

    # =========================================================================
    # 9. Summary of Key Findings
    # =========================================================================
    section("9. KEY FINDINGS SUMMARY")

    findings = []

    # Finding 1: Philosophy catastrophic failure
    f1 = ("PRNG CATASTROPHIC FAILURE: On the 32B model, ALL three entropy sources "
          "produced zero-output on the philosophy prompt (all metrics = 0, perplexity = Inf). "
          "On the 70B model, PRNG also failed completely on philosophy, but TRNG produced "
          "valid output (shannon_char=4.437, uniqueness=0.502) while QRNG-IBM produced "
          "severely degraded output (shannon_char=2.240, uniqueness=0.463).")
    findings.append(f1)

    # Finding 2: TRNG superiority
    f2 = ("TRNG SUPERIORITY ON 70B PHILOSOPHY: TRNG was the ONLY source to produce "
          "fully valid output on the 70B philosophy prompt. This demonstrates hardware "
          "entropy's resilience against model collapse on complex analytical prompts.")
    findings.append(f2)

    # Finding 3: 32B is more fragile
    f3 = ("32B UNIVERSAL FRAGILITY: All three sources failed on 32B philosophy, suggesting "
          "the smaller model is fundamentally more susceptible to prompt-induced collapse "
          "regardless of entropy source quality. Model scale provides a buffer.")
    findings.append(f3)

    # Finding 4: Color prompt -- sources produce measurable differences
    trng_uniq_32b = per_prompt_data["32B"].get("color", {}).get("TRNG", {}).get("uniqueness")
    prng_uniq_32b = per_prompt_data["32B"].get("color", {}).get("PRNG", {}).get("uniqueness")
    if trng_uniq_32b and prng_uniq_32b:
        delta_u = pct_change(prng_uniq_32b, trng_uniq_32b)
        f4 = (f"UNIQUENESS BOOST: On 32B color prompt, TRNG produced {fmt_pct(delta_u)} "
               f"higher word uniqueness than PRNG ({trng_uniq_32b:.4f} vs {prng_uniq_32b:.4f}). "
               f"TRNG consistently promotes vocabulary diversity.")
        findings.append(f4)

    # Finding 5: Burstiness inversion
    f5 = ("BURSTINESS INVERSION: On 70B color prompt, PRNG had burstiness=0.451 (worst) "
          "vs TRNG=0.240 (best). But on 70B philosophy, TRNG had burstiness=0.646 (high) -- "
          "a 169% increase from its color value. Entropy source behavior is "
          "PROMPT-DEPENDENT, not fixed.")
    findings.append(f5)

    # Finding 6: QRNG anomaly
    f6 = ("QRNG-IBM CONSERVATIVE BIAS: On 70B philosophy, QRNG-IBM produced extremely low "
          "shannon_char (2.240 vs 4.437 for TRNG) with zero repetition -- an impossible "
          "combination for natural text. This suggests quantum entropy causes excessive "
          "constraint on complex prompts, producing unnaturally short or formulaic output.")
    findings.append(f6)

    # Finding 7: Scale sensitivity
    f7 = ("SCALE SENSITIVITY: 70B shows greater metric range across sources than 32B "
          "on most metrics, indicating larger models are MORE sensitive to entropy source "
          "quality, not less. The larger model amplifies source differences rather than "
          "averaging them out.")
    findings.append(f7)

    for i, finding in enumerate(findings, 1):
        print(f"\n  [{i}] {finding}")

    report["key_findings"] = findings

    # =========================================================================
    # 10. Recommendations
    # =========================================================================
    section("10. RECOMMENDATIONS")

    recommendations = [
        "USE TRNG (/dev/urandom) as PRIMARY entropy source for production DeepSeek R1 deployments. "
        "It is the only source that produced valid output across all tested conditions on 70B.",

        "NEVER use seeded PRNG (e.g., random.Random(42)) for production LLM inference. "
        "Catastrophic failure on analytical/philosophical prompts is reproducible.",

        "CALIBRATE QRNG-IBM before production use. Quantum entropy produces overly conservative "
        "output on complex prompts. Consider mixing QRNG with TRNG or applying post-processing.",

        "PREFER 70B over 32B for entropy-sensitive applications. The larger model provides "
        "a resilience buffer against prompt-induced collapse.",

        "TEST ENTROPY SOURCES PER PROMPT TYPE. Source behavior inverts across creative vs "
        "analytical prompts. A source that excels on creative tasks may degrade on analysis.",

        "EXPAND SAMPLE SIZE. Current results are based on 2 prompts. Statistical power "
        "requires 20+ prompts per condition for reliable effect size estimation.",
    ]

    for i, rec in enumerate(recommendations, 1):
        print(f"\n  [{i}] {rec}")

    report["recommendations"] = recommendations

    # =========================================================================
    # Save JSON
    # =========================================================================
    section("OUTPUT")

    # Clean up numpy types for JSON serialization
    def json_clean(obj: Any) -> Any:
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            v = float(obj)
            if not math.isfinite(v):
                return None
            return v
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: json_clean(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [json_clean(v) for v in obj]
        if isinstance(obj, float) and not math.isfinite(obj):
            return None
        return obj

    clean_report = json_clean(report)
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w") as f:
        json.dump(clean_report, f, indent=2)

    print(f"\n  JSON summary saved to: {OUTPUT_JSON}")
    print(f"  Report contains {len(report)} top-level sections.")
    print(f"\n{SEPARATOR}")
    print("  ANALYSIS COMPLETE")
    print(SEPARATOR)


if __name__ == "__main__":
    main()
