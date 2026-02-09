# LLaMA 3.2 Entropy Comparison Results

Comparing PRNG vs TRNG vs QRNG on LLaMA 3.2 1B.


## meta-llama/Llama-3.2-1B

**Samples per condition:** 10


### Quality Scores by Prompt and Entropy Source


#### Prompt: "The old lighthouse keeper had never seen anything like it...."

| Entropy Source | Overall Quality | Coherence | Creativity |
|----------------|-----------------|-----------|------------|
| PRNG | 0.61 | 0.85 | 0.48 |
| TRNG | 0.61 | 0.67 | 0.59 |
| QRNG | 0.54 | 0.55 | 0.43 |

#### Prompt: "She opened the letter, and everything changed...."

| Entropy Source | Overall Quality | Coherence | Creativity |
|----------------|-----------------|-----------|------------|
| PRNG | 0.60 | 0.22 | 0.55 |
| TRNG | 0.43 | 0.44 | 0.26 |
| QRNG | 0.61 | 0.70 | 0.41 |

#### Prompt: "Once upon a time, in a kingdom by the sea,..."

| Entropy Source | Overall Quality | Coherence | Creativity |
|----------------|-----------------|-----------|------------|
| PRNG | 0.60 | 0.80 | 0.48 |
| TRNG | 0.25 | 0.00 | 0.00 |
| QRNG | 0.52 | 0.30 | 0.48 |

#### Prompt: "Explain the concept of entropy to a five-year-old...."

| Entropy Source | Overall Quality | Coherence | Creativity |
|----------------|-----------------|-----------|------------|
| PRNG | 0.46 | 0.15 | 0.40 |
| TRNG | 0.61 | 0.11 | 0.87 |
| QRNG | 0.29 | 0.00 | 0.05 |

#### Prompt: "What is the meaning of consciousness?..."

| Entropy Source | Overall Quality | Coherence | Creativity |
|----------------|-----------------|-----------|------------|
| PRNG | 0.62 | 0.00 | 0.90 |
| TRNG | 0.60 | 0.40 | 0.60 |
| QRNG | 0.61 | 0.32 | 0.72 |

### Statistical Analysis

---

## Metrics, Symbols & Interpretation Guide

### Metric Definitions

| Metric | Full Name | What It Measures | Value Range | Good Values | Bad Values |
|--------|-----------|------------------|-------------|-------------|------------|
| `Overall Quality` | Overall Quality Score | Composite score combining coherence, creativity, and other generation quality factors into a single normalized rating. | 0.0 - 1.0 | 0.6 - 1.0 (high-quality output) | < 0.3 (poor quality); 0.0 (complete failure) |
| `Coherence` | Coherence Score | Measures logical consistency, grammatical correctness, and semantic flow of the generated text. How well the output "makes sense" as connected prose. | 0.0 - 1.0 | 0.6 - 1.0 (logically consistent, readable) | 0.0 (incoherent or no meaningful output); < 0.3 (barely readable) |
| `Creativity` | Creativity Score | Measures novelty, originality, and imaginative quality of the output. Higher scores indicate unexpected, inventive, or stylistically rich text. | 0.0 - 1.0 | 0.5 - 1.0 (novel, engaging output) | 0.0 (completely generic or no output); < 0.2 (formulaic, boring) |

### Special Values and Patterns

| Value / Pattern | Meaning | Interpretation |
|----------------|---------|----------------|
| `0.00` | Zero score | The model produced output that entirely failed on this dimension -- either no meaningful text, complete incoherence, or zero creative content. |
| High Coherence + Low Creativity | Formulaic output | The model generated grammatically correct but boring, predictable text. Common with PRNG on constrained prompts. |
| Low Coherence + High Creativity | "Interesting garbage" | The model produced novel tokens but failed to connect them logically. Can occur when entropy injection is too aggressive for the model size. |
| Scores near 0.5 across the board | Mediocre baseline | Middle-of-the-road output that is neither particularly good nor bad. May indicate the model is struggling with the prompt. |

### Entropy Source Labels

| Label | Full Name | Description |
|-------|-----------|-------------|
| **PRNG** | Pseudo-Random Number Generator | Deterministic Mersenne Twister seeding. Reproducible but can produce inconsistent quality. |
| **TRNG** | True Random Number Generator | Hardware entropy from `/dev/urandom`. Non-deterministic, generally the most balanced results. |
| **QRNG** | Quantum Random Number Generator | IBM Quantum cached measurements. Provides structured, often constrained output. |

### How to Read These Tables

Each table groups results by prompt (a specific story opening or question) and shows three rows -- one per entropy source (PRNG, TRNG, QRNG). The three score columns (Overall Quality, Coherence, Creativity) are each normalized to 0.0-1.0, where higher is better. To evaluate an entropy source, look at its scores across ALL prompts rather than any single one, because LLaMA-3.2-1B is a small model and individual prompt results can be highly variable. Key patterns to look for: (1) which source consistently avoids zero scores (reliability), (2) which source achieves the highest average across prompts (overall quality), and (3) whether there are coherence-creativity tradeoffs (e.g., high coherence but low creativity suggests constrained generation). Note that scores of 0.00 on coherence or creativity indicate the model completely failed on that dimension for that prompt-source combination -- these are more informative than middling scores because they reveal failure modes.

For the complete metrics reference, see `METRICS_GLOSSARY.md` in the repository root.
