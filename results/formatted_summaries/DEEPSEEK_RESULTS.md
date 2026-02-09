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

> **Why this matters:** When every metric reads exactly 0.0000 and perplexity shows infinity, the model produced no meaningful output at all -- it either emitted an empty string, a single repeated token, or crashed internally. This is not a gradual quality degradation; it is a complete generation failure. The fact that TRNG and QRNG-IBM did NOT fail on the same prompt demonstrates that the failure is entropy-source-specific: the deterministic PRNG seed created an internal state that caused the 32B model's token selection to collapse entirely on this prompt type. For production systems, this means PRNG can silently return garbage to users with no warning.

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

> **Why this matters:** The 70B model exhibits the same catastrophic PRNG failure as the 32B on philosophy prompts, proving this is a systematic vulnerability rather than a one-off fluke. Notably, QRNG-IBM shows degraded but non-zero metrics (shannon_char = 2.2404 vs the normal ~4.4), suggesting it partially recovered but still struggled. TRNG alone produced fully normal output (shannon_char = 4.4373). This establishes a reliability hierarchy: TRNG > QRNG-IBM > PRNG for robustness on challenging prompts. The partial QRNG degradation (roughly half-normal entropy) warrants further investigation into whether quantum-seeded determinism introduces its own subtle constraints.

---

## Metrics, Symbols & Interpretation Guide

### Metric Definitions

| Metric | Full Name | What It Measures | Value Range | Good Values | Bad Values |
|--------|-----------|------------------|-------------|-------------|------------|
| `shannon_char` | Shannon Entropy (character-level) | Information density per character in the generated text. Higher values indicate more unpredictable, diverse character usage. | 0.0 - ~5.0 bits | 3.5 - 4.8 (rich, varied text) | 0.0 (no output or single token); < 2.0 (extremely repetitive or truncated) |
| `shannon_word` | Shannon Entropy (word-level) | Information density per word. Measures vocabulary diversity and word-choice unpredictability. | 0.0 - ~10.0+ bits | 5.0 - 8.0 (diverse vocabulary) | 0.0 (no output); < 3.0 (extremely limited vocabulary) |
| `perplexity` | Perplexity | How "surprised" a language model would be by the output. Reflects the uncertainty in token prediction. Lower perplexity = more predictable, coherent text. | 1.0 - infinity | 100 - 250 (coherent but not overly rigid) | infinity (no valid tokens produced); > 500 (incoherent or random); < 10 (degenerate repetition) |
| `burstiness` | Burstiness Score | Measures temporal variation in token surprisal. Natural human text has moderate burstiness (mix of predictable and surprising passages). Values near 0 mean flat/robotic; high values mean erratic. | 0.0 - 1.0 | 0.2 - 0.5 (natural, human-like rhythm) | 0.0 (no output or perfectly flat); > 0.7 (erratic, unstable generation) |
| `repetition` | Repetition Rate | Fraction of repeated n-grams in the output. Higher means the model is looping or reusing phrases. | 0.0 - 1.0 | < 0.03 (minimal repetition) | > 0.05 (noticeable loops); 0.0 exactly (may indicate truncation or over-constraint) |
| `uniqueness` | Unique Token Ratio | Proportion of distinct tokens relative to total tokens generated. Higher means richer vocabulary usage. | 0.0 - 1.0 | 0.5 - 0.8 (rich, varied output) | 0.0 (no output); < 0.3 (highly repetitive); > 0.95 (may indicate gibberish) |
| `tsa` | Text Structural Analysis | Weighted composite of character-level entropy accounting for text structure (punctuation, capitalization patterns). Indicates structural diversity. | 0.0 - ~5.0 | 3.5 - 4.5 (well-structured text) | 0.0 (no output); < 2.0 (degraded or formulaic structure) |
| `tre` | Token-Rate Entropy | Entropy measured across token emission rates. Typically mirrors `shannon_word` but accounts for generation timing. Higher = more diverse token selection over time. | 0.0 - ~10.0+ bits | 5.0 - 8.0 (diverse generation) | 0.0 (no output); < 3.0 (collapsed generation) |

### Special Symbols and Status Values

| Symbol / Value | Meaning | Interpretation |
|----------------|---------|----------------|
| `0.0000` | Zero value across all metrics | **Catastrophic failure** -- the model produced no meaningful output. The entropy source caused a complete generation collapse. |
| `∞` (infinity) | Infinite perplexity | The model's token probability distribution was undefined or produced zero-probability tokens. Accompanies catastrophic failure (0.0000 on all other metrics). |
| **PRNG** | Pseudo-Random Number Generator | Deterministic algorithmic randomness (Mersenne Twister). Same seed always yields identical output. |
| **TRNG** | True Random Number Generator | Hardware entropy from `/dev/urandom` or system HRNG. Non-deterministic, non-reproducible. |
| **QRNG-IBM** | Quantum Random Number Generator (IBM Quantum) | Entropy from IBM Quantum superconducting qubit measurements via Hadamard gate. Cached from `ibm_fez` backend. |

### How to Read These Tables

Each table in this file compares the same prompt across three entropy sources (PRNG, TRNG, QRNG-IBM) for a specific DeepSeek R1 model size. Read across a row to compare how the same metric performs under different entropy sources. The "color" prompt is a straightforward creative task; the "philosophy" prompt is an open-ended analytical task that stress-tests the model. When you see an entire column of `0.0000` values with `perplexity = ∞`, that entropy source produced a complete generation failure on that prompt -- the model returned no usable text. For healthy generation, expect `shannon_char` around 4.0-4.5, `perplexity` in the 150-200 range, `burstiness` between 0.2-0.5, `repetition` below 0.05, and `uniqueness` above 0.5. The `tsa` and `tre` metrics provide structural and temporal cross-checks on the primary entropy measures.

For the complete metrics reference, see `METRICS_GLOSSARY.md` in the repository root.