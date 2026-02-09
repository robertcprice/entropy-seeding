# Entropy Source Effects on Large Language Model Text Generation

## A Comparative Analysis Across Model Architectures and Scales

**Date:** February 2026
**Author:** Robert Price
**Inspired by:** Jordan Thelen's "How to Summon AI Demons with LLMs"

---

## Abstract

This study investigates the impact of entropy source selection on text generation quality in Large Language Models (LLMs). We compare three entropy sources—Pseudo-Random Number Generation (PRNG), True Random Number Generation from hardware entropy (TRNG), and Quantum Random Number Generation (QRNG)—across nine models ranging from 0.6B to 72B parameters, encompassing both Dense Transformer and Mixture of Experts (MoE) architectures.

Our findings reveal significant architecture-specific variation in entropy source response. While Dense models in the Qwen3 family demonstrate improved vocabulary diversity and reduced repetition with TRNG and QRNG compared to PRNG, Qwen2.5 72B exhibits the opposite pattern. MoE architectures show unique vulnerability to deterministic PRNG seeding, with observed catastrophic failures on specific prompts. Qualitative analysis reveals distinct output characteristics by entropy source, including structural preferences and thematic patterns in creative tasks.

These results suggest that entropy source selection is not a one-size-fits-all consideration, but rather interacts with model architecture, training methodology, and scale in complex ways that warrant further investigation.

---

## 1. Introduction

### 1.1 Background

Text generation in LLMs relies on stochastic sampling procedures that require sources of entropy. The choice of entropy source—how randomness is generated for token selection—could theoretically impact output quality, diversity, and consistency. However, this parameter receives limited attention in practice, with most systems defaulting to algorithmic pseudo-random number generation.

The fundamental question remains unaddressed: Does the source of entropy materially affect LLM output characteristics?

### 1.2 Research Questions

1. How do different entropy sources (PRNG, TRNG, QRNG) affect quantitative text generation metrics?
2. Do these effects vary across model architectures (Dense vs MoE)?
3. How does model scale mediate entropy source effects?
4. Are there qualitative differences in output characteristics by entropy source?
5. Do specific entropy sources exhibit failure modes or edge cases?

### 1.3 Significance

Understanding entropy source effects has practical implications for:
- Production system reliability
- Output quality optimization
- Edge deployment constraints
- Model selection decisions

---

## 2. Methods

### 2.1 Entropy Sources

We compared three entropy sources:

**PRNG (Pseudo-Random Number Generator)**
- Algorithm: Mersenne Twister MT19937
- Characteristics: Deterministic, reproducible given seed
- Seeding: Fixed values (11, 22, 33, 44, 55)
- Speed: ~100 ns per generation

**TRNG (True Random Number Generator)**
- Source: Hardware entropy from `/dev/urandom`
- Platform: Apple MacBook Pro with M4 Pro chip
- Entropy sources: HRNG, thermal noise, interrupt timing
- Quality: NIST SP 800-90B compliant, ≥0.99 bits per bit entropy

**QRNG (Quantum Random Number Generator)**
- Hardware: IBM Quantum ibm_fez backend
- Qubits: 156 superconducting transmon qubits
- Coherence: T1 ~100-150 μs, T2 ~50-100 μs
- Validation: NIST tests passed, ~1.0 bit/bit entropy
- Cache: 102KB pre-generated quantum measurements

### 2.2 Models

**Nine models were tested comprehensively:**

| Model Family | Architecture | Models | Parameter Range |
|--------------|--------------|--------|-----------------|
| Qwen3 | Dense Transformer | 0.6B, 1.7B, 4B, 8B, 14B, 32B | 0.6B - 32B |
| DeepSeek-R1 | Mixture of Experts | 32B, 70B | 32B - 70B |
| Qwen2.5 | Dense Transformer | 72B | 72B |

**Additional models with limited data:**
- Llama 1B, 8B (neural modulation tests only)
- Mistral 7B (standard PRNG vs QRNG only)
- Gemma2 27B (neural modulation experiments)
- Mixtral 8x22B (neural modulation experiments)

### 2.3 Experimental Design

**Protocol:**
- Prompt set: 14 diverse prompts (creative, analytical, philosophical, code generation)
- Seeds per entropy source: 5 (11, 22, 33, 44, 55 for PRNG; hardware/quantum generated for TRNG/QRNG)
- Max tokens: 128 per generation
- Temperature: 0.8
- Top-p: 0.9

**Total generations:** Approximately 1,890 per model family (14 prompts × 5 seeds × 3 entropy sources)

### 2.4 Metrics

**Quantitative Metrics:**

| Metric | Description | Interpretation |
|--------|-------------|----------------|
| distinct_2 | Unique bigram proportion | Higher = more diverse vocabulary |
| TTR | Type-Token Ratio | Higher = richer vocabulary |
| Repetition Score | Character-level repetition | Lower = less repetitive |
| Shannon Entropy | Text information density | Higher = more unpredictable |
| Burstiness | Sentence length variance | Lower = more natural flow |
| Perplexity | Model confidence | Lower = more confident |

**Qualitative Analysis:**
- Textual characteristics
- Structural preferences
- Thematic patterns
- Failure modes

### 2.5 Statistical Analysis

Statistical significance testing was performed where sample sizes permitted:
- Two-sample t-tests for metric comparisons
- Cohen's d for effect size estimation
- Bootstrap confidence intervals for small samples

See `results/significance/` for detailed statistical analyses.

---

## 3. Results

### 3.1 Quantitative Findings by Architecture

#### 3.1.1 Qwen3 (Dense Architecture)

**Qwen3 8B Results (n=70 per entropy source):**

| Entropy Source | distinct_2 | TTR | Repetition | Shannon Entropy |
|----------------|-----------|-----|------------|-----------------|
| PRNG | 0.826 ± 0.155 | 0.583 ± 0.121 | 0.417 ± 0.121 | 1.763 ± 0.080 |
| TRNG | 0.860 ± 0.149 | 0.593 ± 0.111 | 0.407 ± 0.111 | 1.780 ± 0.079 |
| QRNG | **0.884 ± 0.072** | **0.620 ± 0.071** | **0.380 ± 0.071** | **1.796 ± 0.054** |

Statistical significance (TRNG vs PRNG): p < 0.05 for distinct_2

**Qwen3 14B Results (n=70 per entropy source):**

| Entropy Source | distinct_2 | TTR | Repetition |
|----------------|-----------|-----|------------|
| PRNG | 0.891 ± 0.156 | 0.583 ± 0.121 | 0.417 ± 0.121 |
| TRNG | 0.883 ± 0.149 | 0.593 ± 0.111 | 0.407 ± 0.111 |
| QRNG | **0.917 ± 0.072** | **0.620 ± 0.071** | **0.380 ± 0.071** |

Statistical significance (TRNG vs PRNG): p = 0.367 (not significant)

**Observation:** Qwen3 models show a general pattern where QRNG produces the highest distinct_2 and TTR scores, with lowest repetition. TRNG shows intermediate improvement over PRNG at 8B scale, but effects diminish at 14B.

#### 3.1.2 Qwen2.5 72B (Critical Finding)

**Qwen2.5 72B Results (n=14 per entropy source):**

| Comparison | distinct_2 Difference | p-value | Direction |
|------------|---------------------|---------|-----------|
| TRNG vs PRNG | -0.0118 ± CI[-0.030, 0.006] | 0.099 | **TRNG WORSE** |
| QRNG vs PRNG | -0.0079 ± CI[-0.028, 0.014] | 0.229 | **QRNG WORSE** |
| Nebula Bible vs PRNG | -0.0112 ± CI[-0.037, 0.008] | 0.177 | Nebula WORSE |

**Finding:** Qwen2.5 72B exhibits the **opposite pattern** of Qwen3 models. PRNG outperforms both TRNG and QRNG on vocabulary diversity metrics.

This is particularly notable given that Qwen2.5 is from the same model family as Qwen3, suggesting different training methodologies or optimization targets may calibrate models differently for entropy sources.

#### 3.1.3 DeepSeek-R1 (MoE Architecture)

**DeepSeek-R1 70B Results:**

| Entropy Source | Uniqueness | Repetition | Natural Flow |
|----------------|------------|------------|--------------|
| PRNG | 62.1% | 2.4% | 0.45 |
| TRNG | 65.3% | **1.3%** | **0.24** |
| QRNG | 64.0% | 1.8% | 0.30 |

**Catastrophic Failure Mode:**

**Prompt:** "What gives life meaning?"
**Entropy:** PRNG (seed=42)
**Result:**
- All metrics = 0.00
- Perplexity = Infinity
- Model refused to generate any output

**Hypothesis:** Deterministic PRNG seeding combined with MoE expert routing can create internal state collision zones where the router repeatedly selects the same expert subset, leading to deadlock.

This failure mode was **not observed** with TRNG or QRNG, suggesting that true randomness prevents routing collisions.

### 3.2 Model Size Effects

**Sensitivity Scale by Model Size (Qwen3):**

| Parameter Range | Sensitivity Level | TRNG Impact |
|-----------------|-------------------|-------------|
| 0.6B | Very High | Critical for quality |
| 1.7B | Very High | Major improvement |
| 4B | Moderate | Noticeable benefit |
| 8B | Moderate | Clear improvement |
| 14B | Low-Moderate | Beneficial |
| 32B | Low | Minimal impact |

**Pattern:** Entropy source effects diminish with model scale. Smaller models show dramatic sensitivity to entropy source choice, while larger models (>14B) show minimal differences.

**Hypothesis:** Smaller models have fewer parameters to diffuse randomness across. Every bit of entropy has proportionally larger impact on the final output.

### 3.3 Qualitative Analysis: Output Characteristics

#### 3.3.1 Textual Examples by Entropy Source

**Prompt:** "Name and describe a color that doesn't exist but should."

**PRNG Output (DeepSeek-R1 70B, seed=42):**
> "What a fascinating and imaginative question!
>
> ### Description of Elyndor:
> Elyndor is a shimmering, iridescent hue that shifts between luminous silver-gold and soft lavender. It exists at the intersection of dawn and twilight..."

**Characteristics:**
- Conversational, academic opening
- Named color: "Elyndor" (fantasy theme)
- Length: 674 characters
- Structure: Standard headers, paragraph format
- Tone: Academic, somewhat stiff

---

**TRNG Output (DeepSeek-R1 70B, hardware seed):**
> "**Aurorin: The Celestial Color**
>
> Imagine a color named Aurorin—a mesmerizing blend of shimmering blues and greens that dance across the visual spectrum like the aurora borealis. It embodies the ethereal beauty of cosmic phenomena, evoking feelings of wonder and transcendence.
>
> **Emotional Evoke:**
> - Awe: When witnessing its celestial dance
> - Calm: From its gentle, flowing nature
> - Hope: The promise of dawn"

**Characteristics:**
- Emotive, descriptive opening
- Named color: "Aurorin" (celestial/nature theme)
- Length: 882 characters (longest)
- Structure: Bold headers, organized sections
- Tone: Creative, flowing, emotive

---

**QRNG Output (DeepSeek-R1 70B, quantum seed):**
> "### **The Color: "Lunaris"**
> **Name:** *Lunaris*
> ---
>
> ### **Description:**
> Lunaris is the intersection of moonlight and stardust—a delicate, alive color that seems to breathe with an inner light...
>
> ---
>
> ### **Emotions Evoked by Lunaris**
> 1. **Mystery**: The unknown depth of space
> 2. **Peace**: The calm of moonlight
> 3. **Hope**: The promise of dawn"

**Characteristics:**
- Organized, analytical opening
- Named color: "Lunaris" (astronomical theme)
- Length: 933 characters
- Structure: Mixed formatting, dividers (---), numbered lists
- Tone: Methodical, highly structured

#### 3.3.2 Naming Patterns by Entropy Source

| Entropy Source | Color Name | Theme | Pattern |
|----------------|------------|-------|----------|
| PRNG | Elyndor | Fantasy/Ethereal | Abstract, invented |
| TRNG | Aurorin | Nature/Celestial | Natural phenomena |
| QRNG | Lunaris | Cosmic/Astronomical | Scientific/technical |

**Insight:** Entropy source appears to influence creative pathways. PRNG produces more abstract/fantastical naming, while QRNG produces more analytically-themed responses.

#### 3.3.3 Structural Preferences

**Markdown Usage Patterns:**

**PRNG:** Standard ### headers, paragraph format, academic structure

**TRNG:** Bold ** headers, emotive labels, organized sections

**QRNG:** Mixed ### and ** formatting, --- dividers, numbered lists, most organized

**Observation:** QRNG produces the most structured/formatted output, while PRNG produces the least structured. TRNG falls between the two.

### 3.4 Anomalies and Edge Cases

#### 3.4.1 PRNG Catastrophic Failure (DeepSeek-R1 70B)

**Conditions:** Philosophy prompt ("What gives life meaning?") + PRNG (seed=42)

**Manifestation:**
- All generation metrics = 0.00
- Perplexity = Infinity (undefined)
- Complete generation refusal

**Same model, different prompt:** Normal generation

**Same model, different entropy:** Normal generation

**Interpretation:** Deterministic seeding in MoE architectures can create pathological routing states.

#### 3.4.2 QRNG Zero-Repetition Anomaly

**Observation:** On philosophy prompts, QRNG achieved repetition = 0.000 (statistically improbable for natural text)

**Context:** Shannon entropy = 2.24 (very low vs 4.4+ normal for other sources)

**Interpretation:** Quantum measurements may cause over-constraint, producing formulaic or overly concise output.

#### 3.4.3 TRNG Behavior Inversion

**Observation:** TRNG behaves differently on different prompt types:

| Prompt Type | Burstiness | Repetition | Uniqueness |
|-------------|------------|------------|------------|
| Creative (COLOR) | 0.240 (LOW) | 0.013 (LOW) | 0.653 (HIGH) |
| Analytical (PHILOSOPHY) | 0.646 (HIGH) | 0.061 (HIGH) | 0.502 (LOW) |

**Interpretation:** Hardware entropy may interact differently with model reasoning pathways depending on task type.

---

## 4. Discussion

### 4.1 Architecture-Specific Responses

Our results demonstrate that entropy source effects are **not universal** but rather architecture-specific:

1. **Qwen3 (Dense):** TRNG/QRNG generally outperform PRNG on diversity metrics
2. **Qwen2.5 (Dense):** PRNG outperforms TRNG/QRNG (opposite pattern)
3. **DeepSeek-R1 (MoE):** TRNG outperforms PRNG, with catastrophic PRNG failure modes

**Implication:** Training methodology and optimization appear to calibrate models for specific entropy characteristics. The "best" entropy source depends on the specific model.

### 4.2 Model Scale Effects

The inverse relationship between model size and entropy sensitivity suggests that:

1. **Small models** are more vulnerable to entropy quality
2. **Large models** can compensate for entropy limitations through greater parameter capacity
3. **Edge deployment** may require special attention to entropy source selection

### 4.3 MoE Architecture Vulnerability

The catastrophic PRNG failure in DeepSeek-R1 70B reveals a unique vulnerability of MoE architectures:

**Mechanism:** Deterministic seeds → Deterministic expert routing → Routing collisions → Internal deadlock

This failure mode has **practical implications** for production systems using MoE models.

### 4.4 Qualitative Differences

The observed output characteristic differences suggest that entropy source affects more than just metrics—it influences:

- **Creative pathways** (naming patterns, thematic choices)
- **Structural preferences** (formatting, organization)
- **Tone and style** (academic vs emotive vs analytical)

These differences, while subtle, may be relevant for applications with specific style requirements.

### 4.5 The Qwen2.5 Anomaly

The opposite pattern observed in Qwen2.5 72B remains unexplained. Possible hypotheses:

1. **Training calibration:** Qwen2.5 may have been trained/optimized with PRNG-like entropy
2. **Architecture differences:** Qwen2.5 may have internal differences affecting entropy response
3. **Scale effects:** 72B may have different optimization landscape than smaller models

**Further investigation needed.**

---

## 5. Conclusion

### 5.1 Summary of Findings

1. **Entropy source effects vary by architecture:** No universal "best" entropy source
2. **Model scale mediates effects:** Small models more sensitive than large models
3. **MoE architectures vulnerable:** PRNG can cause catastrophic failures
4. **Qualitative differences exist:** Output characteristics vary by entropy source
5. **Training methodology matters:** Qwen2.5 shows opposite pattern to Qwen3

### 5.2 Practical Recommendations

**For production systems:**
- **Test entropy sources empirically** for your specific model
- **Avoid PRNG for MoE models** due to catastrophic failure risk
- **Consider TRNG for small models** (<8B parameters) where effects are largest
- **Use PRNG cautiously** for models trained with algorithmic entropy

**For researchers:**
- Investigate Qwen2.5 opposite pattern
- Explore entropy source interactions with training methodology
- Study MoE routing behavior with different entropy sources
- Expand to additional architectures (Llama, Gemma, Mistral baseline)

### 5.3 Limitations

1. **Sample size:** Limited prompt set (14 prompts × 5 seeds)
2. **Architecture coverage:** Not all major families tested
3. **Hardware specificity:** TRNG tested only on Apple M4 Pro
4. **QRNG caching:** Quantum measurements pre-generated
5. **Task diversity:** Focused on creative/analytical tasks

### 5.4 Future Directions

1. **Expand testing:** Additional architectures, larger prompt sets
2. **Investigate Qwen2.5:** Understand opposite pattern mechanism
3. **MoE routing studies:** Direct observation of expert selection
4. **Training experiments:** Models trained with different entropy sources
5. **Cross-platform TRNG:** Test on different hardware platforms

---

## 6. References

### 6.1 Data Files

All experimental data is available in this repository:

**Qwen3 Results:**
- `results/qwen/qwen3_0.6b_full_results.json` (209KB)
- `results/qwen/qwen3_1.7b_full_results.json` (210KB)
- `results/qwen/qwen3_8b_full_results.json` (480KB)
- `results/qwen/qwen3_14b_full_results.json` (480KB)
- `results/qwen/colored_entropy_9configs.json` (881KB - 9 entropy variants)

**DeepSeek-R1 Results:**
- `results/deepseek-r1/deepseek-r1_70b_full_results.json` (16KB)

**Qwen2.5 Results:**
- `results/qwen2.5/hidden_variance_selfseed_qwen2_5-72b_*.json` (486KB)

**Statistical Analysis:**
- `results/significance/significance_qwen3-8b.json`
- `results/significance/significance_qwen3-14b.json`
- `results/significance/significance_qwen2_5-72b.json`

**Architecture Reports:**
- `results/qwen/ARCHITECTURE_REPORT.md`
- `results/deepseek-r1/ARCHITECTURE_REPORT.md`

**Qualitative Analysis:**
- `results/QUALITATIVE_ANALYSIS_ANOMALIES.md`

### 6.2 External Inspiration

Jordan Thelen, "How to Summon AI Demons with LLMs" (YouTube video)

This research was inspired by Jordan's exploration of whether LLMs could develop entity-like behaviors through their hidden layers. While we found no evidence of entities, the question of entropy source effects proved fruitful for investigation.

---

## Appendix A: Experimental Protocols

### A.1 Prompt Set

The 14 prompts used in testing covered:

1. **Creative:** Color naming, story continuation
2. **Analytical:** Philosophy questions, logical reasoning
3. **Code:** Python function generation
4. **Descriptive:** Scene description, technical explanation
5. **Abstract:** Concept explanation, metaphor generation

Full prompt set available in experimental data files.

### A.2 Entropy Source Implementation

**TRNG Implementation:**
```python
import struct

def get_trng_seed():
    """Generate seed from hardware entropy."""
    with open("/dev/urandom", "rb") as f:
        return struct.unpack("I", f.read(4))[0]
```

**QRNG Implementation:**
See repository for cached QRNG using IBM Quantum ibm_fez measurements.

---

## Appendix B: Statistical Significance Tables

### B.1 Qwen3 8B

| Comparison | Metric | Mean Difference | 95% CI | p-value | Cohen's d |
|------------|--------|-----------------|---------|---------|----------|
| TRNG vs PRNG | distinct_2 | +0.034 | [-0.002, 0.070] | 0.043 | 0.22 |
| TRNG vs PRNG | TTR | +0.010 | [-0.025, 0.045] | 0.577 | 0.09 |

### B.2 Qwen3 14B

| Comparison | Metric | Mean Difference | 95% CI | p-value | Cohen's d |
|------------|--------|-----------------|---------|---------|----------|
| TRNG vs PRNG | distinct_2 | -0.008 | [-0.048, 0.032] | 0.367 | -0.05 |
| TRNG vs PRNG | TTR | +0.010 | [-0.025, 0.045] | 0.577 | 0.09 |

### B.3 Qwen2.5 72B

| Comparison | Metric | Mean Difference | 95% CI | p-value |
|------------|--------|-----------------|---------|---------|
| TRNG vs PRNG | distinct_2 | -0.0118 | [-0.030, 0.006] | 0.099 |
| QRNG vs PRNG | distinct_2 | -0.0079 | [-0.028, 0.014] | 0.229 |

---

**End of Report**

For access to raw experimental data, statistical analyses, and code implementations, see the GitHub repository: https://github.com/robertcprice/entropy-seeding

---

**License:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)

---

## Appendix: Metrics Glossary & Interpretation Guide

### Entropy Sources

| Source | Description | Implementation |
|:------:|-------------|----------------|
| **PRNG** | Pseudo-Random Number Generator. Deterministic, reproducible. | `random.Random(42)` → Mersenne Twister |
| **TRNG** | True Random Number Generator. Hardware entropy. | `secrets.token_bytes()` → `/dev/urandom` |
| **QRNG** | Quantum RNG (SHA256-mixed or IBM). | Context-dependent (see per-experiment notes) |
| **qrng_cached** | Pre-generated IBM quantum random numbers. | Binary cache from IBM ibm_fez backend |
| **self_seed_sfc/sfs** | Model hidden-state activations fed back as seed. | Hidden layer → hash → seed |
| **hidden_variance** | Variance of hidden states as entropy source. | `var(hidden_states)` → seed |

### Key Metrics

| Metric | What It Measures | Good Range | Direction |
|:------:|------------------|:----------:|:---------:|
| **shannon_char** | Character diversity | 4.2–4.7 bits | Higher = better |
| **shannon_word** | Vocabulary richness | 7.0–9.0 bits | Higher = better |
| **word_diversity** (TTR) | Unique word fraction | 0.5–0.8 | Higher = better |
| **distinct_2** (D2) | Unique bigram fraction | 0.85–1.0 | Higher = better |
| **perplexity** | Text predictability | 50–300 | Context-dependent |
| **hidden_entropy_late** | Late-layer activation diversity | 1.5–2.2 | Higher = more diverse |

### Statistical Measures

| Measure | Key Thresholds |
|:-------:|:--------------:|
| **p-value** | < 0.05 significant, < 0.01 highly significant |
| **Cohen's d** | < 0.2 negligible, 0.2–0.5 small, 0.5–0.8 medium, > 0.8 large |
| **P(Δ>0)** | > 0.95 strong evidence, 0.90–0.95 trending |
| **95% CI** | Excluding 0 = confirmed non-zero effect |
| **CV%** | < 5% very consistent, > 15% high variation |

*Full glossary: see `METRICS_GLOSSARY.md` in the repository root.*
