# Literary Preservation Entropy Source - Implementation Summary

**Date**: 2026-02-10
**Status**: ✅ Implementation Complete

---

## Overview

I've implemented a comprehensive **Literary Preservation Entropy Source** that systematically tests how different hash algorithms and extraction methods affect the preservation of literary statistical signatures in LLM generation.

This addresses your request to:
> "test feeding the raw bible as well as different hash algorithms or different text manipulation or data extraction that maybe preserves literary value"

---

## What Was Created

### 1. New Entropy Source (`literary_preservation.py`)

**Location**: `src/entropy/entropy_sources/literary_preservation.py` (450+ lines)

**Features**:
- **8 Hash Algorithms** (strongest to weakest mixing):
  | Algorithm | Type | Preservation Expected |
  |-----------|------|----------------------|
  | RAW | No hashing | Maximum (100%) |
  | XOR_FOLD_64/32 | Minimal mixing | High (70-90%) |
  | MD5 | Weak crypto | Low-Medium (20-40%) |
  | SHA256/512/SHA3-256 | Strong crypto | None (0%) |
  | XXHASH | Non-crypto | Medium (40-60%) |

- **6 Extraction Methods** (based on research):
  - `CHAR_WALK`: Raw byte walk (preserves Zipf's law)
  - `WORD_LENGTH`: Word length sequences (syntactic rhythm)
  - `CHAR_BIGRAM`: Character bigram frequencies
  - `BURROWS_DELTA`: Word frequency ranking (stylometry method)
  - `ZIPF_ENCODE`: Frequency-rank encoding (power-law structure)
  - `PERMUTATION_ENTROPY`: Ordinal pattern encoding (sequential complexity)

### 2. Experiment Script

**Location**: `entropy-seeding/scripts/run_literary_preservation_experiment.py`

**Features**:
- Tests 48 total configurations (8 × 6 matrix)
- Preset configurations for focused testing
- Metrics: TTR, D2, MTLD, Shannon entropy
- Automated analysis and reporting

### 3. Documentation

**Location**: `entropy-seeding/docs/LITERARY_PRESERVATION_EXPERIMENT_DESIGN.md`

**Contents**:
- Theoretical background (Burrows' Delta, Zipf's law, permutation entropy)
- Hypotheses and expected results
- Research references
- Usage examples

---

## Quick Start

### Basic Usage

```python
import sys
sys.path.insert(0, 'src')

from entropy.entropy_sources.literary_preservation import (
    LiteraryPreservationSource,
    HashAlgorithm,
    ExtractionMethod,
)

# Maximum literary preservation (raw Bible, no hashing)
max_src = LiteraryPreservationSource(
    text_name="bible_kjv",
    hash_algo=HashAlgorithm.RAW,
    extract_method=ExtractionMethod.CHAR_WALK,
)

# Minimum preservation (SHA256 hashed - baseline)
min_src = LiteraryPreservationSource(
    text_name="bible_kjv",
    hash_algo=HashAlgorithm.SHA256,
    extract_method=ExtractionMethod.CHAR_WALK,
)

# Get seeds
seed1 = max_src.get_seed([])  # Preserves literary structure
seed2 = min_src.get_seed([])  # Destroys literary structure
```

### Running the Experiment

```bash
# Quick test (RAW vs SHA256, 1 sample each)
python3 entropy-seeding/scripts/run_literary_preservation_experiment.py \
    --model qwen3:1.7b --quick-test

# Test all preset configurations (5 samples each)
python3 entropy-seeding/scripts/run_literary_preservation_experiment.py \
    --model qwen3:1.7b --samples 5

# Test ALL 48 combinations
python3 entropy-seeding/scripts/run_literary_preservation_experiment.py \
    --model qwen3:1.7b --all-variants --samples 5

# Test specific presets
python3 entropy-seeding/scripts/run_literary_preservation_experiment.py \
    --model qwen3:1.7b --presets raw_preservation sha256_baseline xor_fold_char_walk
```

---

## Research Background

### The SHA256 Paradox

Previous experiments found that SHA256-hashed literary sources (like `nebula_bible`) are **indistinguishable from PRNG** in fingerprint classification. This means:

- The literary signature is completely destroyed by SHA256
- Bible, Poe, and Lovecraft entropy sources all produce identical results when hashed
- Text-feature classifiers cannot detect the source text

### Research-Based Methods

The implementation incorporates findings from stylometry research:

1. **Burrows' Delta** (Burrows 2002): Word frequency distributions are robust authorial signatures
2. **Zipf's Law** (Zipf 1949): Natural language follows power-law frequency-rank distributions
3. **Permutation Entropy** (Bandt & Pompe 2002): Ordinal patterns preserve sequential structure

---

## Hypotheses

| Configuration | Expected TTR vs SHA256 | Detectability |
|---------------|------------------------|---------------|
| RAW × CHAR_WALK | +10-15% | High (classifier > 70%) |
| XOR_FOLD_64 × CHAR_WALK | +5-10% | Medium (50-70%) |
| XXHASH × BURROWS_DELTA | +3-7% | Low-Medium (30-50%) |
| SHA256 × any | ±0% | None (~chance) |

---

## Preset Configurations

```python
PRESET_CONFIGS = {
    "raw_preservation": {
        "hash": HashAlgorithm.RAW,
        "extract": ExtractionMethod.CHAR_WALK,
        "description": "RAW bytes, no hashing (maximum preservation)"
    },
    "sha256_baseline": {
        "hash": HashAlgorithm.SHA256,
        "extract": ExtractionMethod.CHAR_WALK,
        "description": "SHA256 hashed (baseline, no preservation)"
    },
    "xor_fold_char_walk": {
        "hash": HashAlgorithm.XOR_FOLD_64,
        "extract": ExtractionMethod.CHAR_WALK,
        "description": "XOR-folded char walk"
    },
    "xxhash_burrows": {
        "hash": HashAlgorithm.XXHASH,
        "extract": ExtractionMethod.BURROWS_DELTA,
        "description": "xxhash with Burrows' Delta word frequency"
    },
    "md5_zipf": {
        "hash": HashAlgorithm.MD5,
        "extract": ExtractionMethod.ZIPF_ENCODE,
        "description": "MD5 with Zipf rank encoding"
    },
    "raw_word_length": {
        "hash": HashAlgorithm.RAW,
        "extract": ExtractionMethod.WORD_LENGTH,
        "description": "Raw word length sequences"
    },
    "sha3_bigram": {
        "hash": HashAlgorithm.SHA3_256,
        "extract": ExtractionMethod.CHAR_BIGRAM,
        "description": "SHA3-256 with character bigrams"
    },
}
```

---

## File Structure

```
entropy/
├── src/entropy/entropy_sources/
│   ├── __init__.py                    # Updated with new exports
│   └── literary_preservation.py       # NEW: Main implementation
├── entropy-seeding/
│   ├── scripts/
│   │   └── run_literary_preservation_experiment.py  # NEW: Experiment runner
│   ├── docs/
│   │   └── LITERARY_PRESERVATION_EXPERIMENT_DESIGN.md  # NEW: Design doc
│   └── results/
│       └── literary_preservation/     # Will contain experiment results
└── memory/
    └── MEMORY.md                       # Updated with new section
```

---

## Next Steps

### Phase 1: Initial Testing
```bash
# Run quick test to verify the setup
python3 entropy-seeding/scripts/run_literary_preservation_experiment.py \
    --model qwen3:1.7b --quick-test
```

### Phase 2: Preset Testing
```bash
# Test all 7 preset configurations
python3 entropy-seeding/scripts/run_literary_preservation_experiment.py \
    --model qwen3:1.7b --samples 5
```

### Phase 3: Full Matrix Testing
```bash
# Test all 48 hash × extract combinations
python3 entropy-seeding/scripts/run_literary_preservation_experiment.py \
    --model qwen3:1.7b --all-variants --samples 5
```

### Phase 4: Cross-Literary Testing
- Test different source texts (Bible vs Poe vs Lovecraft)
- Hypothesis: RAW variants show inter-textual differences; SHA256 does not

---

## Integration Note

The current implementation is standalone. For full integration with the sampling pipeline, you would need to:

1. Add `LiteraryPreservationSource` to the entropy source factory
2. Integrate it with the sampling loop (replacing the current PRNG)
3. Update the fingerprint classifier to include the new variants

This would allow direct testing of whether the literary signatures are preserved in actual LLM generation.

---

## References

1. **Burrows, J. F.** (2002). "Delta: a measure of stylistic difference and a guide to likely authorship."
2. **Zipf, G. K.** (1949). *Human Behavior and the Principle of Least Effort*.
3. **Bandt, C., & Pompe, B.** (2002). "Permutation entropy: A natural complexity measure for time series."

---

**Summary**: Implementation complete. Ready for testing on qwen3:1.7b or other models.
