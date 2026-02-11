# Pre-Registration: Entropy Source Effects on LLM Text Generation

**Version:** 1.0
**Date:** 2026-02-09
**Authors:** Robert Price
**Status:** DRAFT — freeze before data collection

---

## 1. Study Information

### 1.1 Title
Do Different Entropy Source Distributions for Seed Values Affect Large Language Model Text Generation Properties?

### 1.2 Research Questions

**Primary RQ:** Do seeds drawn from different random number generators (PRNG, TRNG, HMIX) produce statistically different text output distributions when used as LLM sampling seeds?

**Secondary RQs:**
- RQ2: Does the effect vary by model architecture (Qwen, Llama, Gemma, Mistral, Phi)?
- RQ3: Does the effect vary by model scale (1.7B to 8B parameters)?
- RQ4: Does the effect vary by prompt domain (creative, factual, code, etc.)?
- RQ5: Are observed effects explained by seed distribution properties (uniformity, autocorrelation)?

### 1.3 Hypotheses

**H0 (Null):** Text output distributions are identical across entropy sources, controlling for seed value. Any differences are attributable to sampling variability.

**H1a (Distributional):** Seeds from HMIX (SHA256-mixed) produce more uniformly distributed 32-bit values than PRNG (Mersenne Twister), resulting in lower cross-sample variance in text metrics.

**H1b (Architecture-dependent):** Some model architectures (e.g., Gemma3) show statistically detectable differences in text diversity metrics across entropy sources, while others do not.

**H1c (Scale-dependent):** Entropy source effects are inversely related to model scale: smaller models show larger effects.

### 1.4 Key Clarifications

This experiment tests whether **different distributions of seed values** produce different text outputs. It does NOT test whether entropy "quality" matters — once a seed becomes a 32-bit integer for ollama's `--seed` parameter, its provenance is invisible to the model. The only mechanism through which effects can occur is via the **aggregate distributional properties** of the seed values.

---

## 2. Design Plan

### 2.1 Study Type
Within-subjects (repeated measures) experimental design with three conditions (entropy sources) crossed with prompts.

### 2.2 Conditions
| Source | Implementation | Key Property |
|--------|---------------|--------------|
| PRNG | `random.Random(seed).getrandbits(64) % 2**32` | Deterministic, reproducible sequence |
| TRNG | `secrets.token_bytes(8)` → 32-bit | Hardware entropy, independent draws |
| HMIX | `SHA256(timestamp + secrets + counter)` → 32-bit | Hash-mixed, high uniformity |

### 2.3 Prompts
30 single-turn prompts balanced across 9 domains:
- Creative (4), Philosophical (4), Technical (4), Code (4)
- Factual QA (4), Summarization (3), Structured (3)
- Reasoning (2), Naming (2)

3 multi-turn conversations (storytelling, debate, worldbuilding), 3 turns each.

### 2.4 Models
Primary targets (comprehensive, 360+ generations each):
- Qwen3:1.7B, Qwen3:4B, Qwen3:8B
- Gemma3:4B
- Llama3.2:3B, Llama3.1:8B
- Mistral:7B
- Phi4-mini:3.8B

### 2.5 Samples
- **Per condition:** 10 samples per prompt per source per PRNG stream
- **PRNG streams:** 5 independent seeds (42, 123, 7, 999, 314)
- **Total per model:** 30 prompts × 3 sources × 10 samples × 5 streams = 4,500 single-turn + 3 convs × 3 turns × 3 sources × 10 samples × 5 streams = 1,350 multi-turn = **5,850 generations**

### 2.6 Controls
- **Temperature:** Fixed at 0.7 for all models
- **Source order:** Randomized per prompt (seed=12345)
- **CoT stripping:** `<think>` blocks removed before metric computation
- **PRNG streams:** Multiple independent streams to average over stream-specific bias

---

## 3. Sampling Plan

### 3.1 Power Analysis

**Target:** 80% power to detect d=0.50 (medium effect) at α=0.05 (two-sided).

For **paired t-test** with n paired observations:
- n=15 prompts: MDE = d=0.78 (inadequate for medium effects)
- n=30 prompts: MDE = d=0.53 (marginal for medium effects)
- n=50 prompts: MDE = d=0.40 (adequate for small-medium effects)

For **mixed-effects model** using all samples:
- With 30 prompts × 10 samples = 300 observations per source, effective n is between 30 (if prompt dominates) and 300 (if within-prompt variance dominates)
- Estimated MDE ≈ d=0.25-0.40 with mixed-effects approach

**Decision:** 30 prompts with 10 samples each, analyzed via mixed-effects model, provides adequate power for d≥0.40.

### 3.2 Stopping Rule
Run all planned generations for each model. No early stopping based on intermediate results.

### 3.3 Exclusion Criteria
- Generations that return `[TIMEOUT]` or `[ERROR]`
- Generations with < 10 words after CoT stripping (too short for reliable metrics)
- Models that fail > 20% of generations (exclude entire model)

---

## 4. Variables

### 4.1 Independent Variable
**Entropy source:** PRNG, TRNG, HMIX (within-subjects, 3 levels)

### 4.2 Dependent Variables (Metrics)

| Metric | Description | Length-Corrected? |
|--------|-------------|-------------------|
| `shannon_char` | Character-level Shannon entropy | No (inherently normalized) |
| `shannon_word` | Word-level Shannon entropy (Miller-Madow corrected) | No |
| `word_diversity` | Type-Token Ratio | **No** — report but de-emphasize |
| `mtld` | Measure of Textual Lexical Diversity | **Yes** — primary diversity metric |
| `distinct_2` | Fraction of unique bigrams | Partially (less sensitive than TTR) |
| `repetition_ratio` | Fraction of repeated trigrams | N/A (bounded) |
| `length_words` | Word count (after CoT stripping) | N/A (control variable) |

**Primary metrics:** `mtld`, `distinct_2`, `shannon_word`
**Secondary metrics:** `shannon_char`, `repetition_ratio`, `length_words`
**Report but de-emphasize:** `word_diversity` (TTR, due to length confound)

### 4.3 Covariates
- Prompt domain (categorical: 9 levels)
- Prompt constraint level (open, medium, high)
- Model architecture
- Model scale (parameter count)
- PRNG stream seed (for stream-level random effect)

---

## 5. Analysis Plan

### 5.1 Primary Analysis: Mixed-Effects Model

```
metric ~ source + (1|prompt) + (1|prompt:stream)
```

Where:
- `source` = fixed effect (PRNG, TRNG, HMIX)
- `prompt` = random intercept (accounts for prompt-level variance)
- `prompt:stream` = random intercept nested within prompt (accounts for PRNG stream variance)

**Inference:** Omnibus F-test for `source` effect, followed by pairwise contrasts with Tukey HSD correction.

### 5.2 Secondary Analysis: Paired Tests

For backward compatibility with v1:
1. Compute prompt-level means (average across samples within each prompt × source)
2. Run Wilcoxon signed-rank and paired t-tests on prompt means
3. Compute Cohen's d_z (paired)

### 5.3 Multiple Comparison Correction

**Benjamini-Hochberg FDR** at α=0.05, applied separately to:
- All paired test p-values (across metrics × comparisons)
- All mixed-effects p-values (across metrics)
- Cross-model comparisons

### 5.4 Power Reporting

For every test, report:
- Observed effect size (Cohen's d)
- Post-hoc power at observed effect
- Minimum Detectable Effect at 80% power
- Whether the test is adequately powered

### 5.5 Effect Size Classification

| |d| | Interpretation |
|-----|----------------|
| < 0.2 | Negligible |
| 0.2–0.5 | Small |
| 0.5–0.8 | Medium |
| ≥ 0.8 | Large |

### 5.6 Seed Distribution Analysis

Before interpreting any generation results:
1. Test each source's seed distribution for uniformity (KS, chi-squared)
2. Test autocorrelation (lags 1–10)
3. Test pairwise distribution differences (2-sample KS)
4. Report bit-level bias

If seed distributions are indistinguishable (all pairwise KS p > 0.05), then any observed text differences cannot be attributed to distributional properties and are likely spurious.

### 5.7 Domain Interaction Analysis

Test source × domain interaction:
```
metric ~ source * domain + (1|prompt)
```

Report which domains (if any) show entropy source sensitivity.

---

## 6. Robustness Checks

### 6.1 Control Experiment
Run same seed values under different source labels. If ollama is deterministic, same seed → same output regardless of label. This verifies the causal chain.

### 6.2 Length Correction
For any significant TTR result, verify it survives length correction by:
1. Checking MTLD (length-independent) for the same comparison
2. Running TTR analysis with length as a covariate: `TTR ~ source + length_words + (1|prompt)`

### 6.3 CoT Sensitivity Analysis
For Qwen3 models, report both:
- Metrics on full output (including thinking blocks)
- Metrics on stripped output (creative content only)
- Difference between the two as evidence of CoT dilution

### 6.4 Stream Sensitivity
Verify that results hold across PRNG streams:
- Report per-stream effect sizes
- Test stream × source interaction

---

## 7. Reporting Standards

### 7.1 For Each Model, Report
1. Grand means per source per metric (with SDs and n)
2. Paired test results with raw AND BH-adjusted p-values
3. Mixed-effects results with BH-adjusted p-values
4. Cohen's d with 95% CI
5. Post-hoc power at observed effect
6. MDE at 80% power
7. Seed distribution characterization

### 7.2 Language Requirements
- "No significant difference" → "No difference detected at the current sample size (power = X%)"
- Always pair null results with power analysis
- Never claim "no effect" without adequate power (≥80%)
- Explicitly distinguish "statistically significant" from "practically meaningful"

### 7.3 Figures
- Forest plot of effect sizes across models and metrics
- Seed distribution histograms and QQ plots
- Power curves showing MDE as a function of n

---

## 8. Timeline and Amendments

- **Pre-registration date:** 2026-02-09
- **Data collection start:** After pre-registration freeze
- **Amendments:** Any changes to the analysis plan after data collection starts must be documented as deviations and reported separately as exploratory analyses

---

## 9. Code and Data Availability

- Experiment script: `scripts/run_comprehensive_experiment_v2.py`
- Analysis script: `scripts/statistical_analysis_v2.py`
- Seed analysis: `scripts/analyze_seed_distributions.py`
- Control experiment: `scripts/run_control_experiment.py`
- All raw data saved as timestamped JSON files in `results/`
