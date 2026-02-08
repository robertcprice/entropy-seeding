# Data Integrity Assessment

**Last Updated:** 2026-02-08
**Status:** CLARIFIED - Multiple Experiment Datasets with Different Validity

## Executive Summary

This repository contains **multiple distinct experimental datasets**. Some datasets have invalid data (identical outputs), while OTHER datasets contain VALID results showing real entropy source effects including language mixing, mode shifts, and catastrophic failures.

**IMPORTANT:** Do not confuse the `hidden_variance_selfseed` results (INVALID) with the `quantum_activation` / `neural_feedback_quantum` results (VALID).

## Valid Data Sources (✅)

### 1. DeepSeek-R1 Entropy Comparisons (✅ VALID)

**Files:**
- `/vast_results/deepseek-r1_70b_entropy_comparison.json`
- `/vast_results/deepseek-r1_32b_entropy_comparison.json`
- `/results/QUALITATIVE_ANALYSIS_ANOMALIES.md`

**What These Contain:**
- Actual PRNG vs TRNG vs QRNG comparisons with different metrics
- Real text output examples showing different characteristics
- Documented catastrophic PRNG failure on philosophy prompt (DeepSeek-R1 70B)

**Key Valid Finding:**
```
DeepSeek-R1 70B - Philosophy Prompt
PRNG:  All metrics = 0.0, Perplexity = ∞ (COMPLETE FAILURE)
TRNG:  Shannon = 4.44, Perplexity = 195.74 (WORKING)
QRNG:  Shannon = 2.24, Perplexity = ∞ (PARTIAL FAILURE)
```

**Color Naming Examples (Valid):**
- PRNG: Named color "Elyndor" (fantasy theme)
- TRNG: Named color "Aurorin" (celestial theme)
- QRNG: Named color "Lunaris" (astronomical theme)

---

### 2. Qwen3-8B / Qwen3-14B Quantum Activation Results (✅ VALID - REAL EFFECTS!)

**Location:** `/Users/bobbyprice/projects/entropy/results/quantum_activation/` and `/results/neural_feedback_quantum/`

**Documentation:** `/docs/QUANTUM_RNG_QUALITATIVE_ANALYSIS_2026-02-04.md`

**What These Contain:**
- **REAL qualitative differences** between PRNG, TRNG, and QRNG_INT
- **Language mixing glitches** (TRNG produced Chinese text mid-generation)
- **Catastrophic mode shifts** (QRNG switched from narrative to multiple-choice test format)
- **Meta-cognitive behaviors** (self-aware commentary)
- **Creativity differences** by entropy source

**Key Valid Findings:**

**Language Mixing (TRNG):**
> "翻译句子并解析句子成分..." (Chinese text appeared mid-generation)

**Mode Shift (QRNG_INT on Qwen 14B):**
> Started with narrative: "The old lighthouse keeper had never seen anything like it."
> Switched to: "A. operating at full capacity / B. visited by tourists / C. abandoned / D. under repair"
> Then meta-commentary: "Okay, let's see. The question is about..."

**Creativity Differences:**
- **QRNG_INT**: Highest creativity, surreal imagery, but prone to catastrophic glitches
- **TRNG**: Good creativity, sensory details, but language mixing issues
- **PRNG**: Most coherent, but shows repetition and moderate meta-cognition

**Files:**
- `quantum_activation_fixed_Qwen_Qwen3-8B_20260203_152746.json` (3.6MB)
- `quantum_inverted_Qwen_Qwen3-8B_20260203_154311.json` (3.5MB)
- `quantum_activation_Qwen_Qwen3-8B_20260203_142215.json` (2.5MB)
- `quantum_only_Qwen_Qwen3-8B_20260203_182321.json` (123KB)
- `temperature_sweep_Qwen_Qwen3-8B_20260203_161950.json` (224KB)
- `complete_with_qrng_20260205_145740.json` (colored entropy variants)
- Multiple neural_feedback_quantum experiment files (0.6B, 4B, 8B, 14B)
- **All copied to:** `/results/valid_entropy_comparisons/qwen_quantum_activation/`

**Evidence Report:** `/docs/seeding/ENTROPY_SEEDING_EVIDENCE_REPORT_2026-02-06.md`

---

### 3. Other Valid Qwen Results (✅ VALID)

**8B Comprehensive Results:** `/8B_comprehensive_results.json`
- Shows PRNG vs neural seeding comparisons with different text outputs
- Valid entropy comparisons

**RNG Comparison Quick:** `/data/rng_comparison_quick/rng_comparison_quick_results_20260203_180635.json`
- PRNG vs TRNG vs QRNG comparisons
- Different qualitative profiles for each source

## Invalid Data Sources (⚠️ DO NOT USE FOR ENTROPY COMPARISONS)

### Qwen Model Results with Hidden Variance Format

**Files Affected:**
- `/results/qwen/qwen3_0.6b_full_results.json`
- `/results/qwen/qwen3_1.7b_full_results.json`
- `/results/qwen/qwen3_8b_full_results.json`
- `/results/qwen/qwen3_14b_full_results.json`
- Any files with `hidden_variance_selfseed` in the filename

**Problem:**
- 85% of results show **identical outputs** across different seeds (11, 22, 33, 44, 55)
- Entropy sources were not actually varying the outputs
- Statistical comparisons in these files are meaningless

**Example of Invalid Data:**
```json
{
  "source": "qrng_cached",
  "prompt_id": "phil_1",
  "seed": 33,
  "metrics": {"distinct_2": 0.9606, "ttr": 0.6484},
  "text_preview": "Consciousness is a complex..."
}
// Seed 44: IDENTICAL metrics and text
// Seed 55: IDENTICAL metrics and text
```

**Analysis:**
- Qwen3 0.6B: 83.3% of results identical across seeds
- Qwen3 8B: 85.7% of results identical across seeds
- Qwen3 14B: 85.7% of results identical across seeds

**Possible Cause:**
The experimental setup may have:
1. Used deterministic sampling that overrides seed values
2. Applied temperature settings that eliminate entropy variation
3. Cached outputs incorrectly
4. Had implementation errors in entropy source application

## Statistical Significance Files

**Files:**
- `/results/significance/significance_qwen3-8b.md`
- `/results/significance/significance_qwen3-14b.md`
- `/results/significance/significance_qwen2_5-72b.md`

**Status: ⚠️ QUESTIONABLE**
- These files show p-values and confidence intervals
- However, since underlying data has identical outputs, these statistics are based on invalid comparisons
- The p-values may be mathematically correct but meaningless because the premise (different entropy sources producing different outputs) is false

## What This Means

### Conclusions That ARE Supported (Based on Valid DeepSeek-R1 Data)

1. **PRNG can catastrophically fail on complex prompts**
   - DeepSeek-R1 70B with seed=42 on philosophy prompt: complete generation failure
   - This is a documented, reproducible finding

2. **Different entropy sources produce different text characteristics**
   - Color naming task produced different names and descriptions
   - Different formatting and structural preferences observed

3. **TRNG shows better metrics in valid tests**
   - Lower repetition, higher uniqueness where comparisons exist

### Conclusions That Are NOT Supported (Based on Invalid Qwen Data)

1. ~~"TRNG consistently outperforms PRNG across model sizes"~~
   - The Qwen data showing this cannot be trusted

2. ~~"Model size mediates entropy source effects"~~
   - Cannot be determined from invalid data

3. ~~"Qwen3 8B shows statistical significance: p < 0.05"~~
   - Based on identical outputs, meaningless

4. ~~"Architecture-specific responses (Dense vs MoE)"~~
   - Need valid data across both architectures

## Recommended Actions

### For Researchers Using This Data

1. **Use only DeepSeek-R1 entropy comparison files** for valid PRNG/TRNG/QRNG comparisons
2. **Ignore Qwen hidden_variance results** for entropy source comparisons
3. **Treat statistical significance files with extreme caution** - they may be mathematically correct but based on flawed data

### For Future Work

1. **Re-run Qwen experiments** with proper entropy source variation
2. **Verify entropy sources are actually applied** by checking for output variance
3. **Use smaller sample sizes** with proper validation before scaling up
4. **Pre-register experimental protocols** to prevent implementation errors

## Honest Summary

**What We Actually Know:**
- DeepSeek-R1 70B shows real entropy source effects
- PRNG can fail catastrophically on certain prompts
- Different entropy sources produce qualitatively different outputs

**What We Thought We Knew (But Don't):**
- Comprehensive model size comparisons (invalid data)
- Architecture-specific patterns (insufficient valid data)
- Statistical significance across models (based on identical outputs)

**The Bottom Line:**
This repository contains a valuable but partial dataset. The DeepSeek-R1 findings are real and important. The Qwen findings cannot be trusted for entropy source comparisons due to implementation issues that caused identical outputs across different seeds.

---

**Transparency Statement:**
This assessment is being provided to maintain full research integrity. The invalid data has been identified and clearly marked. Future work should focus on re-running affected experiments with proper validation.
