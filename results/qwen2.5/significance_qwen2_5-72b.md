# Entropy Seeding Significance Summary

**File**: results/vast_pulled_2026-02-07/72b/hidden_variance_selfseed_qwen2_5-72b_bnb_full_20260207_020557.json
**Baseline**: prng

## distinct_2

| Source | Mean | Prompts |
|---|---|---|
| prng | 0.9196 | 14 |
| trng | 0.9078 | 14 |
| qrng_cached | 0.9117 | 14 |
| self_seed_sfc | 0.8881 | 14 |
| self_seed_sfs | 0.8993 | 14 |
| hidden_variance | 0.8988 | 14 |
| nebula_bible | 0.9083 | 14 |

| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| trng_vs_prng | -0.0118 | [-0.0305, 0.0061] | 0.099 | 14 |
| qrng_cached_vs_prng | -0.0079 | [-0.0276, 0.0141] | 0.229 | 14 |
| self_seed_sfc_vs_prng | -0.0315 | [-0.0551, -0.0067] | 0.005 | 14 |
| self_seed_sfs_vs_prng | -0.0202 | [-0.0405, -0.0006] | 0.023 | 14 |
| hidden_variance_vs_prng | -0.0208 | [-0.0388, -0.0017] | 0.017 | 14 |
| nebula_bible_vs_prng | -0.0112 | [-0.0371, 0.0084] | 0.177 | 14 |

## ttr

| Source | Mean | Prompts |
|---|---|---|
| prng | 0.6456 | 14 |
| trng | 0.6379 | 14 |
| qrng_cached | 0.6512 | 14 |
| self_seed_sfc | 0.6177 | 14 |
| self_seed_sfs | 0.6272 | 14 |
| hidden_variance | 0.6250 | 14 |
| nebula_bible | 0.6250 | 14 |

| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| trng_vs_prng | -0.0077 | [-0.0263, 0.0106] | 0.205 | 14 |
| qrng_cached_vs_prng | 0.0056 | [-0.0229, 0.0374] | 0.632 | 14 |
| self_seed_sfc_vs_prng | -0.0279 | [-0.0569, 0.0000] | 0.024 | 14 |
| self_seed_sfs_vs_prng | -0.0184 | [-0.0541, 0.0162] | 0.150 | 14 |
| hidden_variance_vs_prng | -0.0206 | [-0.0469, 0.0095] | 0.084 | 14 |
| nebula_bible_vs_prng | -0.0206 | [-0.0541, 0.0106] | 0.103 | 14 |

## repetition_ratio

| Source | Mean | Prompts |
|---|---|---|
| prng | 0.3544 | 14 |
| trng | 0.3621 | 14 |
| qrng_cached | 0.3488 | 14 |
| self_seed_sfc | 0.3823 | 14 |
| self_seed_sfs | 0.3728 | 14 |
| hidden_variance | 0.3750 | 14 |
| nebula_bible | 0.3750 | 14 |

| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| trng_vs_prng | 0.0077 | [-0.0106, 0.0263] | 0.793 | 14 |
| qrng_cached_vs_prng | -0.0056 | [-0.0374, 0.0229] | 0.356 | 14 |
| self_seed_sfc_vs_prng | 0.0279 | [0.0000, 0.0569] | 0.973 | 14 |
| self_seed_sfs_vs_prng | 0.0184 | [-0.0162, 0.0541] | 0.842 | 14 |
| hidden_variance_vs_prng | 0.0206 | [-0.0095, 0.0469] | 0.912 | 14 |
| nebula_bible_vs_prng | 0.0206 | [-0.0106, 0.0541] | 0.891 | 14 |

## hidden_entropy_mean

| Source | Mean | Prompts |
|---|---|---|
| prng | 1.4060 | 14 |
| trng | 1.4116 | 14 |
| qrng_cached | 1.4167 | 14 |
| self_seed_sfc | 1.4061 | 14 |
| self_seed_sfs | 1.4066 | 14 |
| hidden_variance | 1.4044 | 14 |
| nebula_bible | 1.4145 | 14 |

| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| trng_vs_prng | 0.0056 | [-0.0123, 0.0236] | 0.724 | 14 |
| qrng_cached_vs_prng | 0.0107 | [-0.0086, 0.0328] | 0.838 | 14 |
| self_seed_sfc_vs_prng | 0.0000 | [-0.0301, 0.0343] | 0.470 | 14 |
| self_seed_sfs_vs_prng | 0.0005 | [-0.0162, 0.0199] | 0.521 | 14 |
| hidden_variance_vs_prng | -0.0016 | [-0.0135, 0.0104] | 0.390 | 14 |
| nebula_bible_vs_prng | 0.0085 | [-0.0204, 0.0393] | 0.716 | 14 |

## hidden_entropy_early

| Source | Mean | Prompts |
|---|---|---|
| prng | 1.4514 | 14 |
| trng | 1.4581 | 14 |
| qrng_cached | 1.4481 | 14 |
| self_seed_sfc | 1.4468 | 14 |
| self_seed_sfs | 1.4429 | 14 |
| hidden_variance | 1.4457 | 14 |
| nebula_bible | 1.4535 | 14 |

| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| trng_vs_prng | 0.0067 | [-0.0086, 0.0226] | 0.787 | 14 |
| qrng_cached_vs_prng | -0.0033 | [-0.0277, 0.0194] | 0.399 | 14 |
| self_seed_sfc_vs_prng | -0.0046 | [-0.0315, 0.0199] | 0.357 | 14 |
| self_seed_sfs_vs_prng | -0.0085 | [-0.0269, 0.0111] | 0.205 | 14 |
| hidden_variance_vs_prng | -0.0057 | [-0.0266, 0.0167] | 0.294 | 14 |
| nebula_bible_vs_prng | 0.0021 | [-0.0241, 0.0303] | 0.565 | 14 |

## hidden_entropy_mid

| Source | Mean | Prompts |
|---|---|---|
| prng | 1.4618 | 14 |
| trng | 1.4709 | 14 |
| qrng_cached | 1.4854 | 14 |
| self_seed_sfc | 1.4574 | 14 |
| self_seed_sfs | 1.4601 | 14 |
| hidden_variance | 1.4534 | 14 |
| nebula_bible | 1.4757 | 14 |

| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| trng_vs_prng | 0.0091 | [-0.0118, 0.0300] | 0.798 | 14 |
| qrng_cached_vs_prng | 0.0236 | [-0.0026, 0.0555] | 0.956 | 14 |
| self_seed_sfc_vs_prng | -0.0044 | [-0.0385, 0.0317] | 0.383 | 14 |
| self_seed_sfs_vs_prng | -0.0016 | [-0.0267, 0.0279] | 0.444 | 14 |
| hidden_variance_vs_prng | -0.0084 | [-0.0207, 0.0048] | 0.099 | 14 |
| nebula_bible_vs_prng | 0.0139 | [-0.0185, 0.0487] | 0.790 | 14 |

## hidden_entropy_late

| Source | Mean | Prompts |
|---|---|---|
| prng | 1.3010 | 14 |
| trng | 1.3019 | 14 |
| qrng_cached | 1.3128 | 14 |
| self_seed_sfc | 1.3104 | 14 |
| self_seed_sfs | 1.3132 | 14 |
| hidden_variance | 1.3106 | 14 |
| nebula_bible | 1.3105 | 14 |

| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| trng_vs_prng | 0.0008 | [-0.0310, 0.0296] | 0.541 | 14 |
| qrng_cached_vs_prng | 0.0118 | [-0.0173, 0.0418] | 0.783 | 14 |
| self_seed_sfc_vs_prng | 0.0094 | [-0.0276, 0.0560] | 0.631 | 14 |
| self_seed_sfs_vs_prng | 0.0121 | [-0.0138, 0.0431] | 0.800 | 14 |
| hidden_variance_vs_prng | 0.0096 | [-0.0121, 0.0334] | 0.797 | 14 |
| nebula_bible_vs_prng | 0.0095 | [-0.0318, 0.0480] | 0.691 | 14 |
