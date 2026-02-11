# Cross-Scale Entropy Fingerprint Classification

**Date:** 2026-02-09
**Experiment:** E6 — Fingerprinting at 0.6B and 1.7B scale (existing data)

---

## Summary

Ran the entropy fingerprint classifier on existing hidden_variance_selfseed data at 3 scales to test whether smaller models are more susceptible to entropy source fingerprinting.

**Key Finding: Non-monotonic fingerprint detectability across scale.**

| Scale | Sources | Prompts | Best Multiclass | Lift | Pairwise >60% | Best Pair Accuracy |
|-------|---------|---------|----------------|------|---------------|-------------------|
| 0.6B  | 6       | 8       | 20.4% (LogReg) | 1.2x | 4/15 (27%)    | hv↔qrng 75.0%    |
| 1.7B  | 6       | 8       | 14.2% (XGB)    | 0.8x | 0/15 (0%)     | max 50.0%         |
| 8B    | 7       | 14      | 18.0% (RF)     | 1.3x | 9/21 (43%)    | prng↔sfc 85.7%   |

## Detailed Results

### 0.6B (Qwen3-0.6B)

**Multiclass (6-way, LOGO CV):**
- Random Forest: 10.0% (0.6x baseline)
- XGBoost: 11.3% (0.7x baseline)
- Logistic Regression: 20.4% (1.2x baseline) — best

**Pairwise Binary (>60% marked):**
- hidden_variance vs qrng_cached: **75.0%**
- qrng_cached vs self_seed_sfc: **75.0%**
- qrng_cached vs trng: **71.2%**
- hidden_variance vs prng: **62.5%**
- Mean pairwise: 56.7%

**Top Effect Sizes (vs PRNG):**
- hidden_variance: second_person_rate d=+1.71 (large)
- self_seed_sfc: second_person_rate d=+1.64 (large)
- self_seed_sfs: double_quote_rate d=+1.03 (large)

**Notable:** qrng_cached is the most distinctive source at 0.6B (appears in 3 of 4 top pairs). This suggests quantum randomness leaves the largest footprint on the smallest model.

### 1.7B (Qwen3-1.7B)

**Multiclass (6-way, LOGO CV):**
- Random Forest: 10.4% (0.6x baseline)
- XGBoost: 14.2% (0.8x baseline) — best
- Logistic Regression: 8.7% (0.5x baseline)

**Pairwise Binary:**
- ALL pairs at or below 50% — completely undetectable
- Mean pairwise: 37.9% (below chance!)
- Best pair: 50.0% (= random)

**Top Effect Sizes (vs PRNG):**
- self_seed_sfs: double_quote_rate d=+1.03 (only large effect)
- Max |d| across all sources ≈ 0.8 — much smaller than 0.6B or 8B

**Notable:** 1.7B is a "fingerprinting dead zone." The model has enough capacity to absorb entropy source differences but not enough to create consistent, detectable patterns.

### 8B (Qwen3-8B) [from previous experiment]

**Multiclass (7-way, LOGO CV):**
- Random Forest: 18.0% (1.3x baseline)

**Pairwise Binary (>60% marked):**
- prng vs self_seed_sfc: **85.7%**
- hidden_variance vs qrng_cached: **78.6%**
- qrng_cached vs self_seed_sfc: **78.6%**
- hidden_variance vs prng: **67.9%**
- 9/21 pairs above 60%
- Mean pairwise: ~62%

**Top Effect Sizes:**
- self_seed_sfc: avg_sentence_length d=1.84 (very large)
- qrng_cached: he_slope d=0.81 (large)

**Notable:** 8B has the strongest fingerprints, partly because it has hidden entropy trajectory features that smaller models lack.

## Interpretation

### The Fingerprinting U-Curve

```
Fingerprint
Detectability
     ^
     |   *                      *
     |  0.6B                   8B
     |
     |           *
     |          1.7B
     |
     +---+--------+--------+----> Scale
       0.6B     1.7B      8B
```

### Hypotheses for Non-Monotonicity

1. **0.6B — Chaotic regime:** The model is small enough that entropy source differences create large perturbations in the output distribution. But the output is also noisy, making some pairs hard to distinguish.

2. **1.7B — Absorption zone:** The model has developed enough internal representation to absorb entropy source differences and produce similar output regardless of source. Like a bigger sponge absorbing the same amount of water — no spillover.

3. **8B — Amplification regime:** The model is sophisticated enough to produce consistent, high-quality output, but the self-referential sources (self_seed_sfc, hidden_variance) interact with the model's own hidden states to create detectable signatures in the generation dynamics.

### Confounding Factors

The comparison is not perfectly clean:
- **Feature availability:** 8B data includes hidden entropy trajectory features (hidden_entropy_early/mid/late) that 0.6B/1.7B lack. These are among the most discriminative features at 8B.
- **Text data:** 0.6B/1.7B only have 240-char text_preview (≈40 words), while 8B has full text. Short texts produce unreliable text-based features.
- **Source set:** 8B includes nebula_bible (7 sources vs 6).
- **Prompt set:** 8B used 14 prompts vs 8 at smaller scales.

### Controlled Comparison Needed

To make the U-curve claim rigorous, we need:
1. Same sources, same prompts, same number of samples across all scales
2. Full text saved (not 240-char preview)
3. Either include or exclude hidden entropy features consistently
4. Run at 4B and 14B to map the curve more densely

## Data Files

| File | Description |
|------|-------------|
| `results/fingerprint_classifier_hidden_variance_selfseed_qwen3-0.6b_20260206_full.json` | 0.6B classifier results |
| `results/fingerprint_classifier_hidden_variance_selfseed_qwen3-1.7b_20260206_full.json` | 1.7B classifier results |
| `entropy-seeding/results/fingerprint/fingerprint_classifier_qwen3_8b_results.json` | 8B classifier results |

## Next Steps

1. **Controlled cross-scale experiment:** Same design at 0.6B, 1.7B, 4B, 8B with full text saved
2. **Feature ablation:** Test 8B classifier with only the features available at smaller scales (remove hidden entropy)
3. **Token-level features:** Add per-step logit entropy, token rank, softmax confidence to improve small-model classification

---

*Generated: 2026-02-09*
