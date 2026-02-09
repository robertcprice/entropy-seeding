# Entropy Comparison: mistral:latest

**Timestamp:** 2026-02-08T17:54:07.684330
**Samples per condition:** 2


## Prompt: "The old lighthouse keeper had never seen anything ..."

| Metric | PRNG | TRNG | QRNG |
|--------|------|------|------|
| shannon_char | 4.262 | 4.259 | 4.243 |
| shannon_word | 7.512 | 7.531 | 7.301 |
| word_diversity | 0.522 | 0.526 | 0.532 |
| length_words | 592.500 | 600.500 | 489.500 |

> **Interpretation:** All three entropy sources produce similar character-level entropy (~4.25 bits, within the "good/natural text" range of 4.2-4.7). QRNG generates the shortest output (489.5 words) with highest word diversity (0.532) but lowest word-level entropy (7.301), suggesting more concise, less repetitive text. TRNG has the richest vocabulary distribution (7.531) and slightly more diverse words than PRNG.

### Sample Outputs

**PRNG:** That's intriguing! It sounds like the beginning of a captivating story. Let's continue:  The old lighthouse keeper had never seen anything like it. Ev...

**TRNG:** As he stood on the precipice of the rocky coast, the old lighthouse keeper watched in awe as an ethereal glow began to emanate from the shimmering wat...

**QRNG:** As he stood on the rocky shore, the wind howling around him, the old lighthouse keeper gazed upon a sight that was both magnificent and eerie. The sky...


## Prompt: "She opened the letter, and everything changed...."

| Metric | PRNG | TRNG | QRNG |
|--------|------|------|------|
| shannon_char | 4.253 | 4.276 | 4.288 |
| shannon_word | 6.669 | 6.807 | 6.712 |
| word_diversity | 0.712 | 0.698 | 0.719 |
| length_words | 179.500 | 216.500 | 185.000 |

> **Interpretation:** This prompt produces shorter outputs across all sources (179-216 words). QRNG has highest character entropy (4.288) and word diversity (0.719), suggesting the most varied character usage and least repetition. All word_diversity values exceed 0.7, indicating excellent diversity for this shorter output.

### Sample Outputs

**PRNG:** That's a intriguing start to a story! Let me help you take it further:  As she unfolded the parchment carefully, her heart began to race. The words wr...

**TRNG:** That's an intriguing start to a story! It seems like the protagonist has just received some significant news or discovery. The tension is already high...

**QRNG:** That's an intriguing start to a story! Let's continue:  As she unfolded the parchment inside, her heart raced with anticipation. The ink was a deep, r...


## Prompt: "Once upon a time, in a kingdom by the sea,..."

| Metric | PRNG | TRNG | QRNG |
|--------|------|------|------|
| shannon_char | 4.304 | 4.330 | 4.304 |
| shannon_word | 7.303 | 7.059 | 7.354 |
| word_diversity | 0.591 | 0.626 | 0.566 |
| length_words | 426.000 | 303.000 | 500.000 |

> **Interpretation:** Notable length variation: QRNG produces the longest output (500 words) vs TRNG's shortest (303 words). TRNG achieves the highest word diversity (0.626) despite shorter output. QRNG has highest word entropy (7.354) but lowest diversity (0.566), indicating a wider vocabulary distribution spread across more text with some repetition.

### Sample Outputs

**PRNG:** there lived a young princess named Isabella. She was known throughout the land for her kind heart and beautiful spirit. The kingdom was peaceful, but ...

**TRNG:** there lived a brave and noble knight named Sir Eadric. Known throughout the land for his strength, wisdom, and unwavering courage, he was respected an...

**QRNG:** there lived a humble fisherman named Elias. He spent his days mending nets and fishing on his small boat, eking out a simple yet contented existence. ...


## Prompt: "Explain the concept of entropy to a five-year-old...."

| Metric | PRNG | TRNG | QRNG |
|--------|------|------|------|
| shannon_char | 4.351 | 4.327 | 4.404 |
| shannon_word | 6.694 | 6.658 | 6.682 |
| word_diversity | 0.712 | 0.602 | 0.751 |
| length_words | 169.500 | 218.500 | 155.000 |

> **Interpretation:** QRNG stands out with highest character entropy (4.404) and word diversity (0.751) while being the most concise (155 words). TRNG produces the longest output (218.5 words) but with notably lower diversity (0.602). This pattern suggests QRNG may produce more compressed, information-dense explanatory text.

### Sample Outputs

**PRNG:** Hey there! Let's imagine you have a box of different colored Lego blocks. Now, when you first open the box, all the blocks are mixed up and scattered ...

**TRNG:** Alright, let's imagine you have a box full of toys. When you first open the box, all the toys are scattered everywhere, right? It takes some time and ...

**QRNG:** Hey there, little friend! Let's talk about something called "entropy" - it's a big word that helps us understand how things change and become messy ov...


## Prompt: "What is the meaning of consciousness?..."

| Metric | PRNG | TRNG | QRNG |
|--------|------|------|------|
| shannon_char | 4.252 | 4.258 | 4.239 |
| shannon_word | 6.030 | 6.434 | 6.023 |
| word_diversity | 0.732 | 0.696 | 0.776 |
| length_words | 111.500 | 165.500 | 97.000 |

> **Interpretation:** TRNG generates substantially longer output (165.5 words, ~70% more than QRNG's 97 words) with the highest word entropy (6.434) but lowest diversity (0.696). QRNG is the most concise with highest diversity (0.776), consistent with the pattern of QRNG producing tighter, less repetitive text on analytical prompts.

### Sample Outputs

**PRNG:** Consciousness refers to the state of being aware of one's surroundings, thoughts, feelings, and sensations. It's a complex and multifaceted concept th...

**TRNG:** Consciousness refers to an organism's awareness or perception of their own existence, thoughts, feelings, and environment. It encompasses an individua...

**QRNG:** Consciousness refers to an organism's awareness of their own existence, thoughts, feelings, and the world around them. It encompasses subjective exper...


## Prompt: "Think of a color you have never seen before. Descr..."

| Metric | PRNG | TRNG | QRNG |
|--------|------|------|------|
| shannon_char | 4.367 | 4.338 | 4.299 |
| shannon_word | 6.358 | 6.637 | 6.263 |
| word_diversity | 0.769 | 0.701 | 0.765 |
| length_words | 127.500 | 177.000 | 125.000 |

> **Interpretation:** TRNG produces the longest creative output (177 words) with richest vocabulary distribution (6.637 word entropy) but lowest diversity ratio (0.701). PRNG and QRNG produce similarly concise outputs with high diversity (>0.76). All character entropy values are in the natural text range.

### Sample Outputs

**PRNG:** Creating a new color can be quite imaginative, but let's imagine a unique one for this purpose. I'd like to introduce "Aurora Azure."  Imagine a blend...

**TRNG:** Creating a color that doesn't exist in the visible light spectrum for humans can be quite imaginative! Let's call this new color "Xanadu Blue."  Xanad...

**QRNG:** Creating a completely new color is beyond the realms of our current understanding of physics and light spectrum, as all visible colors are combination...


## Prompt: "Is it ever ethical to tell a lie? If so, under wha..."

| Metric | PRNG | TRNG | QRNG |
|--------|------|------|------|
| shannon_char | 4.415 | 4.338 | 4.311 |
| shannon_word | 7.067 | 7.168 | 7.292 |
| word_diversity | 0.699 | 0.664 | 0.641 |
| length_words | 242.500 | 272.500 | 330.000 |

> **Interpretation:** QRNG produces the longest output (330 words) with highest word-level entropy (7.292) but lowest word diversity (0.641), suggesting it generates more text with richer vocabulary distribution but more repeated words. TRNG falls in the middle, while PRNG is the most concise with highest diversity.

### Sample Outputs

**PRNG:** The question of whether it's ever ethical to tell a lie is a complex one and often depends on cultural, philosophical, and moral perspectives. However...

**TRNG:** The question of ethics and lying is complex and varies based on cultural, philosophical, and religious perspectives. However, many moral theories sugg...

**QRNG:** The question of whether it's ever ethical to tell a lie is a complex one and has been debated throughout history. Philosophically, the concept often r...

---

## Metrics, Symbols & Interpretation Guide

### Metric Definitions

| Metric | Full Name | What It Measures | Range | Interpretation |
|:------:|:---------:|------------------|:-----:|----------------|
| **shannon_char** | Character-Level Shannon Entropy | Information content per character; how uniformly characters are distributed across the text. | 0 - ~5.0 bits | **< 3.5:** Low diversity, repetitive characters. **3.5-4.2:** Moderate. **4.2-4.7:** Good, natural text range. **> 4.7:** Very high diversity. |
| **shannon_word** | Word-Level Shannon Entropy | Information content per word; captures vocabulary richness and distribution. | 0 - ~10+ bits | **< 5.0:** Limited vocabulary. **5.0-7.0:** Moderate. **7.0-8.5:** Rich vocabulary. **> 8.5:** Exceptionally diverse. |
| **word_diversity** | Type-Token Ratio (TTR) | Fraction of unique words out of total words. Higher means fewer repeated words. | 0.0 - 1.0 | **< 0.3:** Very repetitive. **0.3-0.5:** Moderate repetition. **0.5-0.7:** Good diversity. **> 0.7:** Excellent diversity (note: shorter texts naturally score higher). |
| **length_words** | Output Length (Words) | Total word count of the generated output, averaged across samples. | 0 - unlimited | Context-dependent. Useful for detecting truncation (0 words) or verbosity differences between entropy sources. |

### Entropy Sources Compared

| Source | Full Name | Description |
|:------:|:---------:|-------------|
| **PRNG** | Pseudo-Random Number Generator | Mersenne Twister MT19937 with fixed seeds (11, 22, 33, 44, 55). Deterministic and reproducible. |
| **TRNG** | True Random Number Generator | Hardware entropy from `/dev/urandom` on Apple M4 Pro. Non-reproducible, high quality. |
| **QRNG** | Quantum Random Number Generator | IBM Quantum ibm_fez backend (156 superconducting qubits). Fundamentally unpredictable per quantum mechanics. |

### Statistical Notes

This file presents **mean values** averaged across 2 samples per condition per prompt. With only n=2, individual results should be treated as preliminary observations rather than statistically robust findings. No significance tests are reported because the sample size is insufficient for reliable inference.

| Measure | Meaning |
|:-------:|---------|
| **Mean value** | Arithmetic average across all samples for that entropy source and prompt |
| **Differences between columns** | Observed difference in means; not tested for significance at n=2 |

### Symbols Used

This file does not use status symbols. All values are raw numeric means.

### How to Read These Tables

Each table corresponds to a single prompt. The three columns (PRNG, TRNG, QRNG) show the average metric value across 2 generations for each entropy source. To compare entropy sources for a given prompt, read across a row:

- **shannon_char** values near 4.2-4.4 indicate natural, well-formed English text across all sources.
- **shannon_word** values in the 6.0-7.5 range indicate moderate-to-rich vocabulary; higher values suggest the model uses a wider spread of words.
- **word_diversity** above 0.5 indicates good text quality; values above 0.7 are excellent but may be inflated by short output length.
- **length_words** reveals how verbose each entropy source makes the model for a given prompt; large differences suggest the entropy source influences generation length.

Because the sample size is only n=2, treat any observed differences as directional signals rather than confirmed effects.

### Key Takeaways

1. **Entropy source has visible but modest effects on Mistral.** Across all 7 prompts, the three entropy sources produce metrics within close range of each other, with character entropy consistently in the 4.2-4.4 band.

2. **QRNG tends to produce shorter, more concise text** with higher word diversity on analytical and philosophical prompts (e.g., consciousness, entropy explanation). This suggests quantum randomness may nudge the model toward tighter, less verbose responses.

3. **TRNG tends to produce longer outputs** with higher word-level Shannon entropy, suggesting hardware entropy encourages the model to generate more expansive text with wider vocabulary distribution, though sometimes at the cost of word diversity (more repeated words in longer text).

4. **PRNG falls in the middle** on most metrics, occasionally matching or exceeding the others on diversity when output length is moderate.

5. **Prompt type matters.** Creative prompts (fairy tale, color invention) show different entropy source effects than analytical prompts (consciousness, ethics). The interaction between prompt type and entropy source warrants further investigation with larger sample sizes.

6. **Sample size limitation.** With only 2 samples per condition, these results are preliminary. Statistical significance cannot be assessed. Future experiments should use at least n=5 per condition for robust comparison.

For the complete metrics reference, see `METRICS_GLOSSARY.md` in the repository root.
