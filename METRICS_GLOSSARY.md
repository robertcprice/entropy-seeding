# Entropy Seeding Experiment — Metrics, Symbols & Interpretation Guide

**Purpose:** This document defines every metric, statistical measure, symbol, and abbreviation used across the entropy seeding experiment reports. Use this as a reference when reading any results table.

---

## 1. Entropy Sources (Independent Variables)

| Source | Full Name | Description | Implementation |
|:------:|:---------:|-------------|----------------|
| **PRNG** | Pseudo-Random Number Generator | Deterministic sequence from a fixed seed. Reproducible but predictable. | `random.Random(42)` → Mersenne Twister |
| **TRNG** | True Random Number Generator | Hardware entropy from OS entropy pool. Non-reproducible, high quality. | `secrets.token_bytes()` → `/dev/urandom` |
| **QRNG** | Quantum Random Number Generator (SHA256-mixed) | SHA256 hash of timestamp + hardware entropy + counter. NOT true quantum. | `SHA256(time_ns + secrets + counter)` |
| **QRNG-IBM** | Quantum Random Number Generator (IBM Quantum) | Real quantum measurements from IBM ibm_fez superconducting qubits. Fundamentally unpredictable per Bell's theorem. | IBM Quantum `ibm_fez` backend, 156 qubits |
| **qrng_cached** | Cached Quantum RNG | Pre-generated quantum random numbers from IBM hardware, stored locally for reproducible experiments. | Binary cache files from IBM Quantum |
| **self_seed_sfc** | Self-Seed (SFC mixing) | Model's own hidden-state activations fed back as seed, mixed with SFC (Small Fast Counting) algorithm. | Hidden layer → SFC hash → seed |
| **self_seed_sfs** | Self-Seed (SFS mixing) | Model's own hidden-state activations fed back as seed, mixed with SFS (Small Fast Scramble) algorithm. | Hidden layer → SFS hash → seed |
| **hidden_variance** | Hidden Layer Variance | Statistical variance of model's internal hidden-state activations used as entropy source. | `var(hidden_states)` → seed |
| **nebula_bible** | Nebula Bible Extraction | Text-derived entropy from Bible KJV via the Nebula 5-layer hierarchical extraction method. | Bible KJV → Nebula pipeline → seed |
| **neural** | Neural Activation Entropy | Entropy derived from MLP layer activations within the model during inference. | Forward pass → MLP activations → hash → seed |

---

## 2. Output Quality Metrics

### 2a. Shannon Entropy Metrics

| Metric | Full Name | What It Measures | Formula | Range | Interpretation |
|:------:|:---------:|------------------|---------|:-----:|----------------|
| **shannon_char** | Character-Level Shannon Entropy | Information content per character. Higher = more uniform character distribution = more diverse text. | H = -Σ p(c) log₂ p(c) | 0–~5.0 bits | **< 3.5:** Low diversity, repetitive characters. **3.5–4.2:** Moderate. **4.2–4.7:** Good, natural text range. **> 4.7:** Very high diversity. |
| **shannon_word** | Word-Level Shannon Entropy | Information content per word. Higher = richer vocabulary usage. | H = -Σ p(w) log₂ p(w) | 0–~10+ bits | **< 5.0:** Limited vocabulary. **5.0–7.0:** Moderate. **7.0–8.5:** Rich vocabulary. **> 8.5:** Exceptionally diverse word usage. |

### 2b. Diversity Metrics

| Metric | Full Name | What It Measures | Formula | Range | Interpretation |
|:------:|:---------:|------------------|---------|:-----:|----------------|
| **word_diversity** / **ttr** | Type-Token Ratio | Fraction of unique words in the output. Higher = less repetition. | unique_words / total_words | 0.0–1.0 | **< 0.3:** Very repetitive. **0.3–0.5:** Moderate repetition. **0.5–0.7:** Good diversity. **> 0.7:** Excellent diversity (short texts tend higher). |
| **distinct_2** / **D2** | Bigram Diversity | Fraction of unique two-word pairs (bigrams). More sensitive to phrase-level repetition than TTR. | unique_bigrams / total_bigrams | 0.0–1.0 | **< 0.7:** Significant repetition. **0.7–0.85:** Moderate. **0.85–0.95:** Good. **> 0.95:** Excellent (near-zero phrase repetition). |
| **repetition_ratio** | Repetition Ratio | Complement of TTR: fraction of repeated words. Lower = better. | 1 - ttr | 0.0–1.0 | **< 0.3:** Excellent (low repetition). **0.3–0.5:** Good. **0.5–0.7:** Moderate repetition. **> 0.7:** Severe repetition problem. |
| **uniqueness** | Word Uniqueness | Same as TTR but used in DeepSeek experiments. Fraction of unique words. | unique_words / total_words | 0.0–1.0 | Same as ttr above. |
| **hapax_ratio** | Hapax Legomena Ratio | Fraction of words that appear exactly once. High = rich, non-repetitive vocabulary. | words_appearing_once / total_unique_words | 0.0–1.0 | **< 0.5:** Many repeated words. **0.5–0.7:** Moderate. **> 0.7:** Most words used only once. |

### 2c. Statistical Text Properties

| Metric | Full Name | What It Measures | Formula | Range | Interpretation |
|:------:|:---------:|------------------|---------|:-----:|----------------|
| **perplexity** | Cross-Entropy Perplexity | How "surprised" a language model would be by the text. Lower = more predictable/coherent. | 2^(cross_entropy) | 1–∞ | **< 50:** Very predictable/formulaic. **50–200:** Natural range. **200–500:** Diverse/creative. **∞:** Catastrophic failure (zero-length output). |
| **burstiness** | Output Burstiness | Measures how "bursty" the text structure is — whether information clusters in bursts vs flows smoothly. | Variance of local entropy windows | 0.0–1.0 | **< 0.2:** Very smooth, even flow. **0.2–0.4:** Natural range. **0.4–0.6:** Moderately bursty. **> 0.6:** Highly erratic output structure. |
| **length_words** | Output Length | Total number of words generated. | word_count(output) | 0–∞ | Context-dependent. Useful for detecting truncation (0) or verbosity differences between sources. |

### 2d. Advanced Entropy Metrics

| Metric | Full Name | What It Measures | Formula | Range | Interpretation |
|:------:|:---------:|------------------|---------|:-----:|----------------|
| **tsa** | Temporal Shannon Analysis | Windowed Shannon entropy computed over sliding text windows. Captures entropy variation over the course of generation. | mean(H_window for each window) | 0–~5.0 | Similar to shannon_char but tracks how entropy evolves during generation. **Stable values** suggest consistent quality; **declining values** suggest degeneration. |
| **tre** | Token Richness Entropy | Combined measure of token-level entropy incorporating bigram patterns and vocabulary richness. | Composite of token entropy + vocab richness + Zipf ratio | 0–~10 | Higher = richer token-level patterns. Values track closely with shannon_word. |

### 2e. Hidden Layer Metrics (H200 GPU Experiments Only)

| Metric | Full Name | What It Measures | Layer Position | Range | Interpretation |
|:------:|:---------:|------------------|:--------------:|:-----:|----------------|
| **hidden_entropy_early** | Early Layer Activation Entropy | Entropy of hidden-state activations in the model's first third of layers. Captures low-level feature diversity. | Layers 0–⅓ | ~1.0–2.5 | Higher = more diverse internal representations at early processing stages. |
| **hidden_entropy_mid** | Mid Layer Activation Entropy | Entropy in middle layers where abstract features form. | Layers ⅓–⅔ | ~1.0–2.5 | Higher = more diverse intermediate representations. |
| **hidden_entropy_late** | Late Layer Activation Entropy | Entropy in final layers closest to token prediction. Most directly influences output diversity. | Layers ⅔–1.0 | ~1.0–2.5 | Higher = more diverse representations at decision-making layers. **This metric shows the strongest entropy source effects.** |
| **hidden_entropy_mean** | Mean Hidden Layer Entropy | Average across all layer positions. Overall measure of internal state diversity. | All layers | ~1.0–2.5 | Higher = more diverse internal state overall. Less sensitive than late-layer entropy to source effects. |

---

## 3. Statistical Measures & Test Results

### 3a. Significance Tests

| Symbol | Full Name | What It Tests | When to Use | Interpretation |
|:------:|:---------:|---------------|-------------|----------------|
| **Wilcoxon p** | Wilcoxon Signed-Rank Test p-value | Non-parametric paired test: are two matched distributions different? | When data may not be normally distributed (small N, skewed). | **p < 0.05:** Statistically significant difference. **p < 0.01:** Highly significant. **p > 0.05:** No significant difference detected. |
| **t-test p** | Paired t-test p-value | Parametric paired test assuming normal differences. | When differences are approximately normally distributed. | Same interpretation as Wilcoxon p. |
| **KW H** | Kruskal-Wallis H statistic | Non-parametric test: do 3+ groups differ? Like a non-parametric one-way ANOVA. | Comparing all entropy sources simultaneously. | Higher H = more evidence of group differences. Significance determined by p-value. |
| **P(Δ>0)** | Bootstrap Probability | Probability that the true difference is positive, estimated by 5000+ bootstrap resamples. | When comparing two sources (e.g., QRNG vs PRNG). | **> 0.95 or < 0.05:** Strong evidence of a real difference. **0.90–0.95:** Trending toward significance. **0.05–0.95:** Not significant. |
| **Mann-Whitney U** | Mann-Whitney U test | Non-parametric test comparing two independent groups. | When samples are unpaired. | p < 0.05 = significant difference between groups. |

### 3b. Effect Size Measures

| Symbol | Full Name | What It Measures | Interpretation Ranges |
|:------:|:---------:|------------------|-----------------------|
| **Cohen's d** | Cohen's d Effect Size | Standardized difference between two group means, measured in pooled standard deviations. | **\|d\| < 0.2:** Negligible effect. **0.2–0.5:** Small effect. **0.5–0.8:** Medium effect. **> 0.8:** Large effect. |
| **95% CI** | 95% Confidence Interval | Range within which the true difference lies with 95% probability. | **CI excludes 0:** Effect is statistically significant. **CI includes 0:** Cannot rule out no difference. **Narrow CI:** Precise estimate. **Wide CI:** Uncertain estimate. |
| **Mean Δ** | Mean Difference | Average difference between two conditions (e.g., QRNG mean - PRNG mean). | **Positive:** First condition is higher. **Negative:** First condition is lower. **Near 0:** No meaningful difference. |
| **CV** | Coefficient of Variation | Standard deviation divided by mean, expressed as %. Measures relative variability. | **< 5%:** Very consistent. **5–15%:** Moderate variation. **> 15%:** High variation. |
| **F-ratio** | F-ratio (ANOVA) | Ratio of between-group variance to within-group variance. | **< 0.1:** Between-group differences negligible compared to within-group. **~1.0:** Equal variance. **> 2.0:** Meaningful between-group effect. |

### 3c. Significance Thresholds

| Notation | p-value Range | Meaning | Confidence Level |
|:--------:|:------------:|---------|:----------------:|
| **ns** | p > 0.10 | Not significant | < 90% |
| * | 0.05 < p < 0.10 | Trending / marginally significant | 90–95% |
| ** | 0.01 < p < 0.05 | Statistically significant | 95–99% |
| *** | p < 0.01 | Highly significant | > 99% |
| **[CI excl. 0]** | — | Bootstrap confidence interval does not include zero | Effect confirmed non-zero |

---

## 4. Table Symbols & Status Indicators

| Symbol | Meaning | Context |
|:------:|---------|---------|
| ✅ | Complete / Passed | Experiment or test completed successfully |
| ❌ | Failed / Error | Experiment or test failed |
| 🔄 | Running / In Progress | Experiment currently executing |
| ⏳ | Queued / Waiting | Scheduled but not yet started |
| ↓ | Decreasing trend | Metric declining over multi-turn conversation |
| ↑ | Increasing trend | Metric improving over multi-turn conversation |
| ∞ | Infinity | Perplexity of zero-length output (catastrophic failure) |
| **FAIL** | Catastrophic failure | Model produced zero or garbage output |
| **DEGRADED** | Partial failure | Model produced output but severely below normal quality |
| **REVERSAL** | Direction reversal | Effect goes in the opposite direction from smaller models |
| **+** / **-** | Delta direction | Positive or negative change vs baseline |
| **bold** values | Notable results | Statistically significant or otherwise noteworthy |

---

## 5. Entropy Source Abbreviations

| Abbreviation | Full Form |
|:------------:|-----------|
| PRNG | Pseudo-Random Number Generator (Mersenne Twister, seed=42) |
| TRNG | True Random Number Generator (hardware /dev/urandom) |
| QRNG | Quantum Random Number Generator (context-dependent: IBM or SHA256) |
| QRNG-IBM | Specifically the IBM Quantum ibm_fez backend |
| SFC | Small Fast Counting (hash mixing algorithm) |
| SFS | Small Fast Scramble (hash mixing algorithm) |
| D2 | distinct_2 (bigram diversity) |
| TTR | Type-Token Ratio (word diversity) |
| KW | Kruskal-Wallis (statistical test) |
| MW-U | Mann-Whitney U (statistical test) |
| CI | Confidence Interval |
| CV | Coefficient of Variation |
| SWA | Sliding Window Attention (Mistral architecture) |
| GQA | Grouped-Query Attention (Llama architecture) |
| MoE | Mixture of Experts (DeepSeek, Mixtral architecture) |
| H200 | NVIDIA H200 GPU (used for instrumented experiments) |
| MLP | Multi-Layer Perceptron (neural network layer type) |
| TSA | Temporal Shannon Analysis |
| TRE | Token Richness Entropy |

---

## 6. How to Read the Results Tables

### Example 1: Basic Metric Comparison Table

```
| Metric | PRNG | TRNG | QRNG | TRNG vs PRNG | QRNG vs PRNG |
|--------|------|------|------|:------------:|:------------:|
| shannon_char | 4.637 | 4.638 | 4.639 | +0.02% | +0.04% |
```

**Reading this:** Shannon character entropy is 4.637 bits for PRNG, 4.638 for TRNG, 4.639 for QRNG. The "TRNG vs PRNG" column shows TRNG is 0.02% higher than PRNG. All values are in the "good, natural text" range (4.2–4.7). The differences are negligible (<1%).

### Example 2: Significance Test Table

```
| Comparison | Mean Δ | 95% CI | P(Δ>0) | N |
|---|---|---|---|---|
| qrng_cached_vs_prng | 0.0579 | [-0.009, 0.143] | 0.946 | 14 |
```

**Reading this:** QRNG cached has 0.0579 higher D2 than PRNG on average. The 95% CI [-0.009, 0.143] includes zero, so we can't be fully confident the effect is real. P(Δ>0) = 0.946 means there's a 94.6% probability the true difference is positive — trending toward significance but not crossing the 95% threshold. N=14 prompts were compared.

### Example 3: Wilcoxon Significance Table

```
| Comparison | Metric | Wilcoxon p | t-test p | Cohen's d | Significant? |
|---|---|---|---|---|---|
| TRNG vs PRNG | shannon_word | 0.107 | 0.057 | +0.54 | No (borderline) |
```

**Reading this:** The Wilcoxon test (non-parametric) gives p=0.107 and the t-test gives p=0.057. Neither crosses p<0.05, so formally "not significant." However, the t-test is borderline (0.057 ≈ 0.05) and Cohen's d=0.54 is a **medium** effect size, suggesting a real but small effect that needs more data to confirm.

### Example 4: Zero/Failure Values

```
| shannon_char | 0.0000 | 0.0000 | 0.0000 |
| perplexity | ∞ | ∞ | ∞ |
```

**Reading this:** All metrics are zero and perplexity is infinity. This is **catastrophic failure** — the model produced no meaningful output. All entropy sources failed on this prompt.

---

## 7. Quick Reference Card

| Metric | Good Range | Bad Range | Direction | Key Insight |
|:------:|:----------:|:---------:|:---------:|-------------|
| shannon_char | 4.2–4.7 | < 3.5 or 0 | Higher = better | Character diversity |
| shannon_word | 7.0–9.0 | < 5.0 or 0 | Higher = better | Vocabulary richness |
| ttr / word_diversity | 0.5–0.8 | < 0.3 | Higher = better | Unique word fraction |
| distinct_2 / D2 | 0.85–1.0 | < 0.7 | Higher = better | Phrase-level diversity |
| repetition_ratio | < 0.3 | > 0.5 | Lower = better | Repetition amount |
| perplexity | 50–300 | 0 or ∞ | Context-dependent | Predictability |
| burstiness | 0.15–0.40 | > 0.6 | Lower = smoother | Output smoothness |
| hidden_entropy_late | 1.5–2.2 | < 1.0 | Higher = better | Internal state diversity |
| Cohen's d | > 0.5 meaningful | < 0.2 negligible | Absolute value | Effect magnitude |
| p-value | < 0.05 significant | > 0.10 not sig | Lower = stronger | Statistical confidence |

---

*This glossary applies to all experiment reports in the entropy-seeding repository. For methodology details, see the main report: `COMPREHENSIVE_ENTROPY_SEEDING_EXPERIMENT_2026-02-09.md`*
