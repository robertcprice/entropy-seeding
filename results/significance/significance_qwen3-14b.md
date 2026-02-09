# Entropy Seeding Significance Summary

**File**: results/vast_pulled_2026-02-07/results/hidden_variance_selfseed_qwen3-14b_20260206_full_v2.json
**Baseline**: prng

## distinct_2

| Source | Mean | Prompts |
|---|---|---|
| prng | 0.8909 | 14 |
| trng | 0.8829 | 14 |
| qrng_cached | 0.9173 | 14 |
| self_seed_sfc | 0.8982 | 14 |
| self_seed_sfs | 0.8841 | 14 |
| hidden_variance | 0.8796 | 14 |
| nebula_bible | 0.9184 | 14 |

| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| trng_vs_prng | -0.0080 | [-0.0476, 0.0324] | 0.367 | 14 |
| qrng_cached_vs_prng | 0.0264 | [-0.0186, 0.0692] | 0.887 | 14 |
| self_seed_sfc_vs_prng | 0.0073 | [-0.0321, 0.0433] | 0.662 | 14 |
| self_seed_sfs_vs_prng | -0.0067 | [-0.0354, 0.0259] | 0.349 | 14 |
| hidden_variance_vs_prng | -0.0112 | [-0.0956, 0.0619] | 0.414 | 14 |
| nebula_bible_vs_prng | 0.0276 | [-0.0129, 0.0697] | 0.907 | 14 |

> **Interpretation:** No entropy source reaches statistical significance for distinct_2 on the 14B model. nebula_bible (P=0.907) and qrng_cached (P=0.887) show weak positive trends but confidence intervals include zero. Notably, the 14B baseline (0.8909) is already substantially higher than the 8B baseline (0.8256), leaving less room for improvement. The larger model's higher baseline bigram diversity may limit the ceiling for entropy-source-driven gains.

## ttr

| Source | Mean | Prompts |
|---|---|---|
| prng | 0.5999 | 14 |
| trng | 0.6131 | 14 |
| qrng_cached | 0.6445 | 14 |
| self_seed_sfc | 0.6256 | 14 |
| self_seed_sfs | 0.6110 | 14 |
| hidden_variance | 0.6110 | 14 |
| nebula_bible | 0.6300 | 14 |

| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| trng_vs_prng | 0.0132 | [-0.0231, 0.0511] | 0.763 | 14 |
| qrng_cached_vs_prng | 0.0446 | [0.0061, 0.0848] | 0.988 | 14 |
| self_seed_sfc_vs_prng | 0.0257 | [-0.0073, 0.0580] | 0.936 | 14 |
| self_seed_sfs_vs_prng | 0.0112 | [-0.0167, 0.0452] | 0.758 | 14 |
| hidden_variance_vs_prng | 0.0112 | [-0.0530, 0.0725] | 0.650 | 14 |
| nebula_bible_vs_prng | 0.0301 | [-0.0128, 0.0753] | 0.920 | 14 |

## repetition_ratio

| Source | Mean | Prompts |
|---|---|---|
| prng | 0.4001 | 14 |
| trng | 0.3869 | 14 |
| qrng_cached | 0.3555 | 14 |
| self_seed_sfc | 0.3744 | 14 |
| self_seed_sfs | 0.3890 | 14 |
| hidden_variance | 0.3890 | 14 |
| nebula_bible | 0.3700 | 14 |

| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| trng_vs_prng | -0.0132 | [-0.0511, 0.0231] | 0.235 | 14 |
| qrng_cached_vs_prng | -0.0446 | [-0.0848, -0.0056] | 0.012 | 14 |
| self_seed_sfc_vs_prng | -0.0257 | [-0.0580, 0.0078] | 0.061 | 14 |
| self_seed_sfs_vs_prng | -0.0112 | [-0.0452, 0.0167] | 0.231 | 14 |
| hidden_variance_vs_prng | -0.0112 | [-0.0725, 0.0530] | 0.343 | 14 |
| nebula_bible_vs_prng | -0.0301 | [-0.0748, 0.0128] | 0.077 | 14 |

## hidden_entropy_mean

| Source | Mean | Prompts |
|---|---|---|
| prng | 1.4625 | 14 |
| trng | 1.4606 | 14 |
| qrng_cached | 1.4796 | 14 |
| self_seed_sfc | 1.4594 | 14 |
| self_seed_sfs | 1.4499 | 14 |
| hidden_variance | 1.4550 | 14 |
| nebula_bible | 1.4599 | 14 |

| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| trng_vs_prng | -0.0019 | [-0.0261, 0.0198] | 0.461 | 14 |
| qrng_cached_vs_prng | 0.0171 | [-0.0181, 0.0506] | 0.840 | 14 |
| self_seed_sfc_vs_prng | -0.0031 | [-0.0298, 0.0203] | 0.414 | 14 |
| self_seed_sfs_vs_prng | -0.0126 | [-0.0537, 0.0262] | 0.268 | 14 |
| hidden_variance_vs_prng | -0.0075 | [-0.0467, 0.0306] | 0.365 | 14 |
| nebula_bible_vs_prng | -0.0025 | [-0.0321, 0.0245] | 0.437 | 14 |

## hidden_entropy_early

| Source | Mean | Prompts |
|---|---|---|
| prng | 1.4345 | 14 |
| trng | 1.4248 | 14 |
| qrng_cached | 1.4367 | 14 |
| self_seed_sfc | 1.4433 | 14 |
| self_seed_sfs | 1.4325 | 14 |
| hidden_variance | 1.4274 | 14 |
| nebula_bible | 1.4433 | 14 |

| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| trng_vs_prng | -0.0097 | [-0.0308, 0.0127] | 0.187 | 14 |
| qrng_cached_vs_prng | 0.0022 | [-0.0237, 0.0272] | 0.590 | 14 |
| self_seed_sfc_vs_prng | 0.0088 | [-0.0186, 0.0361] | 0.736 | 14 |
| self_seed_sfs_vs_prng | -0.0020 | [-0.0331, 0.0310] | 0.441 | 14 |
| hidden_variance_vs_prng | -0.0071 | [-0.0336, 0.0212] | 0.318 | 14 |
| nebula_bible_vs_prng | 0.0088 | [-0.0116, 0.0316] | 0.778 | 14 |

## hidden_entropy_mid

| Source | Mean | Prompts |
|---|---|---|
| prng | 1.4644 | 14 |
| trng | 1.4521 | 14 |
| qrng_cached | 1.4577 | 14 |
| self_seed_sfc | 1.4404 | 14 |
| self_seed_sfs | 1.4453 | 14 |
| hidden_variance | 1.4560 | 14 |
| nebula_bible | 1.4482 | 14 |

| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| trng_vs_prng | -0.0122 | [-0.0428, 0.0173] | 0.215 | 14 |
| qrng_cached_vs_prng | -0.0066 | [-0.0705, 0.0461] | 0.435 | 14 |
| self_seed_sfc_vs_prng | -0.0240 | [-0.0710, 0.0144] | 0.129 | 14 |
| self_seed_sfs_vs_prng | -0.0191 | [-0.0785, 0.0316] | 0.258 | 14 |
| hidden_variance_vs_prng | -0.0084 | [-0.0648, 0.0424] | 0.394 | 14 |
| nebula_bible_vs_prng | -0.0162 | [-0.0522, 0.0143] | 0.168 | 14 |

## hidden_entropy_late

| Source | Mean | Prompts |
|---|---|---|
| prng | 1.4906 | 14 |
| trng | 1.5076 | 14 |
| qrng_cached | 1.5476 | 14 |
| self_seed_sfc | 1.4957 | 14 |
| self_seed_sfs | 1.4731 | 14 |
| hidden_variance | 1.4836 | 14 |
| nebula_bible | 1.4895 | 14 |

| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| trng_vs_prng | 0.0170 | [-0.0287, 0.0555] | 0.788 | 14 |
| qrng_cached_vs_prng | 0.0570 | [0.0150, 0.1005] | 0.996 | 14 |
| self_seed_sfc_vs_prng | 0.0051 | [-0.0316, 0.0422] | 0.608 | 14 |
| self_seed_sfs_vs_prng | -0.0175 | [-0.0867, 0.0441] | 0.305 | 14 |
| hidden_variance_vs_prng | -0.0071 | [-0.0786, 0.0632] | 0.432 | 14 |
| nebula_bible_vs_prng | -0.0011 | [-0.0719, 0.0613] | 0.499 | 14 |
