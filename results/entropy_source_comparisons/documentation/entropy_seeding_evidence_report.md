# Entropy Seeding Evidence Report

**Date**: 2026-02-06
**Scope**: QRNG vs TRNG vs PRNG vs Self-Seeding (including hidden-variance self-seeding)
**Purpose**: Consolidate evidence, surface anomalies, and assess publication readiness.

**Important note**: Hidden-layer entropy (cross-layer) is the required internal metric for seeding analysis. Logits entropy is legacy and **not** used for new claims.

---

## 1) Data Sources Audited (Evidence Map)

### Primary docs
- `docs/seeding/ENTROPY_SOURCE_COMPARISON_2026-02-04.md`
- `docs/seeding/SELFSEED_ANALYSIS_2026-02-04.md`
- `docs/seeding/CRITICAL_ISSUES_2026-02-04.md`
- `docs/seeding/EVALUATION_AND_IMPLICATIONS_2026-02-04.md`
- `docs/QUANTUM_RNG_ANALYSIS_2026-02-04.md`
- `docs/QUANTUM_RNG_QUALITATIVE_ANALYSIS_2026-02-04.md`
- `results/colored_entropy/FINAL_REPORT.md`
- `results/colored_entropy/IBM_QRNG_COMPLETE_ANALYSIS.md`

### Quantitative result files
- `data/rng_comparison_quick/rng_comparison_quick_results_20260203_180635.json`
- `data/rng_quantum_ablations/rng_quantum_ablations_results_20260203_173848.json`
- `data/comprehensive_quantum_rng/comprehensive_qwen_0.6b_standard_20260203_174921/comprehensive_qwen_0.6b_standard_20260203_174921_results.json`
- `data/qwen3_comparison_20260204_203239.json`
- `data/results/full_experiments/all_results.json`
- `results/hidden_variance_selfseed_qwen3-0.6b_20260206.json`
- `results/hidden_variance_selfseed_qwen3-8b_20260206_full_v2.json`
- `results/hidden_variance_selfseed_qwen3-14b_20260206_full_v2.json`
- `results/multi_layer_entropy_report_qwen3-14b.json`
- `results/all_layers_entropy_from_dependency_distance_qwen3-14b.json`

---

## 2) Evidence Summary by Entropy Source

### PRNG (StandardPRNG)
- **Quick RNG comparison** (5 prompts): PRNG had the highest mean overall quality score.
  - Mean overall quality (PRNG): **0.5786**
- **Quantum ablations** (3 prompts): PRNG matched all QRNG variants.
  - PRNG mean overall quality: **0.4591**
- **Comprehensive quantum RNG (0.6B)**: PRNG matched QRNG variants.
  - PRNG mean overall quality: **0.4467**
- **Qwen3 PRNG vs QRNG**: small differences by model.
  - 1.7B vocab richness: PRNG **0.8293**, QRNG **0.8182**
  - 4B vocab richness: PRNG **0.8000**, QRNG **0.8095**
- **Self-seed comparisons (full_experiments)**: PRNG baseline is competitive; self-seed gains are small.

### TRNG (TrueRandomSource)
- **Quantum ablations**: TRNG outperformed PRNG/QRNG variants (overall quality).
  - TRNG mean overall quality: **0.4943** (vs 0.4591)
- **Comprehensive quantum RNG (0.6B)**: TRNG > PRNG/QRNG (overall quality).
  - TRNG mean overall quality: **0.4798** (vs 0.4467)
- **Entropy source comparison (0.5B)**: TRNG best average repetition ratio (32.4%).
- **Anomaly**: TRNG cold-start repetition spike on turn 1 (60.8%) then improves.
  - Documented in `docs/seeding/CRITICAL_ISSUES_2026-02-04.md`.
- **Qualitative**: TRNG shows language-mixing glitches and stronger meta-cognition in some cases.

### QRNG (Cached IBM Quantum data)
- **Quantitative**: often matches PRNG; differences are typically small.
  - 0.6B comprehensive: QRNG_INT/HASH/BITS == PRNG overall quality.
  - 8B/14B neural mode: temperature and activation variance differences < 3%.
- **Qualitative**: QRNG can be most creative but also has higher glitch severity.
  - Example patterns: mode-shifts, meta-cognitive interruptions.
- **Practical**: QRNG_Cached appears stable for multi-turn in small-model tests.

### Self-Seeding (SelfSeed SFC/SFS)
- **Small-model task wins** (0.5B):
  - SFS best overall repetition avg (28.4%).
  - SFS best for personal advice; SFC best for abstract prompts.
- **Full_experiments (0.6B / 1.7B / 4B)**:
  - **0.6B**: SFC/SFS slightly improve distinct-2 vs baseline.
  - **1.7B**: SFS shows the strongest distinct-2 improvement.
  - **4B**: SFC/SFS near parity with baseline (no clear gain).
- **Interpretation**: Self-seeding benefits appear task- and size-dependent.

### Hidden-Variance Self-Seeding (new test)
- **Experiment**: `results/hidden_variance_selfseed_qwen3-0.6b_20260206_full.json`
- **Setup**: Qwen3-0.6B, 8 prompts, 5 seeds, 96 tokens, temp=0.8, top-p=0.9.
- **Summary (means ± std)**:
  - PRNG: distinct-2 **0.8618±0.1084**, TTR **0.6211±0.0969**
  - TRNG: distinct-2 **0.8342±0.0891**, TTR **0.5872±0.0717**
  - QRNG_Cached: distinct-2 **0.8579±0.0845**, TTR **0.6055±0.0741**
  - SelfSeed_SFC: distinct-2 **0.7724±0.1721**, TTR **0.5625±0.1099**
  - SelfSeed_SFS: distinct-2 **0.8382±0.0899**, TTR **0.5703±0.0669**
  - HiddenVariance: distinct-2 **0.8447±0.1507**, TTR **0.5938±0.1191**
- **Summary artifact**: `docs/seeding/ENTROPY_SEEDING_SUMMARY_QWEN3_0.6B_2026-02-06.md`
- **Significance (paired bootstrap, prompts=8)**: `docs/seeding/ENTROPY_SEEDING_SIGNIFICANCE_QWEN3_0.6B_2026-02-06.md`
- **Interpretation**: Hidden-variance seeding is competitive with QRNG/SFS, but PRNG remains strongest on this prompt set.
- **Limitation**: Hidden-layer entropy metrics were **not captured** in this run (legacy metrics only).

### Hidden-Variance Self-Seeding (1.7B full)
- **Experiment**: `results/hidden_variance_selfseed_qwen3-1.7b_20260206_full.json`
- **Setup**: Qwen3-1.7B, 8 prompts, 5 seeds, 96 tokens, temp=0.8, top-p=0.9.
- **Summary (means ± std)**:
  - PRNG: distinct-2 **0.8368±0.1299**, TTR **0.6224±0.0899**
  - TRNG: distinct-2 **0.8145±0.1260**, TTR **0.5740±0.1005**
  - QRNG_Cached: distinct-2 **0.7645±0.2451**, TTR **0.5508±0.1872**
  - SelfSeed_SFC: distinct-2 **0.8053±0.2146**, TTR **0.5612±0.1444**
  - SelfSeed_SFS: distinct-2 **0.8026±0.1904**, TTR **0.5417±0.1251**
  - HiddenVariance: distinct-2 **0.7513±0.2336**, TTR **0.5521±0.1813**
- **Summary artifact**: `docs/seeding/ENTROPY_SEEDING_SUMMARY_QWEN3_1.7B_2026-02-06.md`
- **Significance (paired bootstrap, prompts=8)**: `docs/seeding/ENTROPY_SEEDING_SIGNIFICANCE_QWEN3_1.7B_2026-02-06.md`
- **Interpretation**: PRNG retains the strongest distinct-2/TTR in this run; self-seed and hidden-variance do not improve diversity on this prompt set.
- **Limitation**: Hidden-layer entropy metrics were **not captured** in this run (legacy metrics only).
- **Note**: 4B hidden-variance seeding results are not present in the workspace and are excluded from this report.

### Hidden-Variance Self-Seeding (8B full, hidden entropy captured)
- **Experiment**: `results/hidden_variance_selfseed_qwen3-8b_20260206_full_v2.json`
- **Setup**: Qwen3-8B, 14 prompts, 5 seeds, 128 tokens, temp=0.8, top-p=0.9, **hidden-layer entropy captured**.
- **Summary (distinct-2 / TTR / hidden_entropy_mean)**:
  - PRNG: **0.8256 / 0.5826 / 1.7627**
  - TRNG: **0.8601 / 0.5929 / 1.7804**
  - QRNG_Cached: **0.8836 / 0.6200 / 1.7959**
  - SelfSeed_SFC: **0.8510 / 0.5647 / 1.7581**
  - SelfSeed_SFS: **0.8960 / 0.6222 / 1.7616**
  - HiddenVariance: **0.8279 / 0.5893 / 1.7609**
  - Nebula_Bible: **0.8093 / 0.5536 / 1.7775**
- **Summary artifact**: `docs/seeding/ENTROPY_SEEDING_SUMMARY_QWEN3_8B_2026-02-06.md`
- **Significance (paired bootstrap)**: `docs/seeding/ENTROPY_SEEDING_SIGNIFICANCE_QWEN3_8B_2026-02-06.md`
- **Interpretation**: QRNG_Cached and SelfSeed_SFS lead on distinct-2/TTR; hidden entropy metrics are stable across sources with modest variance.
- **Significance highlights**:
  - QRNG_Cached shows a small but positive **hidden_entropy_mean** shift vs PRNG (CI excludes 0).

### Hidden-Variance Self-Seeding (14B full, hidden entropy captured)
- **Experiment**: `results/hidden_variance_selfseed_qwen3-14b_20260206_full_v2.json`
- **Setup**: Qwen3-14B, 14 prompts, 5 seeds, 128 tokens, temp=0.8, top-p=0.9, **hidden-layer entropy captured**.
- **Summary (distinct-2 / TTR / hidden_entropy_mean)**:
  - PRNG: **0.8909 / 0.5999 / 1.4625**
  - TRNG: **0.8829 / 0.6131 / 1.4606**
  - QRNG_Cached: **0.9173 / 0.6445 / 1.4796**
  - SelfSeed_SFC: **0.8982 / 0.6256 / 1.4594**
  - SelfSeed_SFS: **0.8841 / 0.6110 / 1.4499**
  - HiddenVariance: **0.8796 / 0.6110 / 1.4550**
  - Nebula_Bible: **0.9184 / 0.6300 / 1.4599**
- **Summary artifact**: `docs/seeding/ENTROPY_SEEDING_SUMMARY_QWEN3_14B_2026-02-06.md`
- **Significance (paired bootstrap)**: `docs/seeding/ENTROPY_SEEDING_SIGNIFICANCE_QWEN3_14B_2026-02-06.md`
- **Interpretation**: QRNG_Cached and Nebula_Bible lead on distinct-2/TTR; hidden entropy means are tightly clustered across sources.
- **Significance highlights**:
  - QRNG_Cached shows higher **TTR** and lower **repetition_ratio** vs PRNG (CIs exclude 0).

### Hidden-Layer Entropy (cross-layer evidence)
- **Source**: `results/multi_layer_entropy_report_qwen3-14b.json`
- **Scope**: Cross-layer entropy analysis on Qwen3‑14B only (single model).
- **Key signal**:
  - Early layers (0–13): mean entropy **-89.82**, CV **0.129** (labeled “Exploration phase”).
  - Middle layers (13–27): mean entropy **9.48**, CV **0.040** (labeled “Refinement phase”).
  - Late layers (27–41): mean entropy **5.85**, CV **0.037** (labeled “Execution phase”).
- **Note**: Negative entropy values are reported as-is from the existing estimator; verify scale/definition before cross-paper comparisons.
- **Interpretation**: Cross-layer entropy is strongly phase-structured. This supports using **clustered layer entropy** (early/mid/late) for seeding rather than logits entropy.

---

## 3) Anomalies and Nuances (Cross-Source)

1. **PRNG multi-turn failure**
   - PRNG fails on turn 3 in a multi-turn test (empty response).
   - This is a major reliability issue that must be resolved before publication claims about PRNG baselines.

2. **TRNG cold start**
   - Turn 1 repetition can be very high, then improves over subsequent turns.
   - Suggests warmup or entropy buffering may be required for fair comparison.

3. **QRNG qualitative volatility**
   - Quantitative metrics suggest no advantage, but qualitative inspection shows stronger creativity and more severe glitches.
   - Indicates that current numeric metrics may not capture creative-vs-coherent tradeoffs.

4. **Self-seed size dependence**
   - Clear gains in 0.6B/1.7B, but not in 4B within current tests.
   - Suggests either a scaling threshold or parameter sensitivity.

5. **Metric mismatch across experiments**
   - Different experiments use different metrics (repetition ratio, overall quality, temp/variance, vocab richness).
   - Makes direct comparison non-trivial and is a publication risk.
6. **Hidden-layer entropy missing in seeding runs**
   - 0.6B/1.7B runs used legacy metrics; **hidden-layer entropy was not captured**.
   - 8B/14B runs **do capture hidden-layer entropy** and should be treated as the primary evidence.
   - This blocks claims about cross-model consistency unless 0.6B/1.7B are re-run or explicitly scoped as legacy.

---

## 4) Consistency Check: Where Evidence Agrees vs Conflicts

**Agreements**
- QRNG and PRNG are often close in quantitative metrics.
- TRNG sometimes outperforms PRNG/QRNG on small models.
- Self-seeding can help specific task types (personal/abstract).

**Conflicts**
- Quick comparison favors PRNG overall; other tests favor TRNG.
- QRNG is "no difference" in metrics but "higher creativity with glitches" qualitatively.
- Self-seed looks strong in 0.5B docs but modest in 4B full_experiments.

**Working hypothesis**
- Most conflicts are explained by **model size**, **metric choice**, **prompt set**, and **small sample sizes**.
- The paper must explicitly scope claims to the tested regime and metrics.

---

## 5) Publication Readiness (Entropy Seeding Paper)

**Current status**: **Not yet publication-ready**.

### Strengths
- Multiple RNG conditions tested (PRNG/TRNG/QRNG) across small and large models.
- Multiple evaluation modes (quantitative + qualitative).
- Clear documentation of anomalies and failure modes.
- Self-seeding variants (SFC/SFS/SAC) implemented and tested.

### Gaps blocking publication
1. **Inconsistent metrics across datasets**
   - Need a unified evaluation metric set across all RNG sources.
2. **Small sample sizes**
   - Many comparisons use 3-5 prompts or 2-3 samples.
3. **Self-seeding scaling**
   - Strong evidence is mostly on small models; larger models show weaker gains.
4. **Missing statistical tests**
   - No consistent significance testing across RNG sources.
5. **No human evaluation**
   - Qualitative differences are noted but not systematically scored.
6. **PRNG multi-turn failure unresolved**
   - Must be diagnosed or scoped out to avoid undermining baseline comparisons.
7. **Paper framing mismatch**
   - Seeding results are mixed with temperature/top-p control in places (NEF/TRE overlap). The seeding paper needs strict scope boundaries.
8. **Hidden-layer entropy instrumentation gap**
    - Hidden entropy now recorded for 8B/14B, but missing for 0.6B/1.7B. The paper must either rerun small models or scope them as legacy.

### Minimum fixes for submission readiness
- Standardize metrics and rerun a core benchmark suite across PRNG/TRNG/QRNG/SelfSeed/HiddenVariance.
- Keep the 8B/14B hidden-entropy runs as the canonical baseline; rerun 0.6B/1.7B only if needed for scaling claims.
- Add statistical significance testing (bootstrap or paired tests across prompts).
- Add a small human eval panel for qualitative claims (even 3-5 raters on 20 samples).
- Resolve or scope the PRNG multi-turn failure.
- Separate seeding-only claims from TRE/NEF parameter-control claims.

---

## 6) Recommended Next Steps (Focused and High-Leverage)

1. **Run a unified benchmark suite (only where data is missing)**
   - Same prompts, seeds, metrics across PRNG/TRNG/QRNG/SFS/SFC/HiddenVariance.
   - Do not rerun conditions that already have complete data.
2. **Instrument hidden-layer entropy for seeding**
   - Record cross-layer entropy (early/mid/late) per step and use it in analysis.
   - Avoid logits entropy for internal-dynamics claims.
3. **Fix or scope PRNG multi-turn failure**
   - Add diagnostics and either fix or explicitly exclude the failure scenario.
4. **Add minimal human eval**
   - Quick rating pass for coherence, creativity, and glitch severity.
5. **Paper separation**
   - Keep entropy-seeding paper strictly about entropy sources; TRE handles parameter control.

---

## 7) Conclusion

The entropy seeding research is promising and shows real signal differences between PRNG/TRNG/QRNG and self-seeding variants, but the evidence is not yet cohesive enough for publication. The primary blockers are inconsistent metrics, small sample sizes, unresolved anomalies, and the **missing hidden-layer entropy instrumentation** in seeding runs. The hidden-variance self-seeding test adds a novel feedback mechanism and performs competitively, but it needs hidden-entropy instrumentation and multi-model validation.

Once the core benchmark suite is unified and the anomalies are resolved or scoped, the seeding paper will have a defensible and novel contribution.
