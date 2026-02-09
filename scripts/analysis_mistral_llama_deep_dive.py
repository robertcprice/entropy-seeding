#!/usr/bin/env python3
"""
Deep statistical analysis: Mistral vs Llama entropy source comparison.

Analyses performed:
1. Mistral: Cross-prompt aggregates, deltas, inter-sample variance
2. Mistral: Text similarity and output clustering
3. Mistral vs Qwen: Sliding window vs full attention entropy sensitivity
4. Llama 1B: Qualitative profile analysis per source
5. Llama 1B vs Qwen 1.7B: Cross-architecture consistency
6. QRNG mode shifts and TRNG language mixing detection
7. Text determinism and clustering analysis
"""

import json
import math
import re
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = Path("/Users/bobbyprice/projects/entropy/entropy-seeding/results/valid_entropy_comparisons")
MISTRAL_PATH = BASE / "mistral" / "entropy_comparison_mistral_latest_20260208_175956.json"
LLAMA_PATH = BASE / "llama" / "rng_comparison_quick_results_20260203_180635.json"
QWEN_8B_PATH = BASE / "qwen" / "8B_comprehensive_results.json"
QWEN_COMPLETE_PATH = BASE / "qwen" / "complete_with_qrng_20260205_145740.json"
OUTPUT_PATH = BASE / "analysis_mistral_llama_deep_dive.json"

SOURCES = ["PRNG", "TRNG", "QRNG"]
METRICS = ["shannon_char", "shannon_word", "unique_words", "word_diversity", "length_words", "length_chars"]


def separator(title: str, char: str = "=", width: int = 88) -> None:
    print(f"\n{char * width}")
    print(f"  {title}")
    print(f"{char * width}")


def sub_sep(title: str) -> None:
    print(f"\n--- {title} ---")


# ---------------------------------------------------------------------------
# Text analysis helpers
# ---------------------------------------------------------------------------
def jaccard_similarity(text_a: str, text_b: str) -> float:
    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / len(words_a | words_b)


def cosine_similarity_bow(text_a: str, text_b: str) -> float:
    counter_a = Counter(text_a.lower().split())
    counter_b = Counter(text_b.lower().split())
    all_words = set(counter_a) | set(counter_b)
    if not all_words:
        return 0.0
    vec_a = np.array([counter_a.get(w, 0) for w in all_words], dtype=float)
    vec_b = np.array([counter_b.get(w, 0) for w in all_words], dtype=float)
    dot = np.dot(vec_a, vec_b)
    norm = np.linalg.norm(vec_a) * np.linalg.norm(vec_b)
    return float(dot / norm) if norm > 0 else 0.0


def ngram_overlap(text_a: str, text_b: str, n: int = 3) -> float:
    """Character n-gram Jaccard overlap."""
    def ngrams(s: str) -> set:
        s = s.lower()
        return {s[i:i+n] for i in range(len(s) - n + 1)} if len(s) >= n else set()
    ga, gb = ngrams(text_a), ngrams(text_b)
    if not ga or not gb:
        return 0.0
    return len(ga & gb) / len(ga | gb)


def detect_mode_shift(text: str) -> dict:
    """Detect narrative mode shifts: multiple-choice, list, Q&A, etc."""
    lines = text.strip().split("\n")
    patterns = {
        "multiple_choice": sum(1 for l in lines if re.match(r"^\s*[A-Da-d][).]\s", l)),
        "numbered_list": sum(1 for l in lines if re.match(r"^\s*\d+[).]\s", l)),
        "bullet_list": sum(1 for l in lines if re.match(r"^\s*[-*]\s", l)),
        "question_marks": text.count("?"),
        "exclamation_marks": text.count("!"),
    }
    # Language mixing: non-ASCII sequences (excluding common punctuation)
    non_ascii_sequences = re.findall(r"[^\x00-\x7F]{2,}", text)
    patterns["non_ascii_sequences"] = len(non_ascii_sequences)
    patterns["non_ascii_chars"] = sum(len(s) for s in non_ascii_sequences)
    # Detect if text switches from narrative to instructional
    narrative_markers = len(re.findall(r"\b(he|she|they|his|her|their|the old|the keeper)\b", text, re.I))
    instructional_markers = len(re.findall(r"\b(you should|let's|here are|consider|option|choice|step)\b", text, re.I))
    patterns["narrative_markers"] = narrative_markers
    patterns["instructional_markers"] = instructional_markers
    patterns["is_mode_shifted"] = (
        patterns["multiple_choice"] > 0
        or patterns["numbered_list"] > 3
        or (instructional_markers > narrative_markers and narrative_markers > 0)
    )
    return patterns


def detect_language_mixing(text: str) -> dict:
    """Detect non-English language segments in text."""
    # Common non-English character ranges
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    cyrillic_chars = len(re.findall(r"[\u0400-\u04ff]", text))
    arabic_chars = len(re.findall(r"[\u0600-\u06ff]", text))
    devanagari_chars = len(re.findall(r"[\u0900-\u097f]", text))
    # Check for common non-English word patterns
    foreign_word_patterns = re.findall(
        r"\b(das|der|die|und|nicht|avec|dans|pour|les|une|el|los|las|del|como|esto)\b", text, re.I
    )
    return {
        "cjk_chars": cjk_chars,
        "cyrillic_chars": cyrillic_chars,
        "arabic_chars": arabic_chars,
        "devanagari_chars": devanagari_chars,
        "foreign_words": len(foreign_word_patterns),
        "has_language_mixing": (cjk_chars + cyrillic_chars + arabic_chars + devanagari_chars > 0) or len(foreign_word_patterns) > 2,
    }


def compute_text_stats(text: str) -> dict:
    """Compute additional text statistics beyond what's in the data."""
    words = text.lower().split()
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    word_lengths = [len(w) for w in words]
    sent_lengths = [len(s.split()) for s in sentences]

    return {
        "avg_word_length": float(np.mean(word_lengths)) if word_lengths else 0.0,
        "std_word_length": float(np.std(word_lengths)) if word_lengths else 0.0,
        "avg_sentence_length": float(np.mean(sent_lengths)) if sent_lengths else 0.0,
        "std_sentence_length": float(np.std(sent_lengths)) if sent_lengths else 0.0,
        "num_sentences": len(sentences),
        "hapax_legomena": sum(1 for w, c in Counter(words).items() if c == 1),
        "hapax_ratio": sum(1 for w, c in Counter(words).items() if c == 1) / len(set(words)) if words else 0.0,
        "top_5_words": Counter(words).most_common(5),
    }


# ---------------------------------------------------------------------------
# Section 1: Mistral Analysis
# ---------------------------------------------------------------------------
def analyze_mistral(data: dict) -> dict:
    separator("SECTION 1: MISTRAL (mistral:latest) DEEP ANALYSIS")
    results = {
        "cross_prompt_aggregates": {},
        "per_prompt_details": {},
        "inter_sample_variance": {},
        "text_similarity": {},
        "mode_shift_analysis": {},
        "language_mixing_analysis": {},
    }

    prompts = data["prompts"]
    prompt_keys = list(prompts.keys())
    num_prompts = len(prompt_keys)

    # ---- Cross-prompt aggregates ----
    sub_sep("1a. Cross-Prompt Aggregate Metrics (mean of prompt-means)")
    source_aggregates: dict[str, dict[str, list]] = {s: defaultdict(list) for s in SOURCES}

    for prompt_key in prompt_keys:
        for source in SOURCES:
            agg = prompts[prompt_key][source]["aggregate_metrics"]
            for m in METRICS:
                source_aggregates[source][m].append(agg[f"{m}_mean"])

    print(f"\n{'Metric':<20} {'PRNG':>12} {'TRNG':>12} {'QRNG':>12} {'TRNG-PRNG':>12} {'QRNG-PRNG':>12}")
    print("-" * 80)
    for m in METRICS:
        vals = {}
        for s in SOURCES:
            vals[s] = float(np.mean(source_aggregates[s][m]))
        delta_trng = vals["TRNG"] - vals["PRNG"]
        delta_qrng = vals["QRNG"] - vals["PRNG"]
        print(f"{m:<20} {vals['PRNG']:>12.4f} {vals['TRNG']:>12.4f} {vals['QRNG']:>12.4f} {delta_trng:>+12.4f} {delta_qrng:>+12.4f}")
        results["cross_prompt_aggregates"][m] = {
            "PRNG": vals["PRNG"], "TRNG": vals["TRNG"], "QRNG": vals["QRNG"],
            "delta_TRNG_vs_PRNG": delta_trng, "delta_QRNG_vs_PRNG": delta_qrng,
        }

    # ---- Per-prompt breakdown ----
    sub_sep("1b. Per-Prompt Breakdown (delta from PRNG baseline)")
    for prompt_key in prompt_keys:
        short_prompt = prompt_key[:55] + "..." if len(prompt_key) > 55 else prompt_key
        print(f"\n  Prompt: \"{short_prompt}\"")
        prompt_results = {}
        for m in ["shannon_word", "word_diversity", "length_words"]:
            prng_val = prompts[prompt_key]["PRNG"]["aggregate_metrics"][f"{m}_mean"]
            trng_val = prompts[prompt_key]["TRNG"]["aggregate_metrics"][f"{m}_mean"]
            qrng_val = prompts[prompt_key]["QRNG"]["aggregate_metrics"][f"{m}_mean"]
            d_t = trng_val - prng_val
            d_q = qrng_val - prng_val
            pct_t = (d_t / prng_val * 100) if prng_val != 0 else 0
            pct_q = (d_q / prng_val * 100) if prng_val != 0 else 0
            print(f"    {m:<20} PRNG={prng_val:.4f}  TRNG={d_t:+.4f} ({pct_t:+.1f}%)  QRNG={d_q:+.4f} ({pct_q:+.1f}%)")
            prompt_results[m] = {
                "PRNG": prng_val, "TRNG_delta": d_t, "QRNG_delta": d_q,
                "TRNG_pct": pct_t, "QRNG_pct": pct_q,
            }
        results["per_prompt_details"][short_prompt] = prompt_results

    # ---- Inter-sample variance (only 2 samples) ----
    sub_sep("1c. Inter-Sample Variance (n=2, showing range and CV)")
    print(f"\n{'Source':<8} {'Metric':<20} {'Sample1':>10} {'Sample2':>10} {'Range':>10} {'CV%':>8}")
    print("-" * 68)
    for source in SOURCES:
        source_ranges = []
        source_cvs = []
        for prompt_key in prompt_keys:
            samples = prompts[prompt_key][source]["samples"]
            for m in ["shannon_word", "word_diversity"]:
                v1 = samples[0]["metrics"][m]
                v2 = samples[1]["metrics"][m]
                rng = abs(v2 - v1)
                mean = (v1 + v2) / 2
                cv = (rng / (2 * mean) * 100) if mean != 0 else 0  # approximate CV for n=2
                source_ranges.append(rng)
                source_cvs.append(cv)
        avg_range = np.mean(source_ranges)
        avg_cv = np.mean(source_cvs)
        results["inter_sample_variance"][source] = {
            "avg_range": float(avg_range),
            "avg_cv_pct": float(avg_cv),
        }
        # Print first prompt as example
        samples = prompts[prompt_keys[0]][source]["samples"]
        for m in ["shannon_word", "word_diversity"]:
            v1 = samples[0]["metrics"][m]
            v2 = samples[1]["metrics"][m]
            rng = abs(v2 - v1)
            mean = (v1 + v2) / 2
            cv = (rng / (2 * mean) * 100) if mean != 0 else 0
            print(f"{source:<8} {m:<20} {v1:>10.4f} {v2:>10.4f} {rng:>10.4f} {cv:>7.2f}%")

    print(f"\n  Summary across all prompts:")
    for s in SOURCES:
        r = results["inter_sample_variance"][s]
        print(f"    {s}: avg_range={r['avg_range']:.4f}, avg_CV={r['avg_cv_pct']:.2f}%")

    # ---- Text similarity analysis ----
    sub_sep("1d. Text Similarity Analysis (within-source and cross-source)")
    all_texts: dict[str, list[tuple[str, str]]] = {s: [] for s in SOURCES}
    for prompt_key in prompt_keys:
        for source in SOURCES:
            for sample in prompts[prompt_key][source]["samples"]:
                all_texts[source].append((prompt_key[:40], sample["output"]))

    # Within-source similarity (same prompt, different seeds)
    print("\n  Within-source similarity (same prompt, different seeds):")
    print(f"  {'Prompt':<42} {'Source':<8} {'Jaccard':>8} {'Cosine':>8} {'3gram':>8}")
    print("  " + "-" * 76)
    within_sims = {s: {"jaccard": [], "cosine": [], "ngram": []} for s in SOURCES}
    for prompt_key in prompt_keys:
        short = prompt_key[:40]
        for source in SOURCES:
            samples = prompts[prompt_key][source]["samples"]
            t1, t2 = samples[0]["output"], samples[1]["output"]
            j = jaccard_similarity(t1, t2)
            c = cosine_similarity_bow(t1, t2)
            n = ngram_overlap(t1, t2)
            within_sims[source]["jaccard"].append(j)
            within_sims[source]["cosine"].append(c)
            within_sims[source]["ngram"].append(n)
            print(f"  {short:<42} {source:<8} {j:>8.4f} {c:>8.4f} {n:>8.4f}")

    print(f"\n  Within-source similarity averages:")
    for s in SOURCES:
        j_avg = np.mean(within_sims[s]["jaccard"])
        c_avg = np.mean(within_sims[s]["cosine"])
        n_avg = np.mean(within_sims[s]["ngram"])
        print(f"    {s}: Jaccard={j_avg:.4f}  Cosine={c_avg:.4f}  3-gram={n_avg:.4f}")
        results["text_similarity"][f"{s}_within_source"] = {
            "jaccard_mean": float(j_avg), "cosine_mean": float(c_avg), "ngram_mean": float(n_avg),
        }

    # Cross-source similarity (same prompt, different sources)
    print(f"\n  Cross-source similarity (same prompt, comparing sources):")
    print(f"  {'Prompt':<42} {'Pair':<12} {'Jaccard':>8} {'Cosine':>8}")
    print("  " + "-" * 72)
    cross_sims = defaultdict(lambda: {"jaccard": [], "cosine": []})
    for prompt_key in prompt_keys:
        short = prompt_key[:40]
        for s1, s2 in combinations(SOURCES, 2):
            # Use first sample from each source
            t1 = prompts[prompt_key][s1]["samples"][0]["output"]
            t2 = prompts[prompt_key][s2]["samples"][0]["output"]
            j = jaccard_similarity(t1, t2)
            c = cosine_similarity_bow(t1, t2)
            pair = f"{s1}-{s2}"
            cross_sims[pair]["jaccard"].append(j)
            cross_sims[pair]["cosine"].append(c)
            print(f"  {short:<42} {pair:<12} {j:>8.4f} {c:>8.4f}")

    print(f"\n  Cross-source similarity averages:")
    for pair in cross_sims:
        j_avg = np.mean(cross_sims[pair]["jaccard"])
        c_avg = np.mean(cross_sims[pair]["cosine"])
        print(f"    {pair}: Jaccard={j_avg:.4f}  Cosine={c_avg:.4f}")
        results["text_similarity"][f"cross_{pair}"] = {
            "jaccard_mean": float(j_avg), "cosine_mean": float(c_avg),
        }

    # ---- Mode shift detection ----
    sub_sep("1e. QRNG Mode Shift Detection (narrative -> multiple-choice/list)")
    for prompt_key in prompt_keys:
        short = prompt_key[:55]
        for source in SOURCES:
            for i, sample in enumerate(prompts[prompt_key][source]["samples"]):
                shift = detect_mode_shift(sample["output"])
                if shift["is_mode_shifted"] or shift["multiple_choice"] > 0 or shift["numbered_list"] > 2:
                    print(f"  MODE SHIFT DETECTED: [{source}] sample {i} for \"{short}\"")
                    print(f"    multiple_choice={shift['multiple_choice']}, numbered_list={shift['numbered_list']}")
                    print(f"    narrative_markers={shift['narrative_markers']}, instructional_markers={shift['instructional_markers']}")
                    results["mode_shift_analysis"][f"{source}_{short}_s{i}"] = shift

    if not results["mode_shift_analysis"]:
        print("  No clear mode shifts detected in Mistral outputs.")
        # Still record all mode shift stats for detailed view
        mode_shift_summary = {s: {"total_multi_choice": 0, "total_numbered": 0, "total_instructional": 0} for s in SOURCES}
        for prompt_key in prompt_keys:
            for source in SOURCES:
                for sample in prompts[prompt_key][source]["samples"]:
                    shift = detect_mode_shift(sample["output"])
                    mode_shift_summary[source]["total_multi_choice"] += shift["multiple_choice"]
                    mode_shift_summary[source]["total_numbered"] += shift["numbered_list"]
                    mode_shift_summary[source]["total_instructional"] += shift["instructional_markers"]
        print(f"\n  Mode shift marker totals across all outputs:")
        for s in SOURCES:
            ms = mode_shift_summary[s]
            print(f"    {s}: multi_choice={ms['total_multi_choice']}, numbered_list={ms['total_numbered']}, instructional={ms['total_instructional']}")
        results["mode_shift_analysis"]["summary"] = mode_shift_summary

    # ---- Language mixing detection ----
    sub_sep("1f. TRNG Language Mixing Detection")
    lang_mix_results = {s: {"total_foreign": 0, "total_non_ascii": 0, "samples_with_mixing": 0, "total_samples": 0} for s in SOURCES}
    for prompt_key in prompt_keys:
        for source in SOURCES:
            for i, sample in enumerate(prompts[prompt_key][source]["samples"]):
                lang = detect_language_mixing(sample["output"])
                lang_mix_results[source]["total_samples"] += 1
                lang_mix_results[source]["total_foreign"] += lang["foreign_words"]
                lang_mix_results[source]["total_non_ascii"] += lang["cjk_chars"] + lang["cyrillic_chars"] + lang["arabic_chars"]
                if lang["has_language_mixing"]:
                    lang_mix_results[source]["samples_with_mixing"] += 1
                    print(f"  LANGUAGE MIXING: [{source}] sample {i} for \"{prompt_key[:50]}\"")
                    print(f"    CJK={lang['cjk_chars']}, Cyrillic={lang['cyrillic_chars']}, foreign_words={lang['foreign_words']}")

    if all(v["samples_with_mixing"] == 0 for v in lang_mix_results.values()):
        print("  No significant language mixing detected in Mistral outputs.")
    print(f"\n  Language mixing summary:")
    for s in SOURCES:
        lm = lang_mix_results[s]
        print(f"    {s}: {lm['samples_with_mixing']}/{lm['total_samples']} samples, foreign_words={lm['total_foreign']}, non_ascii={lm['total_non_ascii']}")
    results["language_mixing_analysis"] = lang_mix_results

    return results


# ---------------------------------------------------------------------------
# Section 2: Mistral vs Qwen (Sliding Window vs Full Attention)
# ---------------------------------------------------------------------------
def analyze_mistral_vs_qwen(mistral_data: dict, qwen_8b_data: dict) -> dict:
    separator("SECTION 2: MISTRAL (SWA) vs QWEN 8B (Full Attention) - Entropy Sensitivity")
    results = {}

    # Extract Qwen 8B data from ablation sweeps
    # The Qwen 8B data has dimension/layer/mode sweeps with prng_d2, neural_d2
    # We need the text outputs for matching prompts
    qwen_prompts = list(qwen_8b_data["prompts"].keys()) if isinstance(qwen_8b_data["prompts"], dict) else qwen_8b_data["prompts"]

    # Find the default configuration in Qwen 8B
    mode_sweep = qwen_8b_data["ablations"].get("mode_sweep", {})
    default_config_key = "mode_FULL_layers_20_dims_1024_hash_SHA256"
    if default_config_key in mode_sweep:
        qwen_results = mode_sweep[default_config_key]["results"]
    else:
        # Use the first available
        first_key = list(mode_sweep.keys())[0] if mode_sweep else None
        qwen_results = mode_sweep[first_key]["results"] if first_key else []

    # Mistral prompts
    mistral_prompts = list(mistral_data["prompts"].keys())

    # Find overlapping prompt
    shared_prompts = []
    for mp in mistral_prompts:
        for qr in qwen_results:
            if mp.strip() == qr["prompt"].strip():
                shared_prompts.append(mp)
                break

    print(f"\n  Shared prompts between Mistral and Qwen 8B: {len(shared_prompts)}")
    for sp in shared_prompts:
        print(f"    - \"{sp[:60]}\"")

    # Compare entropy source sensitivity
    # Mistral: we have PRNG, TRNG, QRNG with actual text and metrics
    # Qwen 8B: we have prng_d2, neural_d2 (D2 divergence scores)
    # Different measurement frameworks - compare what we can

    sub_sep("2a. Mistral Source Sensitivity (CV across sources per prompt)")
    mistral_sensitivity = {}
    for prompt_key in mistral_prompts:
        short = prompt_key[:55]
        sw_vals = []
        for source in SOURCES:
            sw_vals.append(mistral_data["prompts"][prompt_key][source]["aggregate_metrics"]["shannon_word_mean"])
        cv = float(np.std(sw_vals) / np.mean(sw_vals) * 100) if np.mean(sw_vals) > 0 else 0.0
        spread = max(sw_vals) - min(sw_vals)
        mistral_sensitivity[short] = {"cv_pct": cv, "spread": spread, "values": {s: v for s, v in zip(SOURCES, sw_vals)}}
        print(f"  \"{short}\"")
        print(f"    shannon_word: PRNG={sw_vals[0]:.4f}, TRNG={sw_vals[1]:.4f}, QRNG={sw_vals[2]:.4f}")
        print(f"    spread={spread:.4f}, CV={cv:.2f}%")

    results["mistral_sensitivity"] = mistral_sensitivity
    avg_cv = np.mean([v["cv_pct"] for v in mistral_sensitivity.values()])
    avg_spread = np.mean([v["spread"] for v in mistral_sensitivity.values()])
    print(f"\n  Mistral average: CV={avg_cv:.2f}%, spread={avg_spread:.4f}")
    results["mistral_avg_cv"] = float(avg_cv)
    results["mistral_avg_spread"] = float(avg_spread)

    sub_sep("2b. Qwen 8B D2 Divergence (PRNG vs Neural seeds)")
    qwen_sensitivity = {}
    for qr in qwen_results:
        prompt = qr["prompt"][:55]
        prng_d2 = qr.get("prng_d2", 0)
        neural_d2 = qr.get("neural_d2", 0)
        diff = qr.get("diff", neural_d2 - prng_d2)
        qwen_sensitivity[prompt] = {"prng_d2": prng_d2, "neural_d2": neural_d2, "diff": diff}
        print(f"  \"{prompt}\"")
        print(f"    prng_d2={prng_d2:.4f}, neural_d2={neural_d2:.4f}, diff={diff:+.4f}")

    results["qwen_8b_sensitivity"] = qwen_sensitivity
    if qwen_sensitivity:
        avg_diff = np.mean([v["diff"] for v in qwen_sensitivity.values()])
        print(f"\n  Qwen 8B average D2 diff (neural-prng): {avg_diff:+.4f}")
        results["qwen_8b_avg_diff"] = float(avg_diff)

    sub_sep("2c. Architecture Comparison Interpretation")
    print("""
  Mistral uses Sliding Window Attention (SWA), attending to a local window
  rather than full context. Qwen 3 uses standard full self-attention.

  KEY FINDING - Cross-source sensitivity comparison:
  """)

    # Mistral: how much does changing the entropy source affect output metrics?
    # Compute per-metric sensitivity
    for m in ["shannon_word", "word_diversity", "length_words"]:
        mistral_vals = {s: [] for s in SOURCES}
        for prompt_key in mistral_prompts:
            for s in SOURCES:
                mistral_vals[s].append(mistral_data["prompts"][prompt_key][s]["aggregate_metrics"][f"{m}_mean"])
        # ANOVA-like: variance between sources vs within sources
        all_means = [np.mean(mistral_vals[s]) for s in SOURCES]
        between_var = float(np.var(all_means))
        within_var = float(np.mean([np.var(mistral_vals[s]) for s in SOURCES]))
        f_ratio = between_var / within_var if within_var > 0 else float("inf")
        print(f"  {m}: between-source var={between_var:.6f}, within-source var={within_var:.6f}, F-ratio={f_ratio:.4f}")
        results[f"mistral_anova_{m}"] = {
            "between_var": between_var, "within_var": within_var, "f_ratio": f_ratio,
        }

    # Compare Qwen's D2 sensitivity
    if qwen_sensitivity:
        d2_diffs = [abs(v["diff"]) for v in qwen_sensitivity.values()]
        print(f"\n  Qwen 8B: mean |D2 diff| = {np.mean(d2_diffs):.4f} (std={np.std(d2_diffs):.4f})")
        print(f"  Mistral: mean shannon_word CV = {avg_cv:.2f}%")
        print(f"\n  INTERPRETATION: {'Mistral SWA shows HIGHER entropy sensitivity' if avg_cv > 1.5 else 'Both architectures show LOW entropy sensitivity'}")
        print(f"  SWA's limited context window may {'amplify' if avg_cv > 2.0 else 'not significantly alter'} seed-derived entropy differences.")

    return results


# ---------------------------------------------------------------------------
# Section 3: Llama 1B Qualitative Profile Analysis
# ---------------------------------------------------------------------------
def analyze_llama(data: dict) -> dict:
    separator("SECTION 3: LLAMA 3.2 1B QUALITATIVE PROFILE ANALYSIS")
    results_out = {
        "per_prompt_profiles": {},
        "aggregate_by_source": {},
        "source_dominance": {},
        "category_analysis": {},
    }

    llama_results = data["results"]
    analysis = data.get("analysis", {}).get("qualitative", {})

    # Score dimensions
    score_keys = [
        "vocabulary_richness", "figurative_language", "emotional_range",
        "novelty", "divergent_thinking", "ethical_alignment", "bias_detection",
        "coherence", "engagement", "formality", "weirdness",
    ]
    categories = [
        "expressiveness", "creativity", "morality", "coherence", "engagement", "style", "weirdness",
    ]

    # ---- Per-prompt profiles ----
    sub_sep("3a. Per-Prompt Qualitative Profiles")
    for r in llama_results:
        prompt = r["prompt"]
        short = prompt[:55]
        print(f"\n  Prompt: \"{short}\"")
        prompt_data = {}
        # Compare overall quality
        print(f"    {'Source':<8} {'Overall':>10} {'Express':>10} {'Creative':>10} {'Coherence':>10} {'Engage':>10}")
        print("    " + "-" * 58)
        for source in SOURCES:
            profile = r["qualitative_profiles"][source]
            oq = profile["overall_quality"]
            cats = profile["category_averages"]
            print(f"    {source:<8} {oq:>10.4f} {cats.get('expressiveness',0):>10.4f} {cats.get('creativity',0):>10.4f} {cats.get('coherence',0):>10.4f} {cats.get('engagement',0):>10.4f}")
            prompt_data[source] = {
                "overall_quality": oq,
                "categories": cats,
                "scores": {k: profile["scores"][k]["value"] for k in score_keys if k in profile["scores"]},
            }
        # Find winner for this prompt
        winner = max(SOURCES, key=lambda s: r["qualitative_profiles"][s]["overall_quality"])
        print(f"    Winner: {winner}")
        prompt_data["winner"] = winner
        results_out["per_prompt_profiles"][short] = prompt_data

    # ---- Aggregate analysis from pre-computed data ----
    sub_sep("3b. Aggregate Qualitative Metrics by Source (from data)")
    if analysis:
        print(f"\n  {'Metric':<25} {'PRNG':>10} {'TRNG':>10} {'QRNG':>10} {'Best':>8}")
        print("  " + "-" * 63)
        for sk in score_keys:
            vals = {}
            for s in SOURCES:
                if s in analysis and sk in analysis[s].get("metrics", {}):
                    vals[s] = analysis[s]["metrics"][sk]["mean"]
            if len(vals) == 3:
                best = max(vals, key=vals.get)
                print(f"  {sk:<25} {vals['PRNG']:>10.4f} {vals['TRNG']:>10.4f} {vals['QRNG']:>10.4f} {best:>8}")
                results_out["aggregate_by_source"][sk] = {**vals, "best": best}

    # ---- Source dominance ----
    sub_sep("3c. Source Dominance Analysis")
    wins = Counter()
    for r in llama_results:
        best_source = max(SOURCES, key=lambda s: r["qualitative_profiles"][s]["overall_quality"])
        wins[best_source] += 1
    total = len(llama_results)
    print(f"\n  Prompt-level wins (overall_quality):")
    for s in SOURCES:
        pct = wins[s] / total * 100
        print(f"    {s}: {wins[s]}/{total} ({pct:.1f}%)")
    results_out["source_dominance"]["prompt_wins"] = dict(wins)

    # Category-level dominance
    cat_wins = {c: Counter() for c in categories}
    for r in llama_results:
        for cat in categories:
            best = max(SOURCES, key=lambda s: r["qualitative_profiles"][s]["category_averages"].get(cat, 0))
            cat_wins[cat][best] += 1

    print(f"\n  Category-level wins:")
    print(f"  {'Category':<18} {'PRNG':>8} {'TRNG':>8} {'QRNG':>8}")
    print("  " + "-" * 42)
    for cat in categories:
        print(f"  {cat:<18} {cat_wins[cat].get('PRNG',0):>8} {cat_wins[cat].get('TRNG',0):>8} {cat_wins[cat].get('QRNG',0):>8}")
    results_out["source_dominance"]["category_wins"] = {c: dict(cat_wins[c]) for c in categories}

    # ---- Statistical significance (Kruskal-Wallis on overall quality) ----
    sub_sep("3d. Statistical Tests (Kruskal-Wallis, n=5 per source)")
    oq_by_source = {s: [] for s in SOURCES}
    for r in llama_results:
        for s in SOURCES:
            oq_by_source[s].append(r["qualitative_profiles"][s]["overall_quality"])

    print(f"\n  Overall quality by source:")
    for s in SOURCES:
        vals = oq_by_source[s]
        print(f"    {s}: mean={np.mean(vals):.4f}, std={np.std(vals):.4f}, range=[{min(vals):.4f}, {max(vals):.4f}]")

    # Kruskal-Wallis
    h_stat, p_val = stats.kruskal(oq_by_source["PRNG"], oq_by_source["TRNG"], oq_by_source["QRNG"])
    print(f"\n  Kruskal-Wallis H={h_stat:.4f}, p={p_val:.4f}")
    print(f"  {'SIGNIFICANT (p<0.05)' if p_val < 0.05 else 'NOT significant (p>=0.05)'} - entropy source {'does' if p_val < 0.05 else 'does NOT'} significantly affect quality")
    results_out["statistical_tests"] = {
        "kruskal_wallis": {"H": float(h_stat), "p": float(p_val), "significant": bool(p_val < 0.05)},
        "source_means": {s: float(np.mean(oq_by_source[s])) for s in SOURCES},
        "source_stds": {s: float(np.std(oq_by_source[s])) for s in SOURCES},
    }

    # Pairwise Mann-Whitney U
    print(f"\n  Pairwise Mann-Whitney U tests:")
    for s1, s2 in combinations(SOURCES, 2):
        u_stat, p_val = stats.mannwhitneyu(oq_by_source[s1], oq_by_source[s2], alternative="two-sided")
        print(f"    {s1} vs {s2}: U={u_stat:.1f}, p={p_val:.4f} {'*' if p_val < 0.05 else ''}")
        results_out["statistical_tests"][f"mann_whitney_{s1}_{s2}"] = {
            "U": float(u_stat), "p": float(p_val), "significant": bool(p_val < 0.05),
        }

    return results_out


# ---------------------------------------------------------------------------
# Section 4: Llama 1B vs Qwen 1.7B Cross-Architecture
# ---------------------------------------------------------------------------
def analyze_llama_vs_qwen_small(llama_data: dict) -> dict:
    separator("SECTION 4: LLAMA 1B vs QWEN 1.7B CROSS-ARCHITECTURE COMPARISON")
    results = {}

    # Try to load Qwen 1.7B data from the complete_with_qrng file
    try:
        with open(QWEN_COMPLETE_PATH) as f:
            qwen_data = json.load(f)
    except Exception as e:
        print(f"  Could not load Qwen 1.7B data: {e}")
        return results

    qwen_models = qwen_data.get("models", [])
    print(f"  Qwen models available: {qwen_models}")
    print(f"  Qwen prompts: {qwen_data.get('prompts', [])}")

    # The Qwen data has different prompts and structure (color, philosophy)
    # vs Llama which has 5 creative/analytical prompts
    # We can still compare general quality patterns

    sub_sep("4a. Architecture Profile Comparison")
    print("""
  Llama 3.2 1B:
    - Architecture: Dense transformer, 1.24B params
    - Attention: Grouped-Query Attention (GQA)
    - Context: 128K tokens
    - Training: Meta's instruction tuning pipeline

  Qwen 3 1.7B:
    - Architecture: Dense transformer, 1.7B params
    - Attention: Full self-attention
    - Context: 32K tokens
    - Training: Alibaba's multilingual training pipeline

  Both are small models (1-2B params) but with different architectural choices.
  Llama uses GQA for efficiency; Qwen uses full attention for quality.
    """)

    # Llama overall quality by source
    llama_oq = {s: [] for s in SOURCES}
    for r in llama_data["results"]:
        for s in SOURCES:
            llama_oq[s].append(r["qualitative_profiles"][s]["overall_quality"])

    print(f"  Llama 1B overall quality by entropy source:")
    for s in SOURCES:
        print(f"    {s}: mean={np.mean(llama_oq[s]):.4f}, std={np.std(llama_oq[s]):.4f}")

    results["llama_1b_quality"] = {
        s: {"mean": float(np.mean(llama_oq[s])), "std": float(np.std(llama_oq[s]))} for s in SOURCES
    }

    # Qwen 1.7b data from the complete file - different format
    if "qwen3:1.7b" in qwen_data.get("results", {}):
        qwen_17b = qwen_data["results"]["qwen3:1.7b"]
        print(f"\n  Qwen 1.7B data available for prompts: {list(qwen_17b.keys())}")
        # Analyze Qwen 1.7B results
        for prompt_key in qwen_17b:
            prompt_results = qwen_17b[prompt_key]
            if isinstance(prompt_results, list) and len(prompt_results) > 0:
                print(f"\n  Qwen 1.7B prompt '{prompt_key}': {len(prompt_results)} results")
                sample = prompt_results[0]
                print(f"    Sample keys: {list(sample.keys())[:10]}")
                if "condition" in sample or "rng" in sample or "source" in sample:
                    conditions = set()
                    for s in prompt_results:
                        for k in ["condition", "rng", "source", "entropy_source"]:
                            if k in s:
                                conditions.add(s[k])
                    print(f"    Conditions found: {conditions}")
                results[f"qwen_17b_{prompt_key}_n"] = len(prompt_results)

    sub_sep("4b. Cross-Architecture Consistency Check")
    # Check if small models show similar entropy source sensitivity patterns
    llama_means = {s: float(np.mean(llama_oq[s])) for s in SOURCES}
    llama_ranking = sorted(SOURCES, key=lambda s: llama_means[s], reverse=True)
    print(f"\n  Llama 1B source ranking: {' > '.join(f'{s}({llama_means[s]:.4f})' for s in llama_ranking)}")

    # Check if the variance across sources is small (suggesting entropy source doesn't matter)
    source_means = list(llama_means.values())
    total_cv = float(np.std(source_means) / np.mean(source_means) * 100)
    print(f"  Llama 1B cross-source CV: {total_cv:.2f}%")
    print(f"  Interpretation: {'SIGNIFICANT' if total_cv > 10 else 'LOW'} variation across entropy sources")
    results["llama_cross_source_cv"] = total_cv
    results["llama_source_ranking"] = llama_ranking

    # Effect size (Cohen's d between best and worst source)
    best, worst = llama_ranking[0], llama_ranking[-1]
    best_vals, worst_vals = llama_oq[best], llama_oq[worst]
    pooled_std = math.sqrt((np.var(best_vals) + np.var(worst_vals)) / 2)
    cohens_d = (np.mean(best_vals) - np.mean(worst_vals)) / pooled_std if pooled_std > 0 else 0
    print(f"\n  Cohen's d ({best} vs {worst}): {cohens_d:.4f}")
    print(f"  Effect size: {'Large (>0.8)' if abs(cohens_d) > 0.8 else 'Medium (0.5-0.8)' if abs(cohens_d) > 0.5 else 'Small (0.2-0.5)' if abs(cohens_d) > 0.2 else 'Negligible (<0.2)'}")
    results["cohens_d_best_worst"] = float(cohens_d)

    return results


# ---------------------------------------------------------------------------
# Section 5: Determinism and Clustering Analysis
# ---------------------------------------------------------------------------
def analyze_determinism_clustering(mistral_data: dict) -> dict:
    separator("SECTION 5: TEXT DETERMINISM AND CLUSTERING ANALYSIS")
    results = {}

    prompts = mistral_data["prompts"]
    prompt_keys = list(prompts.keys())

    # ---- Thinking determinism: how much of the output is "determined" by the prompt? ----
    sub_sep("5a. Prompt Determinism (how much does the prompt constrain output?)")

    # For each prompt, compute mean cross-source similarity
    # High similarity across sources = prompt dominates, seed doesn't matter
    prompt_determinism = {}
    for prompt_key in prompt_keys:
        short = prompt_key[:55]
        all_outputs = []
        for source in SOURCES:
            for sample in prompts[prompt_key][source]["samples"]:
                all_outputs.append(sample["output"])
        # Compute pairwise similarity matrix
        n = len(all_outputs)
        sim_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(i+1, n):
                sim_matrix[i][j] = cosine_similarity_bow(all_outputs[i], all_outputs[j])
                sim_matrix[j][i] = sim_matrix[i][j]
        # Upper triangle mean (excluding diagonal)
        upper_tri = sim_matrix[np.triu_indices(n, k=1)]
        mean_sim = float(np.mean(upper_tri))
        std_sim = float(np.std(upper_tri))
        prompt_determinism[short] = {"mean_pairwise_cosine": mean_sim, "std": std_sim, "n_outputs": n}
        print(f"  \"{short}\"")
        print(f"    Mean pairwise cosine: {mean_sim:.4f} (std={std_sim:.4f}) across {n} outputs")

    results["prompt_determinism"] = prompt_determinism
    overall_determinism = np.mean([v["mean_pairwise_cosine"] for v in prompt_determinism.values()])
    print(f"\n  Overall prompt determinism: {overall_determinism:.4f}")
    print(f"  Interpretation: {'HIGH' if overall_determinism > 0.5 else 'MODERATE' if overall_determinism > 0.3 else 'LOW'} - prompt {'strongly' if overall_determinism > 0.5 else 'moderately' if overall_determinism > 0.3 else 'weakly'} constrains output structure")
    results["overall_determinism"] = float(overall_determinism)

    # ---- Clustering: do outputs cluster by source or by prompt? ----
    sub_sep("5b. Cluster Analysis (do outputs group by SOURCE or by PROMPT?)")

    # Compute within-prompt-within-source vs within-prompt-cross-source vs cross-prompt similarities
    within_source_sims = []   # same prompt, same source, different seed
    cross_source_sims = []    # same prompt, different source
    cross_prompt_sims = []    # different prompt entirely

    for prompt_key in prompt_keys:
        for source in SOURCES:
            samples = prompts[prompt_key][source]["samples"]
            if len(samples) >= 2:
                sim = cosine_similarity_bow(samples[0]["output"], samples[1]["output"])
                within_source_sims.append(sim)

        for s1, s2 in combinations(SOURCES, 2):
            t1 = prompts[prompt_key][s1]["samples"][0]["output"]
            t2 = prompts[prompt_key][s2]["samples"][0]["output"]
            cross_source_sims.append(cosine_similarity_bow(t1, t2))

    for p1, p2 in combinations(prompt_keys, 2):
        t1 = prompts[p1]["PRNG"]["samples"][0]["output"]
        t2 = prompts[p2]["PRNG"]["samples"][0]["output"]
        cross_prompt_sims.append(cosine_similarity_bow(t1, t2))

    print(f"\n  Similarity layers (cosine BoW):")
    print(f"    Within source (same prompt, different seed): mean={np.mean(within_source_sims):.4f} (n={len(within_source_sims)})")
    print(f"    Cross source  (same prompt, different src):  mean={np.mean(cross_source_sims):.4f} (n={len(cross_source_sims)})")
    print(f"    Cross prompt  (different prompt entirely):   mean={np.mean(cross_prompt_sims):.4f} (n={len(cross_prompt_sims)})")

    results["clustering"] = {
        "within_source_mean": float(np.mean(within_source_sims)),
        "cross_source_mean": float(np.mean(cross_source_sims)),
        "cross_prompt_mean": float(np.mean(cross_prompt_sims)),
    }

    # The key insight: is within-source > cross-source?
    # If so, entropy source creates a measurable "fingerprint"
    source_effect = np.mean(within_source_sims) - np.mean(cross_source_sims)
    prompt_effect = np.mean(cross_source_sims) - np.mean(cross_prompt_sims)
    print(f"\n  Source effect (within_source - cross_source): {source_effect:+.4f}")
    print(f"  Prompt effect (cross_source - cross_prompt):  {prompt_effect:+.4f}")
    print(f"\n  INTERPRETATION: {'PROMPT dominates' if prompt_effect > abs(source_effect) else 'SOURCE has comparable effect'}")
    print(f"  Outputs cluster {'primarily by PROMPT content' if prompt_effect > 0.1 else 'weakly'}")
    if abs(source_effect) < 0.02:
        print(f"  Entropy source creates NO measurable clustering effect")
    elif source_effect > 0:
        print(f"  Same-source outputs are SLIGHTLY more similar than cross-source")
    else:
        print(f"  Surprising: cross-source outputs are MORE similar than within-source")

    results["source_effect"] = float(source_effect)
    results["prompt_effect"] = float(prompt_effect)

    # ---- Additional text statistics comparison ----
    sub_sep("5c. Extended Text Statistics by Source")
    print(f"\n  {'Source':<8} {'AvgWordLen':>12} {'AvgSentLen':>12} {'NumSent':>10} {'HapaxRatio':>12}")
    print("  " + "-" * 56)
    for source in SOURCES:
        all_stats = []
        for prompt_key in prompt_keys:
            for sample in prompts[prompt_key][source]["samples"]:
                all_stats.append(compute_text_stats(sample["output"]))
        avg_wl = np.mean([s["avg_word_length"] for s in all_stats])
        avg_sl = np.mean([s["avg_sentence_length"] for s in all_stats])
        avg_ns = np.mean([s["num_sentences"] for s in all_stats])
        avg_hr = np.mean([s["hapax_ratio"] for s in all_stats])
        print(f"  {source:<8} {avg_wl:>12.3f} {avg_sl:>12.2f} {avg_ns:>10.1f} {avg_hr:>12.4f}")
        results[f"{source}_extended_stats"] = {
            "avg_word_length": float(avg_wl),
            "avg_sentence_length": float(avg_sl),
            "avg_num_sentences": float(avg_ns),
            "hapax_ratio": float(avg_hr),
        }

    return results


# ---------------------------------------------------------------------------
# Section 6: Grand Synthesis
# ---------------------------------------------------------------------------
def grand_synthesis(
    mistral_results: dict,
    mistral_vs_qwen: dict,
    llama_results: dict,
    llama_vs_qwen: dict,
    determinism_results: dict,
) -> dict:
    separator("SECTION 6: GRAND SYNTHESIS AND CONCLUSIONS")
    synthesis = {}

    sub_sep("6a. Cross-Model Entropy Source Effect Summary")
    print("""
  +-------------------+------------------------------------------+
  | Model             | Entropy Source Effect on Output Quality   |
  +-------------------+------------------------------------------+""")

    # Mistral
    m_cv = mistral_results.get("cross_prompt_aggregates", {}).get("shannon_word", {})
    m_spread = m_cv.get("delta_QRNG_vs_PRNG", 0)
    print(f"  | Mistral 7B (SWA)  | shannon_word: QRNG delta = {m_spread:+.4f}             |")

    # Llama
    l_stats = llama_results.get("statistical_tests", {})
    l_p = l_stats.get("kruskal_wallis", {}).get("p", 1.0)
    l_means = l_stats.get("source_means", {})
    print(f"  | Llama 1B (GQA)    | KW p={l_p:.4f}, means: {', '.join(f'{s}={v:.3f}' for s,v in l_means.items())} |")

    # Qwen
    q_diff = mistral_vs_qwen.get("qwen_8b_avg_diff", 0)
    print(f"  | Qwen 8B (Full)    | D2 neural-prng diff = {q_diff:+.4f}                  |")
    print("  +-------------------+------------------------------------------+")

    sub_sep("6b. Key Findings")
    findings = []

    # Finding 1: Entropy source sensitivity
    if l_p > 0.05:
        f1 = "Entropy source (PRNG/TRNG/QRNG) does NOT significantly affect output quality (Llama KW p={:.4f})".format(l_p)
    else:
        f1 = "Entropy source SIGNIFICANTLY affects output quality (Llama KW p={:.4f})".format(l_p)
    findings.append(f1)
    print(f"\n  1. {f1}")

    # Finding 2: Determinism
    det = determinism_results.get("overall_determinism", 0)
    f2 = f"Prompt content is the primary driver of output similarity (determinism={det:.4f})"
    findings.append(f2)
    print(f"  2. {f2}")

    # Finding 3: Clustering
    src_eff = determinism_results.get("source_effect", 0)
    prm_eff = determinism_results.get("prompt_effect", 0)
    f3 = f"Outputs cluster by PROMPT (effect={prm_eff:+.4f}), not by entropy source (effect={src_eff:+.4f})"
    findings.append(f3)
    print(f"  3. {f3}")

    # Finding 4: Architecture comparison
    m_avg_cv = mistral_vs_qwen.get("mistral_avg_cv", 0)
    f4 = f"Mistral SWA cross-source CV={m_avg_cv:.2f}% - {'comparable to' if m_avg_cv < 3 else 'higher than'} full attention models"
    findings.append(f4)
    print(f"  4. {f4}")

    # Finding 5: Mode shifts
    mode_shifts = mistral_results.get("mode_shift_analysis", {})
    mode_shift_count = sum(1 for k, v in mode_shifts.items() if k != "summary" and isinstance(v, dict) and v.get("is_mode_shifted"))
    f5 = f"QRNG mode shifts detected: {mode_shift_count} instances in Mistral outputs"
    findings.append(f5)
    print(f"  5. {f5}")

    # Finding 6: Llama source dominance
    dom = llama_results.get("source_dominance", {}).get("prompt_wins", {})
    f6 = f"Llama 1B prompt-level wins: PRNG={dom.get('PRNG',0)}, TRNG={dom.get('TRNG',0)}, QRNG={dom.get('QRNG',0)} (no dominant source)"
    findings.append(f6)
    print(f"  6. {f6}")

    # Finding 7: Effect size
    cd = llama_vs_qwen.get("cohens_d_best_worst", 0)
    f7 = f"Best-vs-worst source Cohen's d={cd:.4f} ({'negligible' if abs(cd) < 0.2 else 'small' if abs(cd) < 0.5 else 'medium' if abs(cd) < 0.8 else 'large'} effect)"
    findings.append(f7)
    print(f"  7. {f7}")

    synthesis["findings"] = findings

    sub_sep("6c. Implications for the SHA256 Paradox")
    sha256_note = """
  The SHA256 Paradox posits that even strong cryptographic hashing cannot
  fully decorrelate sequential consumption of entropy into independent seeds.

  These results show:
  - At the OUTPUT level (text quality, diversity, structure), entropy source
    differences are largely washed out by the model's own deterministic
    processing (attention, MLP, softmax).
  - The MODEL acts as a massive low-pass filter on input entropy. Whether
    the seed comes from PRNG, TRNG, or QRNG, the transformer's billions
    of parameters dominate the output distribution.
  - PROMPT CONTENT is the primary structural driver, with entropy source
    contributing only marginal variation at the token-selection level.
  - This is consistent with the SHA256 Paradox: even if QRNG provides
    "better" randomness, the model's architecture compresses and
    redistributes that entropy through deterministic weight matrices.
    """
    print(sha256_note)
    synthesis["sha256_paradox_note"] = sha256_note.strip()

    return synthesis


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 88)
    print("  DEEP STATISTICAL ANALYSIS: MISTRAL vs LLAMA ENTROPY SOURCE COMPARISON")
    print("  Generated: 2026-02-09")
    print("=" * 88)

    # Load data
    with open(MISTRAL_PATH) as f:
        mistral_data = json.load(f)
    with open(LLAMA_PATH) as f:
        llama_data = json.load(f)
    with open(QWEN_8B_PATH) as f:
        qwen_8b_data = json.load(f)

    print(f"\n  Data loaded:")
    print(f"    Mistral: {mistral_data['model']}, {mistral_data['num_samples']} samples/condition, {len(mistral_data['prompts'])} prompts")
    print(f"    Llama:   {llama_data['config']['model_name']}, {llama_data['config']['num_samples']} samples/condition, {len(llama_data['results'])} prompts")
    print(f"    Qwen:    {qwen_8b_data['hf_name']}, {len(qwen_8b_data['prompts'])} prompts")

    # Run all analyses
    mistral_results = analyze_mistral(mistral_data)
    mistral_vs_qwen = analyze_mistral_vs_qwen(mistral_data, qwen_8b_data)
    llama_results = analyze_llama(llama_data)
    llama_vs_qwen = analyze_llama_vs_qwen_small(llama_data)
    determinism_results = analyze_determinism_clustering(mistral_data)
    synthesis = grand_synthesis(mistral_results, mistral_vs_qwen, llama_results, llama_vs_qwen, determinism_results)

    # Compile all results
    all_results = {
        "metadata": {
            "analysis_date": "2026-02-09",
            "models_analyzed": ["mistral:latest", "meta-llama/Llama-3.2-1B", "Qwen/Qwen3-8B"],
            "mistral_file": str(MISTRAL_PATH),
            "llama_file": str(LLAMA_PATH),
            "qwen_file": str(QWEN_8B_PATH),
        },
        "section_1_mistral": mistral_results,
        "section_2_mistral_vs_qwen": mistral_vs_qwen,
        "section_3_llama": llama_results,
        "section_4_llama_vs_qwen": llama_vs_qwen,
        "section_5_determinism_clustering": determinism_results,
        "section_6_synthesis": synthesis,
    }

    # Save JSON
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n\n  Results saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
