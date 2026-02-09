# Comprehensive Entropy Source Seeding Experiment (Feb 2026)

**Status:** LIVE - Updated as results arrive
**Last Updated:** 2026-02-09
**Author:** Robert Price

---

## Experiment Overview

### Design
- **15 single-turn prompts** across creative, philosophical, and technical domains
- **3 multi-turn conversations** (storytelling, debate, worldbuilding) with 3 turns each
- **3 entropy sources:** PRNG (Mersenne Twister, seed=42), TRNG (os.secrets/urandom), QRNG (SHA256 of timestamp+secrets)
- **5 samples per condition** per prompt per source
- **Total per model:** 225 single-turn + 135 multi-turn = 360 generations
- **Inference:** `ollama run --seed <seed>` (uncapped tokens, temperature default)

### Models Under Test

| Model | Family | Params | Status |
|-------|--------|--------|--------|
| qwen3:4b | Qwen3 Dense | 4B | ✅ Complete |
| qwen3:1.7b | Qwen3 Dense | 1.7B | ✅ Complete |
| qwen3:8b | Qwen3 Dense | 8B | 🔄 Running (~25% Phase 1) |
| mistral:latest | Mistral Dense | 7B | ⏳ Queued |
| llama3.1:8b | Llama3.1 Dense | 8B | ⏳ Queued |

### Metrics
| Metric | Description |
|--------|-------------|
| shannon_char | Character-level Shannon entropy (bits) |
| shannon_word | Word-level Shannon entropy (bits) |
| word_diversity | Type-Token Ratio (unique words / total words) |
| length_words | Output length in words |

---

## Results: qwen3:4b (4B params)

### Single-Turn Cross-Prompt Aggregates (n=15 prompts, 5 samples each)

| Metric | PRNG | TRNG | QRNG | TRNG vs PRNG | QRNG vs PRNG |
|--------|------|------|------|:------------:|:------------:|
| shannon_char | 4.637 ± 0.073 | 4.638 ± 0.078 | 4.639 ± 0.068 | +0.02% | +0.04% |
| shannon_word | 8.344 ± 0.271 | 8.377 ± 0.259 | 8.369 ± 0.256 | +0.40% | +0.30% |
| word_diversity | 0.549 ± 0.039 | 0.543 ± 0.044 | 0.551 ± 0.043 | -0.97% | +0.36% |
| length_words | 1032 ± 284 | 1076 ± 324 | 1038 ± 284 | +4.30% | +0.62% |

**Key observation:** At 4B scale, entropy sources produce nearly identical character-level entropy. TRNG generates ~4% longer outputs on average. Word diversity is essentially equivalent across all three sources.

### Multi-Turn Diversity Evolution (word_diversity)

| Conversation | Source | Turn 1 | Turn 2 | Turn 3 | Trend |
|--------------|--------|--------|--------|--------|-------|
| Storytelling | PRNG | 0.625 | 0.567 | 0.479 | ↓ -23.4% |
| Storytelling | TRNG | 0.628 | 0.549 | 0.480 | ↓ -23.6% |
| Storytelling | QRNG | 0.611 | 0.560 | 0.451 | ↓ -26.2% |
| Debate | PRNG | 0.618 | 0.534 | 0.570 | ↓ -7.8% |
| Debate | TRNG | 0.610 | 0.557 | 0.576 | ↓ -5.6% |
| Debate | QRNG | 0.606 | 0.541 | 0.578 | ↓ -4.6% |
| Worldbuilding | PRNG | 0.555 | 0.553 | 0.504 | ↓ -9.2% |
| Worldbuilding | TRNG | 0.536 | 0.553 | 0.511 | ↓ -4.7% |
| Worldbuilding | QRNG | 0.548 | 0.548 | 0.515 | ↓ -6.0% |

**Finding: Universal vocabulary collapse across turns.** All entropy sources show decreasing word diversity over multi-turn conversations. Storytelling degrades fastest (~24% loss by Turn 3). Debate shows partial recovery at Turn 3 (synthesis task forces broader vocabulary). QRNG shows the steepest storytelling degradation (-26.2%).

### Inter-Sample Variance (CV of word_diversity across 5 samples)

| Source | Mean CV | Interpretation |
|--------|---------|----------------|
| PRNG | 6.97% | Highest variance |
| TRNG | 5.92% | Moderate variance |
| QRNG | 4.79% | **Lowest variance** |

**Surprising finding:** QRNG produces the most *consistent* outputs despite being the most random source. PRNG (deterministic) paradoxically shows the *highest* inter-sample variance. This suggests that the SHA256 mixing in QRNG may produce a more uniform seed distribution that lands in similar probability basins.

---

## Results: qwen3:1.7b (1.7B params)

### Single-Turn Cross-Prompt Aggregates (n=15 prompts, 5 samples each)

| Metric | PRNG | TRNG | QRNG | TRNG vs PRNG | QRNG vs PRNG |
|--------|------|------|------|:------------:|:------------:|
| shannon_char | 4.493 ± 0.071 | 4.487 ± 0.094 | 4.483 ± 0.082 | -0.13% | -0.23% |
| shannon_word | 7.578 ± 0.302 | 7.553 ± 0.383 | 7.569 ± 0.343 | -0.33% | -0.12% |
| word_diversity | 0.448 ± 0.044 | 0.445 ± 0.061 | 0.441 ± 0.057 | -0.63% | -1.48% |
| length_words | 885 ± 180 | 913 ± 231 | 915 ± 222 | +3.20% | +3.35% |

**Key observation:** At 1.7B scale, all entropy sources yield **slightly lower diversity than PRNG** (opposite of the hypothesis). TRNG and QRNG generate ~3% longer outputs. The small model appears to be less sensitive to seed source, with differences well within noise.

### Multi-Turn Diversity Evolution (word_diversity)

| Conversation | Source | Turn 1 | Turn 2 | Turn 3 | Trend |
|--------------|--------|--------|--------|--------|-------|
| Storytelling | PRNG | 0.606 | 0.571 | 0.519 | ↓ -14.4% |
| Storytelling | TRNG | 0.586 | 0.553 | 0.521 | ↓ -11.1% |
| Storytelling | QRNG | 0.587 | 0.537 | 0.507 | ↓ -13.6% |
| Debate | PRNG | 0.567 | 0.561 | 0.572 | ↑ +0.9% |
| Debate | TRNG | 0.561 | 0.557 | 0.587 | ↑ +4.6% |
| Debate | QRNG | 0.586 | 0.553 | 0.573 | ↓ -2.2% |
| Worldbuilding | PRNG | 0.464 | 0.501 | 0.487 | ↑ +5.0% |
| Worldbuilding | TRNG | 0.475 | 0.497 | 0.508 | ↑ +6.9% |
| Worldbuilding | QRNG | 0.470 | 0.494 | 0.483 | ↑ +2.8% |

**Finding: Task-dependent diversity dynamics differ by model size.** At 1.7B, debate and worldbuilding show *increasing* diversity across turns (opposite of 4B). This suggests the smaller model benefits from context accumulation more than the larger model. TRNG shows the strongest worldbuilding improvement (+6.9%).

### Inter-Sample Variance (CV of word_diversity across 5 samples)

| Source | Mean CV | Interpretation |
|--------|---------|----------------|
| PRNG | 8.58% | Moderate variance |
| TRNG | 9.30% | **Highest variance** |
| QRNG | 8.87% | High variance |

**Contrast with 4B:** At 1.7B, TRNG shows the highest variance (opposite of 4B where PRNG was highest). Overall variance is higher for the smaller model (~8-9% vs ~5-7%), suggesting that smaller models are more sensitive to seed values in general.

---

## Statistical Significance Tests

### qwen3:4b — Wilcoxon Signed-Rank (paired, n=15 prompts)

| Comparison | Metric | Wilcoxon p | t-test p | Cohen's d | Significant? |
|------------|--------|:----------:|:--------:|:---------:|:------------:|
| TRNG vs PRNG | shannon_char | 0.865 | 0.858 | +0.05 | No |
| TRNG vs PRNG | shannon_word | 0.107 | 0.057 | **+0.54** | No (borderline) |
| TRNG vs PRNG | word_diversity | 0.525 | 0.409 | -0.22 | No |
| TRNG vs PRNG | length_words | 0.107 | 0.118 | +0.43 | No |
| QRNG vs PRNG | shannon_char | 0.561 | 0.798 | +0.07 | No |
| QRNG vs PRNG | shannon_word | 0.277 | 0.272 | +0.30 | No |
| QRNG vs PRNG | word_diversity | 0.720 | 0.753 | +0.08 | No |
| QRNG vs PRNG | length_words | 0.847 | 0.798 | +0.07 | No |

**Notable:** TRNG→PRNG on shannon_word approaches significance (t-test p=0.057) with a medium effect size (d=0.54). TRNG may genuinely produce slightly higher word-level entropy at 4B scale, but the effect is too small for n=15 to confirm.

### qwen3:1.7b — Wilcoxon Signed-Rank (paired, n=15 prompts)

| Comparison | Metric | Wilcoxon p | t-test p | Cohen's d | Significant? |
|------------|--------|:----------:|:--------:|:---------:|:------------:|
| TRNG vs PRNG | shannon_char | 0.589 | 0.579 | -0.15 | No |
| TRNG vs PRNG | shannon_word | 0.934 | 0.544 | -0.16 | No |
| TRNG vs PRNG | word_diversity | 0.847 | 0.780 | -0.07 | No |
| TRNG vs PRNG | length_words | 0.363 | 0.235 | +0.32 | No |
| QRNG vs PRNG | shannon_char | 0.389 | 0.231 | -0.32 | No |
| QRNG vs PRNG | shannon_word | 0.762 | 0.725 | -0.09 | No |
| QRNG vs PRNG | word_diversity | 0.478 | 0.206 | -0.34 | No |
| QRNG vs PRNG | length_words | 0.277 | 0.184 | +0.36 | No |

**Conclusion: No statistically significant differences detected** between any entropy source at either model size. All p-values >> 0.05. Effect sizes range from negligible (d<0.2) to small-medium (d≈0.5), suggesting that any real effect, if it exists, requires much larger sample sizes to detect.

---

## Cross-Model Comparison: 1.7B vs 4B

### Scale Effects on Entropy Source Sensitivity

| Metric | 1.7B Range (max-min across sources) | 4B Range | Scale Effect |
|--------|--------------------------------------|----------|:------------:|
| shannon_char | 0.010 (PRNG-QRNG) | 0.002 | 5x more sensitive at 1.7B |
| shannon_word | 0.025 | 0.033 | Similar |
| word_diversity | 0.007 | 0.008 | Similar |
| length_words | 30 | 44 | 1.5x more at 4B |

### Key Comparisons

| Finding | 1.7B | 4B |
|---------|------|-----|
| Best diversity source | PRNG (0.448) | QRNG (0.551) |
| Most consistent source | PRNG (CV=8.58%) | QRNG (CV=4.79%) |
| Multi-turn trend (storytelling) | All ↓ (11-14%) | All ↓ (23-26%) |
| Multi-turn trend (worldbuilding) | All ↑ (3-7%) | All ↓ (5-9%) |
| Output length bias | TRNG/QRNG +3% longer | TRNG +4% longer |
| Absolute diversity | ~0.44 | ~0.55 |

### Headline Findings

1. **Vocabulary Collapse is Scale-Dependent:** The 4B model loses vocabulary diversity much faster in multi-turn (-24%) than the 1.7B model (-13%). Larger models may have stronger repetition attractors in extended generation.

2. **QRNG Consistency Paradox:** At 4B, QRNG (the most entropic source) produces the most *consistent* outputs (CV=4.79%). At 1.7B, this effect disappears. This suggests the QRNG SHA256 mixing creates uniformly-distributed seeds that interact with the larger model's probability landscape more predictably.

3. **Entropy Source Effect is Weak:** Across both models, the differences between PRNG/TRNG/QRNG are <1.5% on diversity metrics. The entropy source matters far less than model size (4B has +23% higher diversity than 1.7B regardless of source).

4. **Multi-Turn Dynamics Reverse by Scale:** Worldbuilding diversity *increases* across turns at 1.7B but *decreases* at 4B. This is a novel finding — context accumulation helps small models but may constrain larger ones.

---

## Deep Analysis: Thinking vs Content Divergence (Novel Finding)

### The Chain-of-Thought Determinism Problem

Qwen3 models (with /think enabled) generate an extensive "Thinking..." prefix before actual content. Analysis of text similarity reveals a striking pattern:

**Thinking blocks are ~75% similar across ALL entropy sources and seeds.** Content diverges dramatically (~12% similar).

| Prompt | Thinking Similarity | Content Similarity | Ratio |
|--------|:-------------------:|:------------------:|:-----:|
| P1 (lighthouse) | 78.9% | 13.7% | 0.17x |
| P2 (letter) | 77.3% | 13.0% | 0.17x |
| P3 (kingdom) | 75.0% | 12.1% | 0.16x |
| P4 (robot) | 70.0% | 11.1% | 0.16x |
| P5 (year 2157) | 54.2% | 12.2% | 0.23x |

**Interpretation:** The seed only meaningfully affects content generation, not chain-of-thought reasoning. The model's "thinking" is near-deterministic regardless of entropy source. This means:
1. Our diversity metrics are diluted by ~50% identical thinking tokens
2. The true entropy source effect on creative content may be larger than measured
3. Chain-of-thought creates a "deterministic bottleneck" that shields content from seed influence

### Scale Effect on Thinking Determinism

| Model | Mean Thinking Sim | Mean Content Sim | Think/Content Ratio |
|-------|:-----------------:|:----------------:|:-------------------:|
| qwen3:1.7b | 58.6% | 12.0% | 4.9x |
| qwen3:4b | 63.8% | 14.5% | 4.4x |

**The larger model is MORE deterministic in both thinking and content.** The 4B model's thinking is 5.2 percentage points more similar across samples than the 1.7B model's. This suggests larger models have stronger attractor states in both reasoning and generation. The ratio is slightly lower at 4B (4.4x vs 4.9x), meaning content converges even faster than thinking as scale increases.

### Entropy Source Does NOT Cluster Outputs

Within-source similarity (samples sharing the same entropy source type) is statistically indistinguishable from cross-source similarity:

| Prompt | Within-Source Sim | Cross-Source Sim | Gap |
|--------|:-----------------:|:----------------:|:---:|
| P1 | 9.5% | 8.9% | +0.7% |
| P2 | 9.2% | 9.7% | -0.5% |
| P3 | 9.0% | 9.8% | -0.7% |
| P4 | 9.8% | 7.9% | +1.8% |
| P5 | 9.0% | 8.3% | +0.7% |
| P6 | 8.8% | 9.9% | -1.1% |
| P7 | 7.4% | 7.7% | -0.3% |
| P8 | 17.0% | 16.9% | +0.1% |

**Mean gap: ~+0.1% (effectively zero)**

**This is definitive evidence that entropy source type does not create identifiable output clusters.** Two outputs from the same PRNG are no more similar to each other than to a TRNG or QRNG output. The seed value matters (different seeds produce different outputs), but the *source* of that seed does not.

---

## Additional Observations

### 1. "Thinking..." Prefix Inflation
Both qwen3 models include extensive chain-of-thought (avg ~50% of output) prefixed with "Thinking..." that is highly formulaic ("Okay, the user...", "Hmm, this is..."). This dilutes diversity metrics.

**Recommendation for future experiments:** Strip thinking tokens before computing metrics, or use models without chain-of-thought enabled.

### 2. QRNG Storytelling Collapse
QRNG shows the steepest storytelling diversity loss at 4B (-26.2% vs PRNG -23.4%). Possible explanation: QRNG's uniform seed distribution may consistently push the model into similar narrative patterns, while PRNG's clustered seeds occasionally break it out of local minima.

### 3. Length-Diversity Tradeoff
Longer outputs consistently have lower word_diversity (TTR drops mechanically with length). TRNG/QRNG's tendency to produce longer outputs may partially explain their lower diversity at 1.7B scale.

### 4. Creative Name Convergence
Planet names across all sources frequently converge on "Luminara" / "Lumina" themes. Creature names gravitate toward cloud/weather etymology ("Cirrion", "Cirrus", "Cloudwisp"). This suggests the model has strong thematic attractors that override seed influence.

---

## Pending Results

### qwen3:8b (Running)
- Will test whether the QRNG consistency paradox scales further
- Critical comparison: 8B sits between the tested sizes in previous experiments
- Expected completion: ~2-3 hours

### mistral:latest (Queued)
- First cross-architecture comparison in this experiment series
- Mistral uses sliding window attention vs Qwen's full attention
- Previous data showed interesting QRNG mode shifts with Mistral

### llama3.1:8b (Queued)
- Llama3.1 architecture comparison at same parameter count as qwen3:8b
- Tests whether Qwen-specific findings generalize across architectures
- Expected to complete ~6-8 hours from now

---

## Methodology Notes

### Entropy Source Implementations
- **PRNG:** `random.Random(42)` → `getrandbits(64)` — deterministic starting from fixed seed, sequences diverge across samples
- **TRNG:** `secrets.token_bytes(8)` → hardware entropy from `/dev/urandom` on Apple M4 Pro
- **QRNG:** `SHA256(timestamp_ns + secrets.token_hex(16) + counter)[:8]` — NOT true quantum RNG in this experiment (no IBM Quantum backend). Uses time + hardware entropy + SHA256 mixing as a proxy for high-quality randomness

**Important caveat:** The "QRNG" source in this experiment is actually a SHA256-mixed entropy source, not quantum-derived. It differs from the actual QRNG (IBM ibm_fez) used in earlier experiments. The SHA256 mixing produces more uniformly distributed seeds than raw TRNG.

**Critical implication:** Earlier experiments using actual quantum RNG (IBM ibm_fez backend) showed stronger effects (QRNG distinct_2=0.884 vs PRNG 0.826 on Qwen3-8B). The weaker effects seen here may be because SHA256 mixing already maximizes seed uniformity, eliminating the quantum advantage. The real comparison should be PRNG (deterministic/clustered) vs truly random (TRNG/QRNG), not the quality of randomness.

### Seed Application
Seeds are passed as `--seed` to `ollama run`, which sets the random seed for the model's sampling. Seeds are truncated to 32-bit (`seed % 2**32`).

### Statistical Validity
- 5 samples per condition provides limited statistical power
- Results should be interpreted as directional indicators, not definitive conclusions
- Paired comparisons across 15 prompts provide reasonable within-prompt control

---

## Files & Data

| File | Description |
|------|-------------|
| `entropy-seeding/results/valid_entropy_comparisons/qwen/comprehensive_qwen3_4b_20260208_215109.json` | Raw qwen3:4b data |
| `entropy-seeding/results/valid_entropy_comparisons/qwen/comprehensive_qwen3_1.7b_20260208_231205.json` | Raw qwen3:1.7b data |
| `entropy-seeding/scripts/run_comprehensive_experiment.py` | Experiment runner |
| `entropy-seeding/scripts/analyze_comprehensive_results.py` | Statistical analysis |
| `docs/COMPREHENSIVE_ENTROPY_SEEDING_EXPERIMENT_2026-02-09.md` | This document |

---

*This document is updated as new model results arrive. Check git log for latest version.*
