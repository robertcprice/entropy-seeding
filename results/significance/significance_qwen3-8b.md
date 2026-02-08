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
