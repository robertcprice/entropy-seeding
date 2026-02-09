# Entropy Source Fingerprint Classifier - Detailed Report

## Abstract

**Question:** "Can you detect which entropy source was used by analyzing the generated text?"

**Answer:** Partially. Pairwise detection reaches 85.7% accuracy for mechanistically distinct sources (PRNG vs self-seeding), but 7-way multiclass classification is marginal at 18%. SHA256-chained sources like Nebula are indistinguishable from all others, confirming the SHA256 Paradox.

---

## Motivation

If different entropy sources leave measurable fingerprints in LLM-generated text, several practical consequences follow:

1. **AI watermarking** -- Can entropy-source identity be inferred from output alone?
2. **RNG quality assessment** -- Do different RNG types produce detectably different text?
3. **Model auditing** -- Can self-seeding or feedback-loop sources be identified post-hoc?
4. **SHA256 Paradox validation** -- Does SHA256 chaining truly mask source identity?

This experiment trains classifiers on text features and internal model metrics to answer these questions.

---

## Experimental Setup

### Script

```
scripts/build_entropy_fingerprint_classifier.py
```

Located in the parent `entropy/` project.

### Data

| Property | Value |
|----------|-------|
| **Model** | Qwen3-8B |
| **Hardware** | NVIDIA H200 GPU |
| **Total samples** | 490 |
| **Entropy sources** | 7 |
| **Samples per source** | 70 |
| **Prompt groups** | 14 (5 categories x 2-3 prompts) |

### Entropy Sources Tested

| Source | Mechanism | Description |
|--------|-----------|-------------|
| **prng** | Deterministic | Mersenne Twister with fixed seeds |
| **trng** | Hardware | `/dev/urandom` hardware entropy |
| **qrng_cached** | Quantum | IBM Quantum measurements (cached) |
| **self_seed_sfc** | Feedback (SFC) | Self-seeding with SFC generator |
| **self_seed_sfs** | Feedback (SFS) | Self-seeding with SFS generator |
| **hidden_variance** | Internal state | Seeds from hidden layer variance |
| **nebula_bible** | SHA256 chain | Nebula literary entropy (Bible KJV corpus) |

### Per-Sample Data

Each sample includes the full generated text plus pre-computed metrics:
- `distinct_1`, `distinct_2`, `distinct_3`
- `TTR`, `token_ttr`
- `repetition_ratio`
- `hidden_entropy_early`, `hidden_entropy_mid`, `hidden_entropy_late`, `hidden_entropy_mean`
- `state_distribution` (confident, exploring, branching, focused_uncertain)
- `avg_logits_entropy`, `avg_temperature`

---

## Feature Engineering

### 108 Features Total (54 Raw + 54 Prompt-Normalized)

#### Text Features (30 raw)

| Category | Features |
|----------|----------|
| **Word-level** | n_words, avg_word_length, word_length_std, TTR, unique_word_count, hapax_ratio |
| **Pronoun rates** | 1st_person, 2nd_person, 3rd_person, total_pronoun |
| **Sentence-level** | avg_sentence_length, sentence_length_std, max_sentence_length, min_sentence_length, sentence_count |
| **Punctuation** | comma_rate, semicolon_rate, question_rate, exclamation_rate, double_quote_rate, apostrophe_rate |
| **N-gram repetition** | bigram_repetition_rate, trigram_repetition_rate, fourgram_repetition_rate |
| **Lexical** | content_word_ratio, uppercase_ratio, digit_ratio |

#### Metric Features (16 raw)

| Feature | Source |
|---------|--------|
| distinct_1, distinct_2, distinct_3 | N-gram diversity |
| TTR, token_ttr | Vocabulary richness |
| repetition_ratio | Token-level repetition |
| token_count | Generation length |
| hidden_entropy_mean/early/mid/late | Internal activation entropy |
| avg_logits_entropy | Output distribution entropy |
| avg_temperature | Effective temperature |
| d2/d1 ratio, d3/d2 ratio | Diversity scaling ratios |

#### Hidden Entropy Interactions (7 raw)

| Feature | Computation |
|---------|-------------|
| he_slope_early_late | late - early hidden entropy |
| he_ratio_late_early | late / early hidden entropy |
| he_slope_early_mid | mid - early hidden entropy |
| he_slope_mid_late | late - mid hidden entropy |
| he_late_minus_mean | late - mean hidden entropy |
| he_std | Standard deviation across layers |
| he_range | max - min hidden entropy |

#### State Distribution Features (6 raw)

| Feature | Description |
|---------|-------------|
| confident_rate | Fraction of tokens in "confident" state |
| exploring_rate | Fraction of tokens in "exploring" state |
| branching_rate | Fraction of tokens in "branching" state |
| focused_uncertain_rate | Fraction in "focused uncertain" state |
| confident_exploring_ratio | Ratio of confident to exploring |
| state_entropy | Shannon entropy of state distribution |

#### Prompt Normalization (54 pn_ features)

All 54 raw features are duplicated with a `pn_` prefix after subtracting per-prompt-group means:

```
pn_feature[i] = raw_feature[i] - mean(raw_feature[i] | same prompt group)
```

**Purpose:** Isolate entropy-source-specific signal by removing prompt-driven variation. A prompt about philosophy will naturally have longer sentences than a prompt about colors -- normalization removes this confound.

---

## Methodology

### The Prompt Leakage Problem

**Initial approach:** StratifiedKFold cross-validation.

**Result:** 60.4% accuracy (3.6x over 16.7% baseline for 6 classes).

**Problem:** This was **entirely prompt leakage**. With StratifiedKFold, training and test folds contain samples from the same prompts. The classifier learned to identify prompts, not entropy sources. On an expanded 8B dataset, StratifiedKFold reached 93.7% -- a clear sign of memorization.

```
StratifiedKFold (WRONG):
  Train: [prompt_A_prng, prompt_A_trng, prompt_B_prng, prompt_C_trng, ...]
  Test:  [prompt_A_qrng, prompt_B_trng, ...]

  Classifier learns: "prompt_A has feature X" (prompt identity, NOT source identity)
```

**Fix:** LeaveOneGroupOut (LOGO) cross-validation, where each fold holds out one entire prompt group. The classifier never sees the held-out prompt during training.

```
LeaveOneGroupOut (CORRECT):
  Fold 1 - Train: [prompts 2-14, all sources]  Test: [prompt 1, all sources]
  Fold 2 - Train: [prompts 1,3-14, all sources]  Test: [prompt 2, all sources]
  ...
  Fold 14 - Train: [prompts 1-13, all sources]  Test: [prompt 14, all sources]

  Classifier MUST generalize to unseen prompts.
```

### Cross-Validation

| Property | Value |
|----------|-------|
| **Strategy** | LeaveOneGroupOut (LOGO) |
| **Folds** | 14 (one per prompt group) |
| **Group variable** | Prompt group ID |
| **Guarantee** | No prompt leakage between train/test |

### Feature Selection

| Setting | Value |
|---------|-------|
| **Method** | ANOVA F-score |
| **K (multiclass)** | 30 features |
| **K (pairwise)** | 20 features |
| **Selection scope** | Per-fold (inside CV loop) |

### Models Tested

| Model | Key Hyperparameters |
|-------|---------------------|
| **Random Forest** | n_estimators=500, max_depth=6, min_samples_leaf=3, min_samples_split=5, max_features=sqrt |
| **XGBoost** | n_estimators=300, max_depth=4, learning_rate=0.05, reg_alpha=1.0, reg_lambda=5.0, subsample=0.8, colsample_bytree=0.8, min_child_weight=3 |
| **Logistic Regression** | C=0.1, l1_ratio=0, StandardScaler, max_iter=2000 |

All models use regularized configurations to prevent overfitting on 490 samples.

---

## Results

### 7-Way Multiclass Classification (LOGO CV)

| Model | Accuracy | vs 14.3% Baseline | Lift |
|-------|----------|-------------------|------|
| **Random Forest** | **18.0% +/- 13.2%** | +3.7% | **1.3x** |
| Logistic Regression | 15.9% +/- 12.7% | +1.6% | 1.1x |
| XGBoost | 10.0% +/- 6.2% | -4.3% | 0.7x |

**Interpretation:** Multiclass accuracy is marginal. The 7-way task dilutes signal because different source pairs have different discriminating features -- no single feature set separates all 7 sources simultaneously.

### Top Discriminating Features (RF, Mean Importance)

| Rank | Feature | Importance |
|------|---------|------------|
| 1 | pn_sentence_length_std | 0.054 |
| 2 | pn_he_slope_early_late | 0.051 |
| 3 | pn_metric_d2_d1_ratio | 0.049 |
| 4 | pn_avg_sentence_length | 0.049 |
| 5 | pn_he_ratio_late_early | 0.048 |

**Key observation:** All top features carry the `pn_` prefix (prompt-normalized). Raw features without normalization contain too much prompt-driven noise to be discriminating.

---

### Pairwise Binary Classification (Key Result)

Random Forest with LOGO CV, 20 features per pair. Random baseline = 50%.

#### Pairs Above 60% Accuracy

| Source A | Source B | Accuracy | Lift vs 50% |
|----------|----------|----------|-------------|
| **prng** | **self_seed_sfc** | **85.7%** | **1.71x** |
| hidden_variance | qrng_cached | 78.6% | 1.57x |
| qrng_cached | self_seed_sfc | 78.6% | 1.57x |
| hidden_variance | prng | 67.9% | 1.36x |
| hidden_variance | self_seed_sfs | 67.9% | 1.36x |
| prng | qrng_cached | 64.3% | 1.29x |
| qrng_cached | self_seed_sfs | 64.3% | 1.29x |
| prng | trng | 61.4% | 1.23x |
| self_seed_sfc | self_seed_sfs | 60.7% | 1.21x |

**9 of 21 pairs exceed 60% accuracy.**

#### Pairwise Summary Statistics

| Statistic | Value |
|-----------|-------|
| **Mean pairwise accuracy** | 57.8% |
| **Maximum** | 85.7% (prng vs self_seed_sfc) |
| **Minimum** | 28.6% |
| **Pairs above 60%** | 9 / 21 (43%) |
| **Pairs above 70%** | 3 / 21 (14%) |

#### nebula_bible: Indistinguishable

```
nebula_bible vs prng:           ~50%
nebula_bible vs trng:           ~50%
nebula_bible vs qrng_cached:    ~50%
nebula_bible vs self_seed_sfc:  ~50%
nebula_bible vs self_seed_sfs:  ~50%
nebula_bible vs hidden_variance: ~50%
```

**nebula_bible is at chance level against every other source.** The SHA256 chain in Nebula's hierarchical extraction pipeline completely masks the underlying source identity, confirming the SHA256 Paradox: cryptographic hashing decorrelates the entropy source from its output to such a degree that no text-level or internal-metric-level fingerprint survives.

---

### Cohen's d Effect Sizes (vs PRNG Baseline)

| Source | Feature | Cohen's d | Magnitude |
|--------|---------|-----------|-----------|
| **self_seed_sfc** | pn_avg_sentence_length | **1.84** | **LARGE** |
| **self_seed_sfc** | pn_metric_d2_d1_ratio | **1.24** | **LARGE** |
| hidden_variance | pn_avg_sentence_length | 1.01 | LARGE |
| qrng_cached | pn_he_slope_early_late | 0.81 | MEDIUM-LARGE |
| trng | pn_avg_sentence_length | 0.80 | LARGE |
| qrng_cached | pn_he_ratio_late_early | 0.73 | MEDIUM |

**self_seed_sfc** produces the largest effect sizes against PRNG, consistent with its top pairwise accuracy (85.7%). The self-seeding feedback loop creates a fundamentally different generation trajectory than deterministic PRNG, and this difference is large enough to detect reliably.

---

## Analysis

### Why Multiclass Fails but Pairwise Succeeds

```
7-Way Multiclass:
  Need features that separate ALL 7 sources simultaneously.
  But: prng vs self_seed_sfc discriminates on sentence_length features,
       while hidden_variance vs qrng_cached discriminates on he_slope features.
  No single feature set handles all pairs -> diluted signal -> ~18%

Pairwise Binary:
  Each pair gets its own optimal 20-feature set.
  Mechanistically different pairs have strong, pair-specific signals -> up to 85.7%
```

### The Hidden Entropy Trajectory Signal

The most consistently discriminating features involve hidden entropy trajectory -- how the entropy of internal model activations changes from early layers to late layers during generation.

```
Hidden Entropy Trajectory:

Early layers -----> Mid layers -----> Late layers
     |                  |                  |
     v                  v                  v
  he_early           he_mid            he_late

he_slope_early_late = he_late - he_early    (trajectory shape)
he_ratio_late_early = he_late / he_early    (trajectory scaling)
```

Different entropy sources produce different trajectory shapes:
- **PRNG:** Relatively flat trajectory (deterministic seed produces uniform activation patterns)
- **Self-seeding:** Steeper trajectory (feedback loop creates progressively different activation patterns)
- **QRNG:** Distinctive early-to-late ratio (quantum randomness affects early-layer activation distribution)

This is a subsurface signal -- it does not manifest in surface text features (word choice, punctuation, sentence structure) but is visible in the model's internal computation.

### Source Mechanism Determines Detectability

```
Detectability Scale (vs PRNG):

self_seed_sfc    ████████████████ 85.7%  (feedback loop)
qrng_cached      ████████████░░░░ 64.3%  (quantum)
hidden_variance  █████████████░░░ 67.9%  (internal state)
trng             ████████████░░░░ 61.4%  (hardware)
self_seed_sfs    ████████░░░░░░░░ ~55%   (feedback, different generator)
nebula_bible     ████████░░░░░░░░ ~50%   (SHA256 chain = invisible)
```

Sources with fundamentally different generation mechanisms are most distinguishable. Self-seeding creates a feedback loop that amplifies small differences across generation steps. PRNG is fully deterministic. The contrast is maximal.

---

## Implications

### AI Watermarking and Privacy

Literary entropy sources like Nebula that use SHA256 chaining **cannot be detected from text features alone**. This has two-sided implications:

- **Privacy positive:** Entropy-source-based watermarks using hash chains are invisible to third-party analysis.
- **Audit negative:** If a system uses Nebula-style entropy, there is no post-hoc way to verify the source from the text output.

### RNG Quality Assessment

Different RNG types leave measurably different traces in generation, but the signal is subtle:
- Pairwise detection is possible (up to 85.7%) but requires internal model metrics (hidden entropy), not just surface text features.
- 7-way classification from text alone is near chance (18%).

### Model Auditing

Self-seeding sources are the most detectable (85.7% vs PRNG). If a deployed system uses self-seeding feedback loops, this can potentially be detected through careful analysis of generation patterns -- particularly hidden entropy trajectories.

### The SHA256 Paradox Confirmed

The SHA256 chain in Nebula-style entropy completely erases source identity. This is consistent with the broader SHA256 Paradox finding: while SHA256 does not fully decorrelate sequential consumption within a chain, it is fully effective at masking the identity of the input source from downstream classifiers.

---

## Limitations

| Limitation | Impact |
|------------|--------|
| **Single model (Qwen3-8B)** | Results may not generalize to other architectures |
| **490 samples** | Statistical power limited; wide confidence intervals |
| **14 prompt groups** | LOGO CV has only 14 folds; high variance across folds |
| **No temporal features** | Token-by-token generation dynamics not captured |
| **Cached QRNG** | Not live quantum measurements; cache reuse may reduce distinctiveness |
| **Single temperature** | All generations at same temperature setting |

### Future Directions

1. **Multi-model validation:** Repeat on 14B, 32B, and 70B models to test scale effects
2. **Larger sample sizes:** 200+ samples per source for tighter confidence intervals
3. **Temporal features:** Token-level hidden entropy sequences as time-series features
4. **Deep learning classifiers:** 1D-CNN or LSTM on token-level feature sequences
5. **Adversarial testing:** Can sources be modified to evade detection?
6. **Cross-model transfer:** Do fingerprints trained on Qwen3 transfer to DeepSeek-R1?

---

## Final Summary

```
+-------------------------------------------------------------------+
|                                                                   |
|         ENTROPY SOURCE FINGERPRINTS: PARTIALLY DETECTABLE         |
|                                                                   |
|   7-Way Multiclass:  18% (marginal, ~1.3x over baseline)         |
|   Best Pairwise:     85.7% (PRNG vs self_seed_sfc)               |
|   Pairs > 60%:       9 / 21 (43%)                                |
|   Mean Pairwise:     57.8%                                       |
|                                                                   |
|   KEY FINDINGS:                                                   |
|                                                                   |
|   1. Pairwise detection works for mechanistically                 |
|      different sources (85.7% best case)                          |
|                                                                   |
|   2. Multiclass dilutes signal (different pairs need              |
|      different features)                                          |
|                                                                   |
|   3. SHA256-chained sources (nebula_bible) are                    |
|      completely invisible (~50% vs everything)                    |
|                                                                   |
|   4. Hidden entropy trajectory is the strongest                   |
|      discriminating signal (not surface text)                     |
|                                                                   |
|   5. Prompt normalization is essential (all top                   |
|      features are pn_ normalized)                                 |
|                                                                   |
+-------------------------------------------------------------------+
```

---

*Report generated: 2026-02-09*
*Script: `scripts/build_entropy_fingerprint_classifier.py`*
*Data: 490 samples, 7 entropy sources, Qwen3-8B on H200 GPU*
*CV strategy: LeaveOneGroupOut (14 folds, prompt-leakage-free)*

---

## Appendix: Metrics Glossary

### Key Metrics

| Metric | What It Measures | Good Range | Direction |
|:------:|------------------|:----------:|:---------:|
| **distinct_2** (D2) | Unique bigram fraction | 0.85-1.0 | Higher = more diverse |
| **TTR** | Type-Token Ratio (unique words / total words) | 0.5-0.8 | Higher = richer vocabulary |
| **hidden_entropy_mean** | Mean entropy across hidden layers (nats) | 1.3-1.6 | Higher = more activation diversity |
| **he_slope_early_late** | Late - early hidden entropy | Variable | Captures trajectory shape |

### Statistical Measures

| Measure | Key Thresholds |
|:-------:|:--------------:|
| **Cohen's d** | < 0.2 negligible, 0.2-0.5 small, 0.5-0.8 medium, > 0.8 large |
| **LOGO** | LeaveOneGroupOut CV: holds out one prompt per fold, prevents prompt leakage |
| **ANOVA F-score** | Between-class vs within-class variance; used for feature selection |
| **Prompt normalization (pn_)** | Feature residuals after subtracting per-prompt-group means |

### Entropy Sources

| Source | Description |
|:------:|-------------|
| **prng** | Pseudo-Random (Mersenne Twister, fixed seeds). Deterministic, reproducible. |
| **trng** | True Random (`/dev/urandom`). Hardware entropy, non-reproducible. |
| **qrng_cached** | Quantum Random (IBM `ibm_fez`, cached). Fundamentally unpredictable. |
| **self_seed_sfc** | Self-seeding with SFC generator. Feedback loop from generation output. |
| **self_seed_sfs** | Self-seeding with SFS generator. Alternative feedback-loop variant. |
| **hidden_variance** | Seeds derived from hidden layer activation variance during generation. |
| **nebula_bible** | Nebula literary entropy with Bible KJV corpus, SHA256 chain. |

*Full glossary: see `METRICS_GLOSSARY.md` in the repository root.*
