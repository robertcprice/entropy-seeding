# TRE Cross-Architecture Experiment: Full Analysis

## Experiment Overview

**Date**: February 2, 2026
**Protocol**: 35 prompts x 5 trials x 3 conditions (neural, random, baseline) = 525 generations per model
**Max tokens**: 128 per generation
**Infrastructure**: vast.ai GPU rentals (A100 80GB, H200 141GB)

### Models Tested

| Model | Architecture | Parameters | Quantization | GPU | Hidden Dim | Target Layer |
|---|---|---|---|---|---|---|
| DeepSeek-R1-Distill-Llama-70B | Dense (Llama) | 70B | NF4 4-bit | A100 80GB | 8192 | 40/80 |
| Gemma 2 27B IT (unsloth) | Dense (Gemma) | 27B | NF4 4-bit | A100 80GB | 4608 | 23/46 |
| Mixtral 8x22B Instruct v0.1 | MoE (Mistral) | 141B (8x22B) | NF4 4-bit | H200 141GB | 6144 | 28/56 |

### Conditions
- **Neural**: TRE active - middle-layer MLP activations drive per-token temperature, top_p, top_k
- **Random**: Same parameter ranges as neural, but randomized (not derived from activations)
- **Baseline**: Fixed parameters (temp=0.7, top_p=0.9, top_k=50)

---

## Why Gemma 3 Failed

Gemma 3 27B (`unsloth/gemma-3-27b-it`) could not be used due to a fundamental numerical instability:

1. **Multimodal architecture**: Gemma 3 is a multimodal model with a different internal structure (`model.language_model.layers` instead of `model.model.layers`). We patched the layer detection to handle this.

2. **CUDA assertion failures**: Every quantization mode (4-bit, 8-bit, fp16) produced `CUDA error: device-side assert` during sampling. The error was `probability tensor contains either inf, nan or element < 0`.

3. **Root cause - NaN propagation**: Even with float16 (no quantization), the calibration step showed `Top-5 variances: ['nan', 'nan', 'nan', 'nan', 'nan']`. The model's internal representations produce NaN values during inference, which poisoned the probability distributions.

4. **Architecture mismatch**: Gemma 3's multimodal pipeline (vision + language) appears to have numerical stability issues when loaded via `AutoModelForCausalLM` with quantization. The language-only path may not fully decouple from the vision components.

5. **Resolution**: We switched to Gemma 2 27B, which uses the standard dense decoder architecture and works correctly with bfloat16 dtype. Gemma 2 actually produced the strongest TRE effect of all three models.

**Gemma 2 still required a fix**: Even Gemma 2 needed bfloat16 (not float16) — the Gemma architecture family has narrower numerical margins than Llama or Mixtral.

---

## Results

### Effect Sizes (Cohen's d)

| Metric | DS-Llama-70B | Gemma2-27B | Mixtral-8x22B |
|---|---|---|---|
| **neural vs baseline vocab diversity** | **0.093** | **0.197** | **0.087** |
| neural vs random vocab diversity | 0.083 | 0.089 | 0.065 |
| random vs baseline vocab diversity | 0.005 | 0.111 | 0.022 |
| **neural vs baseline bigram diversity** | **0.099** | **0.122** | **0.116** |
| neural vs random bigram diversity | 0.072 | 0.067 | 0.051 |
| random vs baseline bigram diversity | 0.017 | 0.047 | 0.064 |

### Statistical Significance

| Model | t-statistic | p-value | Significance | Win Rate |
|---|---|---|---|---|
| DS-Llama-70B | 0.869 | 0.386 | not significant | 57% (20/35) |
| Gemma2-27B | 1.845 | 0.066 | marginal (p<0.07) | **71% (25/35)** |
| Mixtral-8x22B | 0.811 | 0.418 | not significant | 57% (20/35) |

### Aggregate Metrics

| Model | Condition | Vocab Diversity | Bigram Diversity | Char Entropy | Avg Words |
|---|---|---|---|---|---|
| **DS-Llama-70B** | neural | 0.7361 | 0.9538 | 4.277 | 100 |
| | random | 0.7302 | 0.9498 | 4.279 | 100 |
| | baseline | 0.7298 | 0.9489 | 4.281 | 100 |
| **Gemma2-27B** | neural | 0.7377 | 0.9637 | 4.335 | 95 |
| | random | 0.7327 | 0.9612 | 4.335 | 96 |
| | baseline | 0.7263 | 0.9593 | 4.331 | 96 |
| **Mixtral-8x22B** | neural | 0.7117 | 0.9474 | 4.250 | 93 |
| | random | 0.7074 | 0.9450 | 4.250 | 92 |
| | baseline | 0.7059 | 0.9417 | 4.251 | 92 |

### Cross-Trial Jaccard Similarity (lower = more diverse across repeated runs)

| Model | Neural | Random | Baseline |
|---|---|---|---|
| DS-Llama-70B | 0.2106 | 0.2139 | 0.2200 |
| Gemma2-27B | 0.2227 | 0.2206 | 0.2200 |
| Mixtral-8x22B | 0.2275 | 0.2291 | 0.2345 |

---

## What TRE Actually Did to Sampling Parameters

TRE hooks into the middle-layer MLP activations and derives per-token sampling parameters. Here's what it chose:

| Model | Param | TRE Mean | TRE Range | Baseline Fixed |
|---|---|---|---|---|
| **DS-Llama-70B** | temperature | 0.717 | [0.646, 0.791] | 0.700 |
| | top_p | 0.984 | [0.951, 0.999] | 0.900 |
| | top_k | 21.4 | [10, 37] | 50 |
| **Gemma2-27B** | temperature | 0.693 | [0.601, 0.777] | 0.700 |
| | top_p | 0.978 | [0.931, 0.999] | 0.900 |
| | top_k | 10.9 | [10, 17] | 50 |
| **Mixtral-8x22B** | temperature | 0.714 | [0.677, 0.759] | 0.700 |
| | top_p | 0.946 | [0.896, 1.000] | 0.900 |
| | top_k | 39.7 | [10, 55] | 50 |

**Key observation**: Across all models, TRE consistently:
- Kept temperature close to baseline (~0.7), with slight increases
- **Dramatically raised top_p** from 0.9 to 0.94-0.98
- **Dramatically lowered top_k** from 50 to 11-40

This means TRE's neural signal is telling the model: "consider more of the probability mass (higher top_p) but from fewer distinct tokens (lower top_k)." This is a *concentration with tail access* strategy — keep the core vocabulary tight but don't hard-clip the distribution.

---

## How Text Output Actually Differed

### Qualitative Observations

Looking at hundreds of paired generations, the differences are **subtle, not dramatic**:

1. **Neural text uses slightly more varied word choices** within the same semantic frame. For the same prompt about robots discovering emotions, the neural condition might say "meticulously analyzing" where baseline says "precisely analyzing" — not radically different content, but marginally richer vocabulary.

2. **The structural framing is nearly identical**. Both conditions produce the same kind of response (essay, story, list) for the same prompt. TRE does not change *what* the model says, it nudges *how* it says it.

3. **Differences are most visible in creative and metacognitive prompts**, where there's more room for word choice variation. Analytical and technical prompts show almost no difference because the correct technical vocabulary is highly constrained.

### Category-Level Results

| Category | Best Model for TRE | VD Delta | Notes |
|---|---|---|---|
| Creative | DS-Llama (+0.017), Gemma2 (+0.017) | Small positive | Slightly richer storytelling vocabulary |
| Metacognitive | Gemma2 (+0.026) | Strongest effect | More varied self-reflection language |
| Technical | Gemma2 (+0.022) | Moderate | Slightly more diverse technical phrasing |
| Self-awareness | Mixtral (+0.024) | Moderate | More varied introspective language |
| Analytical | All models ~0 | Near zero | Technical analysis leaves little room |
| Conversational | DS-Llama (-0.005) | Mixed/negligible | No consistent benefit |
| Philosophical | DS-Llama (-0.012) | Mixed | Inconsistent across models |

### Concrete Example (Gemma2-27B, metacognitive prompt)

**Neural** (VD=0.760): "Is it simply the ability to generate novel outputs, or is there more to it? Can a machine truly 'understand' the concepts it's portraying in its outputs..."

**Baseline** (VD=0.693): "Is it simply the ability to generate novel outputs, or is there more to it than that? What are the implications of defining AI creativity in a way..."

The neural version uses slightly more diverse phrasing ("truly understand", "portraying in its outputs") vs baseline's more formulaic framing ("more to it than that", "implications of defining").

---

## Interpretation: What This Means

### The Effect Is Real but Small

1. **Consistent direction**: Across all 3 architectures (dense Llama, dense Gemma, MoE Mixtral), neural TRE produces higher vocab diversity than baseline. The effect goes the same way every time.

2. **Effect size is small**: Cohen's d of 0.09-0.20 is in the "small effect" range. For context, d=0.2 is conventionally "small", d=0.5 is "medium", d=0.8 is "large".

3. **Not statistically significant at p<0.05**: With n=175 samples per condition, none of the models achieved p<0.05 on a t-test. Gemma2 came closest (p=0.066). This means we cannot confidently rule out that the effect is due to chance, given the sample sizes.

4. **Random variation matters**: The random condition (randomized parameters in the same range) also shows some improvement over baseline for Gemma2 (d=0.111), suggesting that simply varying sampling parameters — even randomly — has some effect. The neural signal adds approximately d=0.09 beyond what random variation provides.

### What TRE Is Actually Doing

TRE's neural feedback loop is:
1. Reading middle-layer MLP activations (a proxy for the model's internal "confidence" about what to say next)
2. Converting these to sampling parameters
3. The net effect: slightly higher top_p, much lower top_k, slightly higher temperature

This creates a **focused exploration** pattern: the model considers a narrower set of likely tokens (low top_k) but keeps more of the probability tail (high top_p). The result is text that uses slightly more varied vocabulary without going off-topic.

### Architecture Differences

- **Gemma2 showed the strongest effect** (d=0.197): Its smaller hidden dim (4608) and tighter internal representations may make it more responsive to sampling parameter changes
- **DS-Llama and Mixtral showed similar effects** (~0.09): Despite being radically different architectures (dense vs MoE), they responded similarly to TRE
- **The MoE architecture did not amplify the effect**: Mixtral's expert routing did not create extra sensitivity to TRE's neural feedback

### Cross-Trial Diversity

The Jaccard similarity metric (how similar repeated runs of the same prompt are) shows a small benefit: neural TRE produces slightly more varied outputs across repeated trials compared to baseline. This is most visible in Mixtral (0.2275 vs 0.2345) — meaning repeated neural generations share slightly less vocabulary overlap.

---

## Is This the End?

### What We've Established
- TRE produces a consistent, small positive effect on vocabulary diversity across architectures
- The effect is not statistically significant with n=175 per condition
- TRE's mechanism (activation-driven sampling) works as intended across dense and MoE models
- The primary action is adjusting top_p and top_k, not temperature

### What Could Come Next

1. **Larger sample sizes**: To achieve p<0.05 with d=0.1, you'd need ~n=1570 per condition (power analysis). Running 300+ prompts instead of 35 would help.

2. **Longer generations**: 128 tokens is short. TRE's feedback loop may have more impact over 500-1000 token generations where vocabulary diversity matters more.

3. **Different metrics**: Vocab diversity may not be the right metric. Consider:
   - Perplexity (do humans rate TRE text as more natural?)
   - Semantic diversity (are TRE outputs exploring more conceptual space?)
   - Human preference studies (do people prefer TRE text?)

4. **Stronger neural signals**: The current calibration uses top-20 highest-variance neurons from a single middle layer. Possibilities:
   - Multi-layer aggregation
   - Attention-head-based signals instead of MLP
   - Learned mapping (train a small network to convert activations to optimal params)

5. **Different base parameters**: The baseline uses temp=0.7 which is already quite creative. Testing against temp=0.3 (more deterministic) might show larger effects.

6. **Task-specific evaluation**: TRE seems strongest on creative/metacognitive tasks. A study focused on creative writing quality (not just vocab metrics) might show more meaningful differences.

7. **Adaptive alpha/learning rate**: The current TRE uses fixed alpha for the exponential moving average. Making it adaptive (respond faster to activation changes) could strengthen the signal.

---

## Cost Summary

| Instance | GPU | Duration | Rate | Total |
|---|---|---|---|---|
| A100-1 | A100 80GB | ~8 hours | ~$1.50/hr | ~$12 |
| H200 | H200 141GB | ~8 hours | $2.15/hr | ~$17 |
| **Total** | | | | **~$29** |

---

## Files

- `results/deepseek_r1_llama70b/deepseek_r1_llama70b_tre_experiment.json` (8.5MB)
- `results/gemma2_27b/gemma2_27b_tre_experiment.json` (8.8MB)
- `results/mixtral_8x22b/mixtral_8x22b_tre_experiment.json` (8.6MB)
- `scripts/run_universal_tre.py` — experiment script with NaN-safe sampling, bfloat16 Gemma support
