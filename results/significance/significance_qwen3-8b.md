# Entropy Seeding Significance Summary

**File**: results/vast_pulled_2026-02-07/results/hidden_variance_selfseed_qwen3-8b_20260206_full_v2.json
**Baseline**: prng

## distinct_2

| Source | Mean | Prompts |
|---|---|---|
| prng | 0.8256 | 14 |
| trng | 0.8601 | 14 |
| qrng_cached | 0.8836 | 14 |
| self_seed_sfc | 0.8510 | 14 |
| self_seed_sfs | 0.8960 | 14 |
| hidden_variance | 0.8279 | 14 |
| nebula_bible | 0.8093 | 14 |

| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| trng_vs_prng | 0.0344 | [-0.0408, 0.1094] | 0.811 | 14 |
| qrng_cached_vs_prng | 0.0579 | [-0.0090, 0.1429] | 0.946 | 14 |
| self_seed_sfc_vs_prng | 0.0253 | [-0.0641, 0.1175] | 0.697 | 14 |
| self_seed_sfs_vs_prng | 0.0703 | [-0.0090, 0.1693] | 0.950 | 14 |
| hidden_variance_vs_prng | 0.0022 | [-0.0793, 0.0619] | 0.551 | 14 |
| nebula_bible_vs_prng | -0.0163 | [-0.1136, 0.0849] | 0.357 | 14 |

> **Interpretation:** No entropy source achieves statistical significance for distinct_2 on this 8B model. self_seed_sfs (P=0.950) and qrng_cached (P=0.946) show suggestive trends toward higher bigram diversity but remain below the p<0.05 threshold. The 8B model appears relatively insensitive to entropy source choice for this metric.

## ttr

| Source | Mean | Prompts |
|---|---|---|
| prng | 0.5826 | 14 |
| trng | 0.5929 | 14 |
| qrng_cached | 0.6200 | 14 |
| self_seed_sfc | 0.5647 | 14 |
| self_seed_sfs | 0.6222 | 14 |
| hidden_variance | 0.5893 | 14 |
| nebula_bible | 0.5536 | 14 |

| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| trng_vs_prng | 0.0103 | [-0.0432, 0.0654] | 0.637 | 14 |
| qrng_cached_vs_prng | 0.0374 | [-0.0179, 0.1077] | 0.886 | 14 |
| self_seed_sfc_vs_prng | -0.0179 | [-0.0865, 0.0441] | 0.298 | 14 |
| self_seed_sfs_vs_prng | 0.0396 | [-0.0201, 0.1155] | 0.869 | 14 |
| hidden_variance_vs_prng | 0.0067 | [-0.0692, 0.0608] | 0.610 | 14 |
| nebula_bible_vs_prng | -0.0290 | [-0.1177, 0.0592] | 0.250 | 14 |

> **Interpretation:** No source reaches significance for TTR. qrng_cached (+0.0374, P=0.886) and self_seed_sfs (+0.0396, P=0.869) show modest positive trends. nebula_bible actually trends slightly lower than PRNG, suggesting Bible-sourced entropy may not help lexical diversity on this model.

## repetition_ratio

| Source | Mean | Prompts |
|---|---|---|
| prng | 0.4174 | 14 |
| trng | 0.4071 | 14 |
| qrng_cached | 0.3800 | 14 |
| self_seed_sfc | 0.4353 | 14 |
| self_seed_sfs | 0.3778 | 14 |
| hidden_variance | 0.4107 | 14 |
| nebula_bible | 0.4464 | 14 |

| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| trng_vs_prng | -0.0103 | [-0.0651, 0.0433] | 0.363 | 14 |
| qrng_cached_vs_prng | -0.0374 | [-0.1077, 0.0179] | 0.110 | 14 |
| self_seed_sfc_vs_prng | 0.0179 | [-0.0441, 0.0865] | 0.694 | 14 |
| self_seed_sfs_vs_prng | -0.0396 | [-0.1155, 0.0201] | 0.127 | 14 |
| hidden_variance_vs_prng | -0.0067 | [-0.0603, 0.0692] | 0.385 | 14 |
| nebula_bible_vs_prng | 0.0290 | [-0.0592, 0.1183] | 0.747 | 14 |

> **Interpretation:** No source significantly reduces repetition on the 8B model. For repetition_ratio, lower is better. qrng_cached (-0.0374, P(delta>0)=0.110, i.e. P(reduction)=0.890) and self_seed_sfs (-0.0396, P(delta>0)=0.127, i.e. P(reduction)=0.873) show the strongest reduction trends but neither reaches conventional significance. Wide confidence intervals reflect high prompt-to-prompt variance with N=14.

## hidden_entropy_mean

| Source | Mean | Prompts |
|---|---|---|
| prng | 1.7627 | 14 |
| trng | 1.7804 | 14 |
| qrng_cached | 1.7959 | 14 |
| self_seed_sfc | 1.7581 | 14 |
| self_seed_sfs | 1.7616 | 14 |
| hidden_variance | 1.7609 | 14 |
| nebula_bible | 1.7775 | 14 |

| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| trng_vs_prng | 0.0177 | [-0.0038, 0.0393] | 0.949 | 14 |
| qrng_cached_vs_prng | 0.0332 | [0.0084, 0.0589] | 0.995 | 14 |
| self_seed_sfc_vs_prng | -0.0045 | [-0.0511, 0.0371] | 0.422 | 14 |
| self_seed_sfs_vs_prng | -0.0011 | [-0.0361, 0.0417] | 0.460 | 14 |
| hidden_variance_vs_prng | -0.0018 | [-0.0275, 0.0235] | 0.438 | 14 |
| nebula_bible_vs_prng | 0.0148 | [-0.0298, 0.0643] | 0.718 | 14 |

> **Interpretation:** qrng_cached is the only source reaching significance for mean hidden entropy (+0.0332, P=0.995, CI excludes zero). This is a strong result: cached quantum randomness reliably increases internal model uncertainty across the full generation. trng shows a suggestive trend (P=0.949) but its CI barely includes zero. Other sources show no meaningful effect.

## hidden_entropy_early

| Source | Mean | Prompts |
|---|---|---|
| prng | 1.6542 | 14 |
| trng | 1.6631 | 14 |
| qrng_cached | 1.6597 | 14 |
| self_seed_sfc | 1.6709 | 14 |
| self_seed_sfs | 1.6285 | 14 |
| hidden_variance | 1.6687 | 14 |
| nebula_bible | 1.6549 | 14 |

| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| trng_vs_prng | 0.0089 | [-0.0119, 0.0287] | 0.803 | 14 |
| qrng_cached_vs_prng | 0.0055 | [-0.0240, 0.0352] | 0.633 | 14 |
| self_seed_sfc_vs_prng | 0.0167 | [-0.0118, 0.0453] | 0.874 | 14 |
| self_seed_sfs_vs_prng | -0.0256 | [-0.0543, 0.0039] | 0.043 | 14 |
| hidden_variance_vs_prng | 0.0145 | [-0.0070, 0.0359] | 0.902 | 14 |
| nebula_bible_vs_prng | 0.0008 | [-0.0436, 0.0436] | 0.528 | 14 |

> **Interpretation:** No source significantly affects early-layer hidden entropy. self_seed_sfs shows a borderline *decrease* (P(delta>0)=0.043, i.e. P(decrease)=0.957), suggesting it may paradoxically reduce early-layer uncertainty. self_seed_sfc and hidden_variance show weak positive trends (P~0.87-0.90) but do not reach significance. Early layers appear relatively robust to entropy source manipulation.

## hidden_entropy_mid

| Source | Mean | Prompts |
|---|---|---|
| prng | 1.7816 | 14 |
| trng | 1.7859 | 14 |
| qrng_cached | 1.8050 | 14 |
| self_seed_sfc | 1.7523 | 14 |
| self_seed_sfs | 1.7723 | 14 |
| hidden_variance | 1.7718 | 14 |
| nebula_bible | 1.7831 | 14 |

| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| trng_vs_prng | 0.0043 | [-0.0275, 0.0363] | 0.582 | 14 |
| qrng_cached_vs_prng | 0.0234 | [-0.0081, 0.0610] | 0.914 | 14 |
| self_seed_sfc_vs_prng | -0.0294 | [-0.0799, 0.0139] | 0.105 | 14 |
| self_seed_sfs_vs_prng | -0.0093 | [-0.0665, 0.0562] | 0.365 | 14 |
| hidden_variance_vs_prng | -0.0098 | [-0.0483, 0.0287] | 0.294 | 14 |
| nebula_bible_vs_prng | 0.0015 | [-0.0654, 0.0730] | 0.498 | 14 |

> **Interpretation:** No source significantly affects mid-layer hidden entropy. All comparisons have wide confidence intervals spanning zero. qrng_cached shows the strongest positive trend (P=0.914) but remains non-significant. Mid-layer representations appear largely unaffected by entropy source choice.

## hidden_entropy_late

| Source | Mean | Prompts |
|---|---|---|
| prng | 1.8522 | 14 |
| trng | 1.8922 | 14 |
| qrng_cached | 1.9229 | 14 |
| self_seed_sfc | 1.8513 | 14 |
| self_seed_sfs | 1.8840 | 14 |
| hidden_variance | 1.8422 | 14 |
| nebula_bible | 1.8943 | 14 |

| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| trng_vs_prng | 0.0399 | [-0.0026, 0.0844] | 0.966 | 14 |
| qrng_cached_vs_prng | 0.0707 | [0.0280, 0.1165] | 0.999 | 14 |
| self_seed_sfc_vs_prng | -0.0009 | [-0.0808, 0.0731] | 0.490 | 14 |
| self_seed_sfs_vs_prng | 0.0318 | [-0.0437, 0.1158] | 0.780 | 14 |
| hidden_variance_vs_prng | -0.0100 | [-0.0569, 0.0341] | 0.330 | 14 |
| nebula_bible_vs_prng | 0.0421 | [-0.0467, 0.1386] | 0.802 | 14 |

> **Interpretation:** Late-layer hidden entropy shows the strongest entropy-source effects across all layers. qrng_cached achieves highly significant results (+0.0707, P=0.999, CI=[0.0280, 0.1165] excludes zero), confirming that quantum randomness reliably elevates late-layer internal uncertainty. trng approaches significance (P=0.966). Late layers appear most sensitive to entropy source quality, consistent with the hypothesis that entropy effects propagate and amplify through transformer depth.

---

## Metrics, Symbols & Interpretation Guide

### 1. Metric Definitions

| Metric | Full Name | What It Measures | Value Range | Good | Bad |
|---|---|---|---|---|---|
| distinct_2 | Distinct Bigrams Ratio | Fraction of unique bigrams (two-word pairs) out of total bigrams in generated text | 0.0 -- 1.0 | Higher (closer to 1.0) = more diverse word combinations | Lower = repetitive phrasing, degenerate output |
| ttr | Type-Token Ratio | Ratio of unique words (types) to total words (tokens) in generated text | 0.0 -- 1.0 | Higher = richer vocabulary usage | Lower = limited vocabulary, repetitive word choice |
| repetition_ratio | Repetition Ratio | Fraction of generated tokens that are repeated n-grams (typically 4-grams or longer) | 0.0 -- 1.0 | Lower (closer to 0.0) = less repetitive output | Higher = more degenerate looping/repetition |
| hidden_entropy_mean | Mean Hidden-State Entropy | Average Shannon entropy of the model's hidden-state activation distributions across all layers, averaged over all generation steps | 0.0 -- ~3.0+ (unbounded, model-dependent) | Higher = greater internal uncertainty/diversity in representations | Lower = more collapsed/deterministic internal states |
| hidden_entropy_early | Early-Layer Hidden Entropy | Shannon entropy of hidden-state activations in the first third of transformer layers | Same as above | Higher = richer early representations | Lower = early collapse of representation diversity |
| hidden_entropy_mid | Mid-Layer Hidden Entropy | Shannon entropy of hidden-state activations in the middle third of transformer layers | Same as above | Higher = sustained diversity through middle processing | Lower = mid-layer representation collapse |
| hidden_entropy_late | Late-Layer Hidden Entropy | Shannon entropy of hidden-state activations in the final third of transformer layers | Same as above | Higher = maintained diversity near output | Lower = late-layer collapse, potentially driving surface-level repetition |

### 2. Entropy Source Definitions

| Source Key | Full Name | Description |
|---|---|---|
| prng | Pseudo-Random Number Generator | Standard software PRNG (baseline). Deterministic algorithm seeded from system entropy. |
| trng | True Random Number Generator | Hardware-based randomness from physical processes (e.g., thermal noise). |
| qrng_cached | Quantum Random Number Generator (Cached) | Randomness derived from quantum mechanical processes, pre-cached for performance. |
| self_seed_sfc | Self-Seed (SFC variant) | Model seeds its own randomness using Small Fast Counting (SFC) generator initialized from model hidden states. |
| self_seed_sfs | Self-Seed (SFS variant) | Model seeds its own randomness using Small Fast Scramble (SFS) generator initialized from model hidden states. |
| hidden_variance | Hidden Variance | Entropy derived from the variance of the model's own hidden-state activations during generation. |
| nebula_bible | Nebula Bible | Entropy extracted from the King James Bible text via the Nebula 5-layer hierarchical extraction pipeline. |

### 3. Statistical Columns Explained

| Column | Full Name | Meaning |
|---|---|---|
| Mean | Arithmetic Mean | Average metric value across all prompts for that entropy source. |
| Prompts | Sample Size (per source) | Number of distinct prompts evaluated. Each prompt produces one generation per source. |
| Mean Delta | Mean Difference | Average of the per-prompt paired differences: (alternative source value) minus (PRNG baseline value). Positive = alternative is higher; negative = alternative is lower. |
| 95% CI | 95% Bootstrap Confidence Interval | The range within which the true mean difference lies with 95% confidence, estimated via bootstrap resampling (typically 10,000 iterations). If this interval excludes zero, the difference is statistically significant at p<0.05. |
| P(Delta>0) | Bootstrap Probability of Positive Difference | Fraction of bootstrap resamples where the mean difference was positive. Values near 1.0 indicate the alternative source reliably produces higher values; values near 0.0 indicate it reliably produces lower values. |
| N | Paired Sample Size | Number of paired observations (one per prompt). Equal to Prompts since each prompt has exactly one observation per source. |

### 4. How to Read the Comparison Tables

Each comparison row is named `{source}_vs_prng`, meaning the metric value of the named source **minus** the PRNG baseline. For example:

- `trng_vs_prng` with Mean Delta = +0.034 means TRNG produced values 0.034 higher than PRNG on average.
- `nebula_bible_vs_prng` with Mean Delta = -0.016 means Nebula Bible produced values 0.016 lower than PRNG on average.

**For metrics where higher is better** (distinct_2, ttr, hidden_entropy_*): positive Mean Delta = source is better than PRNG.

**For metrics where lower is better** (repetition_ratio): negative Mean Delta = source is better than PRNG. In this case, P(Delta>0) near 0.0 indicates the source reliably reduces repetition.

### 5. Significance Thresholds

| P(Delta>0) Range | Interpretation | Conventional Label |
|---|---|---|
| 0.975 -- 1.000 (or 0.000 -- 0.025) | Strong evidence of a real difference | Significant at p<0.05 (two-tailed equivalent) |
| 0.950 -- 0.975 (or 0.025 -- 0.050) | Suggestive evidence, borderline significant | Approaching significance |
| 0.900 -- 0.950 (or 0.050 -- 0.100) | Weak trend, not conventionally significant | Trend only |
| 0.500 -- 0.900 (or 0.100 -- 0.500) | No meaningful evidence of a difference | Not significant |

**Note on two-tailed equivalence:** P(Delta>0) is a one-tailed measure. For two-tailed significance at the 0.05 level, the equivalent thresholds are P(Delta>0) > 0.975 or P(Delta>0) < 0.025. The 95% CI provides a direct two-tailed test: if it excludes zero, the result is significant at p<0.05 (two-tailed).

### 6. Effect Size Interpretation

With N=14, this experiment has limited statistical power. Practical guidelines:

- **P(Delta>0) > 0.99 with CI excluding zero**: Strong, reliable effect. The entropy source consistently outperforms PRNG across prompts.
- **P(Delta>0) = 0.95--0.99**: Suggestive effect. Likely real but needs larger N to confirm. Worth investigating with more prompts.
- **P(Delta>0) = 0.80--0.95**: Weak trend. Could be real but could also be noise. Not actionable without replication.
- **P(Delta>0) = 0.50--0.80**: No evidence of effect. The source behaves indistinguishably from PRNG for this metric.

The magnitude of Mean Delta should be interpreted relative to the metric's scale. For example, a distinct_2 difference of 0.05 on a scale of 0--1 represents a 5 percentage point shift, which is meaningful. A hidden_entropy difference of 0.03 on values around 1.76 represents roughly a 1.7% relative change.

### 7. Key Takeaways for Qwen3-8B

**Statistically significant results (95% CI excludes zero):**
- **qrng_cached** significantly increases **hidden_entropy_mean** (+0.0332, P=0.995) and **hidden_entropy_late** (+0.0707, P=0.999). Cached quantum randomness reliably elevates the model's internal uncertainty, especially in later layers.

**Borderline / suggestive results (P > 0.95 but CI includes zero):**
- **self_seed_sfs** and **qrng_cached** show trends toward higher distinct_2 (P=0.950 and 0.946 respectively).
- **trng** trends toward higher hidden_entropy_mean (P=0.949) and hidden_entropy_late (P=0.966).
- **self_seed_sfs** shows a borderline *decrease* in hidden_entropy_early (P(delta>0)=0.043), suggesting it may reduce early-layer diversity.

**Non-significant results:**
- No entropy source significantly improves surface-level text quality metrics (distinct_2, ttr, repetition_ratio) on this 8B model at conventional significance levels. The effects on output text diversity are small relative to prompt-to-prompt variability.
- hidden_variance, self_seed_sfc, and nebula_bible show no significant effects on any metric.

**Practical implications:** On Qwen3-8B, entropy source choice primarily affects internal model dynamics (hidden entropy) rather than surface text quality. qrng_cached is the only source with reliably measurable effects, and those effects concentrate in late transformer layers. The 8B model appears relatively robust to entropy source manipulation, suggesting its smaller capacity limits how much entropy source quality can influence generation.

For the complete metrics reference, see `METRICS_GLOSSARY.md` in the repository root.
