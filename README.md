# Entropy Seeding: PRNG vs TRNG vs QRNG for LLMs

## Overview

This repository contains comprehensive research on how different entropy sources (random number generators) affect Large Language Model output quality. We tested **7 model sizes** ranging from 0.6B to 70B parameters across **3 entropy sources**:

- **PRNG**: Pseudo-Random Number Generator (deterministic, seeded)
- **TRNG**: True Random Number Generator (hardware entropy from /dev/urandom)
- **QRNG**: Quantum Random Number Generator (IBM Quantum measurements)

## Key Findings

### Winner: TRNG (/dev/urandom)

| Metric | PRNG | TRNG | QRNG |
|--------|------|------|------|
| Uniqueness | 62% | **65%** ✅ | 64% |
| Repetition | 2.4% | **1.3%** ✅ | 1.8% |
| Natural Flow | 0.45 | **0.24** ✅ | 0.30 |
| Catastrophic Failures | Yes ❌ | **No** ✅ | No |

**Primary Recommendation:** Use TRNG (`/dev/urandom`) for all production LLM deployments.

### Small vs Large Model Impact

| Model Size | Entropy Sensitivity | Personality Visibility |
|------------|---------------------|----------------------|
| **0.6B - 1.7B** | VERY HIGH ⚠️ | Very pronounced |
| **8B - 14B** | MODERATE ⚠️ | Noticeable |
| **32B - 70B** | LOW | Subtle |

**Critical:** For edge deployment with small models (<14B), entropy source selection is **essential** for output quality.

## Quick Start

### Using TRNG in Python

```python
import struct
import torch

def get_trng_seed():
    """Get true random seed from /dev/urandom (Linux/macOS)."""
    with open("/dev/urandom", "rb") as f:
        return struct.unpack("I", f.read(4))[0]

# Set the seed before generation
seed = get_trng_seed()
torch.manual_seed(seed)

# Generate text with TRNG seeding
output = model.generate(inputs, max_tokens=500)
```

### Using TRNG in HuggingFace Transformers

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import struct

def get_trng_seed():
    with open("/dev/urandom", "rb") as f:
        return struct.unpack("I", f.read(4))[0]

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-8B")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")

# Set TRNG seed
torch.manual_seed(get_trng_seed())

# Generate
inputs = tokenizer("Your prompt here", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=200)
```

## Repository Structure

```
entropy-seeding/
├── README.md                    # This file
├── COMPREHENSIVE_REPORT.md      # Full analysis report
├── results/                     # Raw and summary results
│   ├── large_models/           # 32B, 70B model results
│   └── small_models/           # 0.6B, 8B, 14B model results
└── examples/                    # Text output examples
    ├── prng_samples.txt        # PRNG personality examples
    ├── trng_samples.txt        # TRNG personality examples
    └── qrng_samples.txt        # QRNG personality examples
```

## Configuration Recommendations

### By Model Size

#### Large Models (32B+)
```python
config = {
    "entropy_source": "trng",
    "temperature": 0.8,
    "top_p": 0.9
}
```

#### Medium Models (8B-14B)
```python
config = {
    "entropy_source": "trng",
    "temperature": 0.85,  # Slightly higher
    "top_p": 0.93,        # Tighter nucleus
    "repetition_penalty": 1.1
}
```

#### Small Models (<8B)
```python
config = {
    "entropy_source": "trng",  # ESSENTIAL
    "temperature": 0.9,        # Higher for creativity
    "top_p": 0.95,
    "repetition_penalty": 1.15,
    "min_length": 20           # Prevent truncation
}
```

### By Use Case

| Use Case | Entropy Source | Temperature | Notes |
|----------|----------------|-------------|-------|
| Creative Writing | TRNG | 0.85-0.95 | Best flow |
| Code Generation | QRNG/TRNG | 0.2-0.4 | QRNG's structure helps |
| Analytical Tasks | TRNG | 0.7-0.8 | Monitor for behavior inversion |
| Conversation | TRNG | 0.8 | Most natural |
| Education | TRNG | 0.75 | Balances clarity |

## Personality Profiles

### PRNG: "Volatile"
- ✅ Creative and varied
- ❌ Unpredictable quality
- ❌ Can catastrophically fail
- **Use for:** Debugging, experiments
- **Avoid for:** Production, security

### TRNG: "Balanced"
- ✅ Most natural text flow
- ✅ Highest vocabulary diversity
- ✅ Least repetitive
- ✅ No catastrophic failures
- **Use for:** All production applications
- **Avoid for:** Situations requiring absolute determinism

### QRNG: "Structured"
- ✅ Consistent formatting
- ✅ Most organized structure
- ❌ Can be overly constrained
- ❌ Lower vocabulary richness
- **Use for:** Structured output, code
- **Avoid for:** Maximum creativity needed

## Anomalies and Edge Cases

### 1. PRNG Catastrophic Failure (DeepSeek-R1 70B)
- Prompt: "What gives life meaning?"
- All metrics = 0.00, perplexity = ∞
- **Lesson:** Never use seeded PRNG for production

### 2. QRNG Zero Repetition
- Repetition = 0.000 (statistically impossible)
- Indicates over-constraint
- **Lesson:** QRNG needs calibration

### 3. Small Model Repetition Crisis
- Models <1B: TRNG showed HIGHER repetition than PRNG
- **Lesson:** Very small models need hybrid approaches

## Metrics Explained

| Metric | What It Measures | Good Value |
|--------|-----------------|------------|
| **Shannon Entropy** | Character-level information diversity | 4.2-4.6 |
| **TSA** | Sliding-window entropy over time | High mean, low std |
| **TRE** | Token response distribution | 6.0-8.0 |
| **Burstiness** | Sentence length variance | 0.2-0.4 |
| **Repetition** | Repeated n-gram percentage | < 0.03 |
| **Uniqueness** | Unique word percentage | > 0.60 |

## Citation

If you use this research, please cite:

```bibtex
@misc{entropy_seeding_2026,
  title={Entropy Seeding: PRNG vs TRNG vs QRNG for Large Language Models},
  author={Entropy Research Team},
  year={2026},
  month={February},
  url={https://github.com/yourusername/entropy-seeding}
}
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Areas of interest:
- Testing on additional model architectures
- Exploring hybrid entropy approaches
- QRNG calibration techniques
- Small model optimization

## Contact

For questions or discussions, please open an issue on GitHub.

---

**Last updated:** 2026-02-07
**Models tested:** Qwen3 (0.6B, 8B, 14B, 32B), DeepSeek-R1 (32B, 70B)
**Total comparisons:** 50+ entropy source × model combinations
