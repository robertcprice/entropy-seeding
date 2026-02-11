# V1 Experiment Methodology Errors

**Date:** 2026-02-09
**Status:** Superseded by v2 scripts

This documents what was wrong with the v1 experiment design and why all v1 scripts have been deleted. The v1 result data is preserved in `results/valid_entropy_comparisons/` for reference but should not be used for new conclusions.

---

## Critical Errors

### 1. The Seed Bottleneck (fundamental design flaw)

All three entropy sources (PRNG, TRNG, QRNG) produce a 64-bit integer that gets truncated to 32 bits and passed to `ollama run --seed N`. Ollama calls `torch.manual_seed(N)` internally. The model has no way to know where N came from.

The only way different sources could produce different outputs is if they produce different **distributions** of 32-bit numbers. We tested this with n=5,000 seeds per source and found all three distributions are statistically indistinguishable (KS p-values 0.15-0.90).

**Impact:** The hypothesis "entropy source quality affects LLM output" has no mechanism to be true at the seed level.

### 2. Severely Underpowered (n=15 paired observations)

The v1 analysis averaged 5 samples per prompt into a single mean, then ran paired tests on 15 prompt means. At n=15:

- Minimum detectable effect at 80% power: d=0.78 (huge)
- Power for d=0.50 (medium effect): ~40-50%
- Power for d=0.30 (small effect): ~15%

Most reported effects were d<0.5. The experiment literally could not detect what it was looking for. "No significant difference" was reported as if it meant "no effect" — but it actually meant "we can't tell."

No power analysis was reported.

### 3. No Multiple Comparison Correction

12 tests per model x 8 models = 96 tests. At alpha=0.05, ~4.8 false positives expected by chance. The v1 analysis found 3-5 "significant" results — consistent with pure chance.

When we applied Benjamini-Hochberg FDR correction to the Gemma3 data (the model with the most "significant" results), **zero tests survived**.

### 4. Aggregating to Prompt Means Discarded 80% of Data

Each model generated 75 observations per source (15 prompts x 5 samples), but only 15 values (prompt means) entered the paired tests. A mixed-effects model using all 75 observations would have ~2x the statistical power.

---

## Major Errors

### 5. TTR Length Confound

Type-Token Ratio (word_diversity) decreases with text length (Heaps' Law). TRNG generated ~3-4% longer outputs on several models. No length-corrected diversity metric (MTLD, HD-D) was computed. Some reported diversity differences may be pure length artifacts.

### 6. Chain-of-Thought Contamination

Qwen3 models produce `<think>...</think>` blocks that are 60-75% identical regardless of seed. All metrics were computed on the full output including thinking blocks, diluting measured effects by ~50% for 3 of 8 models.

### 7. Source Order Not Randomized

Sources always ran in order PRNG → TRNG → QRNG. GPU warm-up, thermal throttling, and cache state were confounded with source.

### 8. "QRNG" Was Mislabeled

The v1 "QRNG" source was `SHA256(timestamp + secrets + counter)` — a hash-mixed entropy source with zero quantum component. The H200 experiments used real IBM quantum bits. Using the same label for both caused confusion in cross-setting comparisons.

### 9. Temperature Not Controlled

Each model used its own default temperature (Qwen3: 0.6, Mistral: 0.7, Llama: 0.8). Temperature interacts with seed sensitivity. Cross-model comparisons were confounded.

---

## Minor Errors

### 10. Single PRNG Stream

All models shared one Mersenne Twister sequence (seed=42). If that particular sequence had quirks, the bias was systematic across all models.

### 11. Unbalanced Prompt Set

67% creative/philosophical, 13% naming (with floor/ceiling effects on short outputs). Missing: code generation, factual QA, summarization, structured output, reasoning.

### 12. No Pre-Registration

Hypotheses and analysis plans were not specified before data collection. All findings were post-hoc.

### 13. Shannon Entropy Bias

No Miller-Madow correction applied to Shannon entropy estimates. Minor for 200+ word texts, but matters for the short naming prompts.

---

## What V2 Fixes

| Error | V2 Fix |
|-------|--------|
| Seed bottleneck | Documented as design limitation; direct injection experiment bypasses it |
| Underpowered | Power analysis reported for every test; MDE computed |
| No FDR correction | Benjamini-Hochberg on all p-values |
| 80% data discarded | Mixed-effects model uses all individual samples |
| TTR length confound | MTLD (length-corrected) added as primary diversity metric |
| CoT contamination | `<think>` blocks stripped before metric computation |
| Source order | Randomized per prompt |
| QRNG mislabel | Renamed to HMIX (hash-mixed) |
| Temperature confound | Explicit temperature=0.7 for all models |
| Single PRNG stream | 5 independent streams (seeds 42, 123, 7, 999, 314) |
| Unbalanced prompts | 30 prompts across 9 balanced domains |
| No pre-registration | PREREGISTRATION.md with formal hypotheses |
| Shannon bias | Miller-Madow correction applied |

---

## V1 Scripts Deleted

```
scripts/run_comprehensive_experiment.py      → replaced by run_comprehensive_experiment_v2.py
scripts/statistical_analysis_generic.py      → replaced by statistical_analysis_v2.py
scripts/statistical_analysis_comprehensive.py → replaced by statistical_analysis_v2.py
scripts/statistical_analysis_llama.py        → one-off deep dive, not needed
scripts/run_local_entropy_experiment.py      → superseded by v2
scripts/analyze_comprehensive_results.py     → superseded by v2
scripts/generate_formatted_tables.py         → superseded by v2
scripts/deepseek_deep_dive_analysis.py       → one-off deep dive, not needed
scripts/qwen_scale_architecture_deep_dive.py → one-off deep dive, not needed
scripts/analysis_mistral_llama_deep_dive.py  → one-off deep dive, not needed
```

V1 result data preserved in `results/valid_entropy_comparisons/` for reference.
