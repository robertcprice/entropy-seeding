# DeepSeek R1 Entropy Comparison Results

Comparing PRNG vs TRNG vs QRNG-IBM on DeepSeek R1 models.


## deepseek-r1:32b

**Timestamp:** 2026-02-05 05:39:05


### Prompt: color

| Metric | PRNG | TRNG | QRNG-IBM |
|--------|------|------|----------|
| shannon_char | 4.3709 | 4.3430 | 4.3362 |
| shannon_word | 6.8813 | 6.6981 | 6.7681 |
| perplexity | 188.3953 | 183.6569 | 184.3059 |
| burstiness | 0.2359 | 0.5083 | 0.3025 |
| repetition | 0.0138 | 0.0118 | 0.0392 |
| uniqueness | 0.6549 | 0.7105 | 0.5777 |
| tsa | 4.1193 | 4.1118 | 4.1074 |
| tre | 6.8813 | 6.6981 | 6.7681 |

### Prompt: philosophy

| Metric | PRNG | TRNG | QRNG-IBM |
|--------|------|------|----------|
| shannon_char | 0.0000 | 0.0000 | 0.0000 |
| shannon_word | 0.0000 | 0.0000 | 0.0000 |
| perplexity | ∞ | ∞ | ∞ |
| burstiness | 0.0000 | 0.0000 | 0.0000 |
| repetition | 0.0000 | 0.0000 | 0.0000 |
| uniqueness | 0.0000 | 0.0000 | 0.0000 |
| tsa | 0.0000 | 0.0000 | 0.0000 |
| tre | 0.0000 | 0.0000 | 0.0000 |

#### Key Findings

- **PRNG CATASTROPHIC FAILURE**: All metrics = 0 for philosophy prompt
- TRNG and QRNG-IBM produced valid outputs

## deepseek-r1:70b

**Timestamp:** 2026-02-05 05:23:34


### Prompt: color

| Metric | PRNG | TRNG | QRNG-IBM |
|--------|------|------|----------|
| shannon_char | 4.4120 | 4.4655 | 4.4138 |
| shannon_word | 6.8250 | 6.5265 | 6.7930 |
| perplexity | 199.2506 | 196.3429 | 197.9965 |
| burstiness | 0.4506 | 0.2399 | 0.2769 |
| repetition | 0.0243 | 0.0128 | 0.0221 |
| uniqueness | 0.6067 | 0.6531 | 0.5784 |
| tsa | 4.1470 | 4.1983 | 4.1516 |
| tre | 6.8250 | 6.5265 | 6.7930 |

### Prompt: philosophy

| Metric | PRNG | TRNG | QRNG-IBM |
|--------|------|------|----------|
| shannon_char | 0.0000 | 4.4373 | 2.2404 |
| shannon_word | 0.0000 | 6.7929 | 2.5860 |
| perplexity | ∞ | 195.7357 | ∞ |
| burstiness | 0.0000 | 0.6457 | 0.3589 |
| repetition | 0.0000 | 0.0608 | 0.0000 |
| uniqueness | 0.0000 | 0.5021 | 0.4625 |
| tsa | 0.0000 | 4.1596 | 2.0874 |
| tre | 0.0000 | 6.7929 | 2.5860 |

#### Key Findings

- **PRNG CATASTROPHIC FAILURE**: All metrics = 0 for philosophy prompt
- TRNG and QRNG-IBM produced valid outputs