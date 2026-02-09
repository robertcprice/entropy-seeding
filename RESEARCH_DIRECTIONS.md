# Research Directions: Entropy Source Effects on LLM Generation

**Date:** 2026-02-09
**Status:** Active research — experiments prioritized by impact and feasibility
**Companion to:** `COMPREHENSIVE_ENTROPY_SEEDING_EXPERIMENT_2026-02-09.md`

---

## Current State of Evidence

### What We Know (Statistically Confirmed)
1. **Transformer is a low-pass filter on entropy** — prompt drives ~96% of output variation, source <1%
2. **Below 14B: entropy source doesn't matter** for aggregate text quality metrics
3. **14B is the sweet spot** — QRNG cached produces +4.5% TTR (p=0.99)
4. **72B reversal** — PRNG becomes *better* than alternatives (p=0.005)
5. **MoE catastrophic failure** — DeepSeek R1 collapses on philosophy prompts; only TRNG prevents it
6. **Multi-turn degradation** — PRNG-seeded Llama loses -4.8% vocabulary diversity over 3 turns (d=-0.50)
7. **All 3 architectures at 8B agree** — Dense, SWA, GQA show negligible entropy source effects (36 tests, 0 significant)
8. **Nebula reduces text-induced bias by 23.8%** vs single-layer literary hash chain
9. **Bible KJV entropy** — -25.2% D2, 2.1x first-person pronouns vs PRNG
10. **Pairwise fingerprinting works** — 9/21 source pairs above 60%, PRNG vs self_seed_sfc = 85.7%

### What We Don't Know (Gaps)
1. Statistical significance not reached at n=70 for many 8B comparisons
2. Only Bible KJV tested as literary source at 8B+ scale (21 other texts untested)
3. Individual Nebula layer contributions not quantified
4. No formal information-theoretic analysis of SHA256 Paradox
5. No empirical style transfer validation (literary source → generation style)
6. Recursive modulation dynamics not mapped (feedback_gain phase space)
7. Token-level fingerprint features not explored (only text-surface features tested)
8. No end-to-end watermarking proof-of-concept

---

## Priority Experiments

### Tier 1: High Impact, Ready to Run (1-2 weeks)

#### E1. Power-Up 8B Sample Size
**Goal:** Reach statistical significance on Bible vs PRNG at 8B scale
**Current:** n=70 per source, CIs too wide
**Plan:**
```
python scripts/run_hidden_variance_selfseed.py \
    --model Qwen/Qwen3-8B \
    --sources nebula_bible,prng,trng,qrng_cached,self_seed_sfs,hidden_variance \
    --n_per_source 300 \
    --seeds 11,22,33,44,55 \
    --max_tokens 128 \
    --output results/power_up_nebula_8b.json
```
**Expected:** repetition_ratio p<0.01 at n=300, 1st-person pronoun effect highly significant
**Hardware:** H200, ~8 hours
**Impact:** Turns directional trends into publishable significance results

#### E2. Full Nebula Genre Sweep at 8B
**Goal:** Establish genre-specific entropy coloring effects
**Plan:**
```
python scripts/run_nebula_genre_sweep.py \
    --model Qwen/Qwen3-8B \
    --texts all \
    --n_per_text 100 \
    --seeds 11,22,33 \
    --max_tokens 128 \
    --output results/nebula_genre_sweep_8b.json
```
**Expected:**
- Genre ranking (which genres cause most/least coloring)
- Horror (Lovecraft) vs Horror (Poe) comparison to isolate prose density effects
- Specific structural features driving coloring identified
**Hardware:** H200, ~12 hours
**Impact:** First systematic genre-entropy interaction study

#### E3. Extended Pairwise Fingerprinting
**Goal:** Boost pairwise classifier accuracy with more data
**Current:** n=70, 85.7% best pair
**Plan:**
- Re-use E1 data (n=300 per source)
- Run `build_entropy_fingerprint_classifier.py` with more samples
- Add token-ID sequence features (e.g., token bigram distribution, token entropy trajectory)
**Expected:** PRNG vs self_seed_sfc should exceed 90% with n=300
**Impact:** Establishes entropy fingerprinting as practically viable

---

### Tier 2: Medium Effort, High Scientific Value (2-4 weeks)

#### E4. Nebula Layer Ablation
**Goal:** Quantify each layer's contribution to debiasing and coloring
**Design:**
```
Conditions (Bible KJV on 8B):
  Full Nebula (5 layers)     -- baseline
  No Layer 1 (chunk hashes)  -- remove raw content
  No Layer 2 (frequencies)   -- remove statistical fingerprint
  No Layer 3 (boundaries)    -- remove rhythm/structure
  No Layer 4 (positional)    -- remove position awareness
  No Layer 5 (entanglement)  -- remove non-local dependencies
  Only Layer 1               -- equivalent to literary source
  Only Layers 2+3            -- structural features only
  Only Layers 4+5            -- positional features only

n=200 per condition × 9 conditions = 1,800 generations
```
**Expected:** Layer 5 (entanglement) contributes most to debiasing; Layer 1 most to coloring
**Impact:** Enables engineering-driven optimization of Nebula architecture

#### E5. Recursive Modulation Phase Space (Subset)
**Goal:** Map dynamical regimes of RecursiveModulation
**Design (reduced):**
```
feedback_gain: [0.01, 0.1, 0.3, 0.7, 1.0]  (5 values)
modulation_mode: [additive, xor, rotation]    (3 modes)
base_source: [nebula_bible, prng]             (2 sources)

n=50 per condition × 30 conditions = 1,500 generations
```
**Measurements:** Autocorrelation at lags 1/5/10, output D2/TTR/hidden_entropy
**Expected:** Three regimes — stable (gain<0.1), periodic (0.1-0.5), chaotic (>0.5)
**Impact:** Maps the operating regime for recursive entropy feedback

#### E6. Fingerprinting at 0.6B Scale
**Goal:** Test if smaller models are more susceptible to fingerprinting
**Rationale:** 8B models resist entropy effects (96% prompt-driven). At 0.6B, the model has less internal representation capacity, so entropy source effects may be amplified.
**Plan:** Run existing `build_entropy_fingerprint_classifier.py` on 0.6B data
**Expected:** Pairwise accuracies should be higher than 8B (more detectable fingerprints)
**Impact:** Confirms scale-dependent fingerprint detectability

#### E7. Token-Level Fingerprint Features
**Goal:** Move beyond surface text features to generation-process features
**New features to extract:**
- Token ID bigram distribution (which token pairs follow each other)
- Per-step softmax entropy trajectory
- Per-step perplexity curve
- Token rank distribution (was the chosen token rank 1, 2, 5, 100?)
- Attention entropy over generation steps
**Requires:** Modifying generation pipeline to log per-step data
**Expected:** Should dramatically improve classifier accuracy
**Impact:** Proves fingerprint is in generation dynamics, not surface text

---

### Tier 3: Ambitious Extensions (4-8 weeks)

#### E8. Style Transfer Through Sampling
**Goal:** Demonstrate entropy-driven style transfer without model modification
**Design:**
```
Model: Qwen3-8B (fixed weights)
Prompts: 50 neutral prompts (neither genre-specific nor stylistic)
Sources: 6 genre representatives:
  - bible_kjv (religious)       - lovecraft (cosmic horror)
  - austen (romance)           - plato (philosophical)
  - shakespeare (dramatic)     - darwin (scientific)

Evaluation:
  1. LLM Judge: "What genre/style does this text most resemble?"
  2. Stylometric analysis: sentence length, vocabulary, formality
  3. Topic modeling: dominant themes per source
  4. Human evaluation: 20 raters classify genre from output alone
```
**Impact:** First demonstration of "style transfer through sampling" — paradigm-shifting if confirmed

#### E9. SHA256 Paradox: Formal Information-Theoretic Proof
**Goal:** Prove why sequential hash consumption preserves structural information
**Approach:**
```
Let X = {x_1, ..., x_n} be structured text chunks
Let Y_i = SHA256(x_i)

Claim: While H(Y_i) ≈ 256 bits (near-uniform),
       I(Y_i; Y_{i+1}) > 0 for structured text
       because the walk Y_1 → Y_2 → ... carries autocorrelation

Measurement: Estimate I(Y_i; Y_{i+1}) across texts and compare
             to I(R_i; R_{i+1}) for truly random sequences
```
**Impact:** Standalone information theory / cryptography paper

#### E10. Practical Entropy Watermarking
**Goal:** Build an end-to-end AI text watermarking system
**Architecture:**
- **Embedding:** Choose private literary text → build Nebula chains → use as generation entropy → invisible watermark
- **Detection:** Given text, try all known literary keys → statistical correlation test with expected walk pattern
- **Key space:** 22 texts × 5 gear ratios = 110 built-in keys; custom texts = unlimited
**Advantages:** No model modification, works with any autoregressive model, key is just a text file
**Impact:** Practical watermarking system — currently, Nebula sources are undetectable by text classifiers (confirmed)

#### E11. Cross-Architecture Generalization at Scale
**Goal:** Confirm literary entropy effects are universal
**Design:**
```
Models (all ~8B):
  - Qwen3-8B (Dense, confirmed)
  - Llama-3.1-8B (GQA, confirmed)
  - Mistral-7B (SWA, confirmed)
  - Gemma-2-9B (new, different tokenizer)
  - Mixtral-8x7B (MoE architecture)

Sources: prng, nebula_bible, nebula_shakespeare, self_seed_sfc
n=100 per source per model = 2,000 per model, 10,000 total
```
**Expected:** D2 reduction from Bible generalizes; MoE may show different sensitivity
**Impact:** Establishes universality of findings

---

## Novel Experiment Ideas (Unexplored Territory)

### N1. Adversarial Entropy Sources
Train a small neural network to generate entropy that MAXIMIZES a specific text property (e.g., repetition, creativity score, formality). Use this as a "steered entropy source." If it works, it proves entropy can be weaponized to bias generation.

### N2. Entropy Source as a Channel
Model the entropy source → token selection pipeline as an information channel. Measure the channel capacity. This tells us how many bits of information can be transmitted from the entropy source through the model to the output text.

### N3. Multi-Source Blending Optimization
Instead of one source, blend multiple sources dynamically. Use the model's internal state to decide the blend ratio. When the model is "confused" (high internal entropy), use more structured entropy (Nebula); when confident, use more random (PRNG).

### N4. Temporal Dynamics of Entropy Effects
Track how entropy source effects evolve over the course of generation (token 1 vs token 50 vs token 200). Are effects stronger at the beginning when the model is still "choosing a direction"? Do they fade as the model builds context?

### N5. Entropy Source Transfer Across Fine-Tuning
Test: if a model is fine-tuned, do its entropy source sensitivities change? Does instruction-tuning dampen or amplify literary entropy effects?

### N6. Consciousness Oscillation × Entropy Source Interaction
The project has extensive consciousness oscillation research (cognitive state mapping, strange loop detection). Test whether different entropy sources change the oscillation dynamics — do literary sources produce different consciousness oscillation frequencies than PRNG?

---

## Publication Targets

| Paper | Title | Venue | Required Experiments | Timeline |
|-------|-------|-------|---------------------|----------|
| 6 | Literary Entropy Sources: How Text Structure Propagates Through Hash Chains | EMNLP 2026 | E1, E2, E3, E4, E11 | 6-8 weeks |
| 7 | Entropy-Based Style Transfer Without Model Modification | NeurIPS 2026 | E8, E10, E5 | 8-12 weeks |
| 8 | The SHA256 Paradox: Information Preservation in Cryptographic Hash Consumption | Info Theory venue | E9 | 4-6 weeks |

---

## Quick-Start Commands

```bash
# Tier 1: Run tomorrow
# E1 - Power-up (H200)
python scripts/run_hidden_variance_selfseed.py --model Qwen/Qwen3-8B \
    --sources nebula_bible,prng,trng,qrng_cached,self_seed_sfs,hidden_variance \
    --n_per_source 300 --seeds 11,22,33,44,55 --max_tokens 128

# E2 - Genre sweep (H200)
python scripts/run_nebula_genre_sweep.py --model Qwen/Qwen3-8B \
    --texts all --n_per_text 100 --seeds 11,22,33 --max_tokens 128

# E3 - Extended fingerprinting (local, uses E1 output)
python scripts/build_entropy_fingerprint_classifier.py \
    --input results/power_up_nebula_8b.json --model all

# E6 - 0.6B fingerprinting (local, uses existing data)
python scripts/build_entropy_fingerprint_classifier.py \
    --input results/hidden_variance_selfseed_qwen3-0.6b_*.json --model all
```

---

## Metric Glossary

| Term | Definition |
|------|-----------|
| **D2 (distinct_2)** | Unique bigrams / total bigrams. Higher = more diverse. |
| **TTR** | Unique words / total words. Higher = richer vocabulary. |
| **Cohen's d** | Standardized effect size. |d| < 0.2 negligible, 0.2-0.5 small, 0.5-0.8 medium, > 0.8 large. |
| **LOGO** | LeaveOneGroupOut cross-validation. Prevents prompt leakage by holding out entire prompts. |
| **Prompt normalization (pn_)** | Feature residuals after subtracting per-prompt means. Isolates source-specific signal. |
| **SHA256 Paradox** | Sequential hash consumption preserves source autocorrelation despite per-element uniformity. |
| **Gear ratio** | Prime-number advancement rates in Nebula layers. Ensures non-repeating combined pattern. |
| **Nebula** | 5-layer hierarchical text entropy extraction. See `reports/NEBULA_ENTROPY_SOURCE_EXPLAINED.md`. |

---

*Last updated: 2026-02-09*
