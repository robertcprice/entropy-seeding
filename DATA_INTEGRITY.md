# Data Integrity Assessment

**Last Updated:** 2026-02-08
**Status:** CRITICAL FINDINGS - Partial Data Invalidity

## Executive Summary

This repository contains mixed valid and invalid experimental data. A significant portion of the Qwen model results (0.6B, 1.7B, 8B, 14B) show identical outputs across different entropy seeds, indicating those results **cannot be used** for entropy source comparisons. However, valid entropy source comparison data exists for DeepSeek-R1 models.

## Valid Data Sources

### DeepSeek-R1 Entropy Comparisons (✅ VALID)

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
