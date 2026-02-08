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
