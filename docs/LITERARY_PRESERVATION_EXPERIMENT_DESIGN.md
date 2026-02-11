# Literary Preservation Experiment Design

**Purpose**: Systematically investigate how different hash algorithms and extraction methods affect the preservation of literary statistical signatures in LLM generation.

**Date**: 2026-02-10
**Status**: Implementation Complete

---

## Background: The SHA256 Paradox

### The Paradox
Our previous entropy seeding experiments revealed a surprising finding: **SHA256-hashed literary sources are completely invisible to text-feature classifiers**. When Bible text is hashed with SHA256 before seeding LLM generation, the resulting output is indistinguishable from PRNG-seeded generation.

This is surprising because:
1. SHA256 is a deterministic function — the same input always produces the same output
2. The Bible contains rich statistical structure (Zipfian word frequencies, character bigrams, syntactic patterns)
3. We expected some of this structure to survive the hashing process

### Why This Matters
If literary entropy is truly destroyed by SHA256:
- **Literary seeding may be futile**: Using Bible, Poe, or Lovecraft text for entropy may be no different from PRNG
- **Information loss**: We're discarding potentially valuable structured randomness
- **Literary diversity**: Different texts may have different effects on generation quality

---

## Research Questions

### Primary Questions
1. **Does SHA256 completely decorrelate literary sources?** (Confirm the SHA256 Paradox)
2. **Which hash algorithms preserve the most/least literary structure?** (Hash spectrum)
3. **Which extraction methods preserve authorial signatures?** (Extraction spectrum)
4. **Can classifiers detect text-derived entropy with non-cryptographic hashes?** (Detection threshold)

### Secondary Questions
1. Does XOR-folding preserve enough structure to be detectable?
2. Do word-frequency based methods (Burrows' Delta, Zipf) preserve authorial signatures better than character-based methods?
3. Is there a "sweet spot" — enough mixing for uniformity but enough preservation for literary structure?

---

## Experimental Design

### Hash Algorithm Spectrum

| Algorithm | Type | Mixing Strength | Expected Preservation |
|-----------|------|-----------------|----------------------|
| **RAW** | None | None | Maximum (100%) |
| **XOR_FOLD_64** | Minimal mixing | Very low | High (80-90%) |
| **XOR_FOLD_32** | Minimal mixing | Low | Medium-High (70-80%) |
| **MD5** | Weak crypto | Medium | Low-Medium (20-40%) |
| **SHA256** | Strong crypto | Very high | None (0%) |
| **SHA512** | Strong crypto | Very high | None (0%) |
| **SHA3_256** | Strong crypto (sponge) | Very high | None (0%) |
| **XXHASH** | Non-crypto | Low-Medium | Medium (40-60%) |

**Rationale**: This spectrum allows us to observe the gradual degradation of literary signatures as mixing strength increases.

### Extraction Method Spectrum

| Method | What It Preserves | Theoretical Basis |
|--------|-------------------|-------------------|
| **CHAR_WALK** | Character distribution (Zipf's law) | Byte frequency directly maps to int |
| **WORD_LENGTH** | Syntactic rhythm | Word lengths encode authorial style |
| **CHAR_BIGRAM** | Sequential character patterns | "th", "he", "in" frequencies are language-specific |
| **BURROWS_DELTA** | Word frequency ranking | Burrows' Delta stylometry method |
| **ZIPF_ENCODE** | Frequency-rank distribution | Power-law structure of natural language |
| **PERMUTATION_ENTROPY** | Sequential complexity | Ordinal pattern encoding (Bandt-Pompe) |

**Rationale**: Different methods capture different aspects of literary structure. Testing all six allows us to identify which features are most robust to hashing.

### Experimental Matrix

Total variants: 8 hash algorithms × 6 extraction methods = **48 configurations**

For practicality, we also define **preset configurations** that test the most interesting combinations:

```python
PRESET_CONFIGS = {
    "raw_preservation": (RAW, CHAR_WALK)           # Maximum preservation (control)
    "sha256_baseline": (SHA256, CHAR_WALK)         # Minimum preservation (baseline)
    "xor_fold_char_walk": (XOR_FOLD_64, CHAR_WALK) # Minimal mixing
    "xxhash_burrows": (XXHASH, BURROWS_DELTA)      # Non-crypto + word frequency
    "md5_zipf": (MD5, ZIPF_ENCODE)                # Weak crypto + Zipf
    "raw_word_length": (RAW, WORD_LENGTH)         # Syntactic rhythm focus
    "sha3_bigram": (SHA3_256, CHAR_BIGRAM)        # Different crypto + sequential
}
```

---

## Theoretical Background

### Stylometry and Author Attribution

#### Burrows' Delta Method
- **Source**: Burrows, J. F. (2002). "Delta: a measure of stylistic difference and a guide to likely authorship."
- **Principle**: Authors have characteristic word frequency distributions
- **Method**: Rank words by frequency, compare frequency vectors between texts
- **Application**: If we encode word frequencies as seeds, Burrows' Delta signatures should be preserved

#### Zipf's Law
- **Source**: Zipf, G. K. (1949). "Human Behavior and the Principle of Least Effort."
- **Principle**: Word frequency follows power-law distribution: f(r) ∝ 1/r^α
- **Application**: Natural language has characteristic Zipf exponent (~1.0 for English)
- **Preservation**: Hashing destroys the power-law structure, XOR-folding preserves it partially

#### Permutation Entropy
- **Source**: Bandt, C., & Pompe, B. (2002). "Permutation entropy: A natural complexity measure..."
- **Principle**: Encodes ordinal patterns instead of raw values
- **Application**: Preserves sequential structure while being robust to noise
- **Relevance**: Text has characteristic ordinal patterns (e.g., "the" often followed by "of", "and")

### Hash Function Properties

| Property | Cryptographic (SHA256) | Non-Cryptographic (xxhash) | Minimal (XOR) |
|----------|------------------------|---------------------------|---------------|
| Avalanche effect | Strong | Moderate | None |
| Bit independence | High | Medium | Low |
| Collision resistance | Yes | Partial | No |
| Structure preservation | No | Partial | Yes |
| Speed | Medium | Fast | Very Fast |

**Avalanche Effect**: A 1-bit input change changes ~50% of output bits. This destroys literary structure.

**Expected Outcome**: XOR-folding should preserve the most literary structure, SHA256 the least.

---

## Hypotheses

### Primary Hypotheses

1. **H1: SHA256 completely decorrelates literary sources**
   - Prediction: SHA256 variants will be indistinguishable from PRNG in classifier tests
   - Effect size: TTR difference < 2% compared to PRNG

2. **H2: RAW bytes show maximum literary preservation**
   - Prediction: RAW variants will be most distinguishable from PRNG
   - Effect size: TTR difference > 10% compared to SHA256

3. **H3: Hash strength correlates negatively with preservation**
   - Prediction: XOR_FOLD > MD5 > XXHASH > SHA256 in preservation
   - Rationale: Stronger mixing destroys more structure

4. **H4: Word-frequency methods preserve authorial signatures better than character methods**
   - Prediction: BURROWS_DELTA and ZIPF_ENCODE > CHAR_WALK in preservation
   - Rationale: Word frequencies are more distinctive than character distributions

### Secondary Hypotheses

5. **H5: XOR-folding provides uniform randomness while preserving structure**
   - Prediction: XOR_FOLD variants have near-uniform seed distributions but detectable literary signatures

6. **H6: Permutation entropy is robust to mild hashing**
   - Prediction: PERMUTATION_ENTROPY × XXHASH shows preservation where CHAR_WALK × XXHASH does not

---

## Evaluation Metrics

### Diversity Metrics
- **TTR** (Type-Token Ratio): Unique words / total words
- **D2** (Distinct-2): Unique bigrams / total bigrams
- **MTLD** (Measure of Textual Lexical Diversity): Length-corrected lexical diversity

### Information Metrics
- **Shannon Entropy**: Character-level entropy
- **Permutation Entropy**: Ordinal pattern entropy

### Statistical Tests
- **Cohen's d**: Effect size between configurations
- **Pairwise classification**: Can a classifier distinguish entropy sources?

---

## Implementation

### Files Created

1. **`src/entropy/entropy_sources/literary_preservation.py`**
   - `LiteraryPreservationSource` class
   - 8 hash algorithms implemented
   - 6 extraction methods implemented
   - Factory functions for common configurations

2. **`entropy-seeding/scripts/run_literary_preservation_experiment.py`**
   - Main experiment runner
   - 48 configuration matrix support
   - Preset configurations for focused testing
   - Metrics computation (TTR, D2, MTLD, entropy)
   - Result analysis and reporting

### Usage

```bash
# Quick test (RAW vs SHA256 baseline)
python entropy-seeding/scripts/run_literary_preservation_experiment.py \
    --model qwen3:1.7b --quick-test

# Test all preset configurations
python entropy-seeding/scripts/run_literary_preservation_experiment.py \
    --model qwen3:1.7b --samples 5

# Test ALL 48 hash × extract combinations
python entropy-seeding/scripts/run_literary_preservation_experiment.py \
    --model qwen3:1.7b --all-variants --samples 5

# Test specific presets
python entropy-seeding/scripts/run_literary_preservation_experiment.py \
    --model qwen3:1.7b --presets raw_preservation sha256_baseline xor_fold_char_walk
```

---

## Expected Results

### Quantitative Predictions

| Configuration | Expected TTR vs SHA256 | Detectability |
|---------------|------------------------|---------------|
| RAW × CHAR_WALK | +10-15% | High (classifier > 70%) |
| XOR_FOLD_64 × CHAR_WALK | +5-10% | Medium (classifier 50-70%) |
| XXHASH × BURROWS_DELTA | +3-7% | Low-Medium (classifier 30-50%) |
| MD5 × ZIPF_ENCODE | +1-3% | Low (classifier 20-30%) |
| SHA256 × any | ±0% | None (classifier ~ chance) |

### Qualitative Predictions

1. **RAW variants will show the most diversity**: Different literary texts (Bible, Poe, Lovecraft) will produce statistically distinguishable outputs

2. **SHA256 variants will be indistinguishable from PRNG**: All SHA256 configurations will cluster together, regardless of extraction method

3. **XOR-folding will be the sweet spot**: Provides near-uniform randomness while preserving detectable literary structure

4. **Word-frequency methods will be more robust**: BURROWS_DELTA and ZIPF_ENCODE will show preservation even with weak hashing (MD5, XXHASH)

---

## Follow-up Experiments

### Phase 2: Cross-Literary Testing
- Test different literary texts (Bible vs Poe vs Lovecraft vs Shakespeare)
- Hypothesis: RAW variants will show inter-textual differences; SHA256 will not

### Phase 3: Classifier Validation
- Train a classifier to distinguish entropy sources
- Use GroupKFold to avoid prompt leakage
- Test both pairwise (binary) and multi-class classification

### Phase 4: Quality Assessment
- Human evaluation of generation quality
- Does literary preservation affect perceived quality?
- Or is it purely a statistical artifact?

---

## References

1. **Burrows, J. F.** (2002). "Delta: a measure of stylistic difference and a guide to likely authorship." *Literary and Linguistic Computing*, 17(3), 267-287.

2. **Zipf, G. K.** (1949). *Human Behavior and the Principle of Least Effort*. Addison-Wesley.

3. **Bandt, C., & Pompe, B.** (2002). "Permutation entropy: A natural complexity measure for time series." *Physical Review Letters*, 88(17), 174102.

4. **Efron, B., & Stein, C.** (1981). "The jackknife estimate of variance." *The Annals of Statistics*, 9(3), 586-596.

5. **Cohen, J.** (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.). Lawrence Erlbaum.

---

## Notes

- **SHA256 Paradox**: The finding that SHA256-hashed literary sources are indistinguishable from PRNG in LLM generation
- **Zipf's Law**: Power-law distribution of word frequencies in natural language
- **Burrows' Delta**: Stylometric method using word frequency ranking for author attribution
- **Permutation Entropy**: Complexity measure based on ordinal patterns, robust to noise
- **XOR-folding**: Minimal mixing method that XORs input bytes into target size

---

**Document Status**: Complete (2026-02-10)
**Implementation Status**: Complete
**Ready for Testing**: Yes
