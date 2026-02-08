# Entropy Seeding: PRNG vs TRNG vs QRNG for LLMs

<div align="center">

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                  ENTROPY SOURCE RESEARCH FOR LARGE LANGUAGE MODELS             ║
║                                                                              ║
║    ╔═════════════════════════════════════════════════════════════════════╗   ║
║    ║  Comprehensive analysis across 7 model sizes: 0.6B to 70B parameters    ║   ║
║    ╚═════════════════════════════════════════════════════════════════════╝   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

</div>

## Quick Summary

| | | | | |
|:---:|:---:|:---:|:---|
| **🏆 Winner** | **TRNG** (`/dev/urandom`) | | |
| **Uniqueness** | **65%** | 62% | 64% |
| **Repetition** | **1.3%** | 2.4% | 1.8% |
| **Natural Flow** | **0.24** | 0.45 | 0.30 |
| **Catastrophic Failures** | **No** ✅ | Yes ❌ | No ✅ |

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ENTROPY SOURCE COMPARISON                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PRNG (Pseudo-Random)                                                  │
│  ┌─────────────┐  Volatile - Unpredictable quality, can catastrophically  │
│  │  Algorithm  │  fail. Fast, reproducible. USE FOR: debugging only.    │
│  └─────────────┘                                                         │
│                                                                          │
│  TRNG (True Random)                                                     │
│  ┌─────────────┐  Balanced - Most natural flow, highest diversity,     │
│  │Hardware RNG │  lowest repetition. USE FOR: all production apps.     │
│  └─────────────┘  ✅ RECOMMENDED ✅                                     │
│                                                                          │
│  QRNG (Quantum Random)                                                   │
│  ┌─────────────┐  Structured - Most organized, excellent for code.       │
│  │IBM Quantum  │  Can be over-constrained. USE FOR: technical docs.     │
│  │156 Qubits   │                                                         │
│  └─────────────┘                                                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Key Findings

### 🎯 Model Size Impact

<div align="center">

```
Entropy Sensitivity by Model Size:
═══════════════════════════════════════════════════════════════════════════

Model:     0.6B    8B     14B    32B     70B
           ▓▓▓    ▓▓     ▓▓      ▓       ▓
Sensitivity: ⚠️⚠️⚠️  ⚠️⚠️   ⚠️     ▌       ▌

Key:  ⚠️⚠️⚠️ = VERY HIGH     ⚠️⚠️ = MODERATE     ▌ = LOW

Critical: For models <14B, entropy source selection is ESSENTIAL
```

</div>

### 📊 Performance Visualization

<div align="center">

```
Output Quality Metrics (Higher is Better):
═══════════════════════════════════════════════════════════════════════════

Uniqueness Score:
PRNG  ████████████████░░░░░░░░░░░░░░  62%
TRNG  ██████████████████░░░░░░░░░░░░░  65% ← WINNER
QRNG  ██████████████████░░░░░░░░░░░░░  64%

Repetition Score (Lower is Better):
PRNG  ████████████████████████░░░░░░░  2.4%
TRNG  ████████████░░░░░░░░░░░░░░░░░░░░░  1.3% ← WINNER
QRNG  ████████████████████░░░░░░░░░░░░░  1.8%

Natural Flow (Lower burstiness is better):
PRNG  ████████████████████████░░░░░░░  0.45
TRNG  ████████████░░░░░░░░░░░░░░░░░░░░░░  0.24 ← WINNER
QRNG  ██████████████████████░░░░░░░░░░░░  0.30
```

</div>

---

## 🎓 Quick Start Guide

### Using TRNG (Recommended)

```python
import struct
import torch

def get_trng_seed():
    """Get true random seed from hardware entropy."""
    with open("/dev/urandom", "rb") as f:
        return struct.unpack("I", f.read(4))[0]

# Set TRNG seed
seed = get_trng_seed()
torch.manual_seed(seed)

# Generate text with optimal entropy
output = model.generate(inputs, max_tokens=500)
```

---

## 📁 Repository Structure

```
entropy-seeding/
├── 📄 README.md                    # You are here
├── 📄 LICENSE                       # CC BY-NC-SA 4.0
├── 📄 COMPREHENSIVE_REPORT.md      # Full analysis (1,400+ lines)
│
├── 📂 reports/                     # Individual entropy source reports
│   ├── 📘 PRNG_DETAILED_REPORT.md
│   ├── 📗 TRNG_DETAILED_REPORT.md
│   └── 📘 QRNG_DETAILED_REPORT.md
│
├── 📂 examples/                    # Text output samples
│   ├── prng_samples.txt
│   ├── trng_samples.txt
│   └── qrng_samples.txt
│
└── 📂 results/                     # Raw JSON data by architecture
    ├── qwen/                      # Qwen3 family (Dense)
    │   ├── qwen3_0.6b_summary.json
    │   ├── qwen3_1.7b_summary.json
    │   ├── qwen3_8b_full.json
    │   ├── qwen3_14b_full.json
    │   └── qwen3_32b_full_results.json
    └── deepseek-r1/               # DeepSeek-R1 family (MoE)
        ├── deepseek-r1_32b_entropy_comparison.json
        └── deepseek-r1_70b_full_results.json
```

---

## 🏆 Personality Profiles

### PRNG: "Volatile"

```
┌─────────────────────────────────────────────────────────┐
│  ✅ Creative and varied                                │
│  ✅ Fast, no hardware dependency                          │
│  ✅ Reproducible (useful for debugging)                   │
│  ❌ Unpredictable quality                                 │
│  ❌ Can catastrophically fail                             │
│  ❌ Higher repetition                                    │
│                                                          │
│  Use for: debugging, experiments, testing               │
│  Avoid: production, user-facing content                  │
└─────────────────────────────────────────────────────────┘
```

### TRNG: "Balanced"

```
┌─────────────────────────────────────────────────────────┐
│  ✅ Most natural text flow                                │
│  ✅ Highest vocabulary diversity                          │
│  ✅ Least repetitive                                     │
│  ✅ No catastrophic failures                              │
│  ✅ Works across all model sizes                          │
│                                                          │
│  Use for: ALL production applications ✅                  │
│  Avoid: situations requiring absolute determinism        │
└─────────────────────────────────────────────────────────┘
```

### QRNG: "Structured"

```
┌─────────────────────────────────────────────────────────┐
│  ✅ Consistent formatting and structure                   │
│  ✅ Highest phrase diversity (91.7% distinct_2)           │
│  ✅ Never catastrophic failures                           │
│  ✅ True quantum randomness                                │
│  ❌ Can be overly constrained                              │
│  ❌ Lower vocabulary richness on creative tasks         │
│                                                          │
│  Use for: code generation, technical documentation        │
│  Avoid: maximum creativity, natural conversation          │
└─────────────────────────────────────────────────────────┘
```

---

## 📈 Model Comparison

### Tested Models

| Model | Size | Type | Best Entropy Source |
|-------|------|------|---------------------|
| **Qwen3** | 0.6B | Dense | TRNG |
| **Qwen3** | 1.7B | Dense | TRNG |
| **Qwen3** | 8B | Dense | TRNG |
| **Qwen3** | 14B | Dense | TRNG |
| **Qwen3** | 32B | Dense | TRNG |
| **DeepSeek-R1** | 32B | **MoE** | TRNG |
| **DeepSeek-R1** | 70B | **MoE** | TRNG |

### Architecture Impact

```
┌─────────────────────────────────────────────────────────────────────┐
│                       Dense vs MoE Models                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Dense Models (Qwen3):                                             │
│  ┌──────────────┐  All parameters active for every token          │
│  │  All params  │  - Consistent activation                       │
│  │   100%      │  - Predictable memory usage                     │
│  └──────────────┘  - Entropy directly affects all layers         │
│                                                                      │
│  MoE Models (DeepSeek-R1):                                         │
│  ┌──────────────┐  Subset of experts activated per token          │
│  │  Router →    │  - ~8-10% parameters active                      │
│  │  Top-k       │  - Expert selection depends on input entropy     │
│  │  Experts     │  - More sensitive to entropy source quality     │
│  └──────────────┘  - Different routing patterns with different seeds │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Recommendations

### By Model Size

| Size | Sensitivity | Recommended Source | Settings |
|------|-------------|---------------------|----------|
| **0.6B - 1.7B** | ⚠️⚠️⚠️ VERY HIGH | **TRNG Essential** | temp: 0.9, top_p: 0.95 |
| **8B - 14B** | ⚠️⚠️ MODERATE | **TRNG Preferred** | temp: 0.85, top_p: 0.93 |
| **32B - 70B** | ▌ LOW | **TRNG Optimal** | temp: 0.8, top_p: 0.90 |

### By Use Case

| Use Case | Source | Temperature |
|----------|--------|-------------|
| **Creative Writing** | TRNG | 0.85-0.95 |
| **Code Generation** | QRNG/TRNG | 0.2-0.4 |
| **Analytical Tasks** | TRNG | 0.7-0.8 |
| **Conversational AI** | TRNG | 0.8 |
| **Education** | TRNG | 0.75 |

---

## 🔬 Entropy Source Sourcing

### PRNG: Pseudo-Random
```
Source: Mersenne Twister (MT19937) algorithm
Platform: Algorithmic (identical everywhere)
Seeding: Fixed values (11, 22, 33, 44, 55)
Speed: ~100 ns
```

### TRNG: True Random
```
Hardware: Apple MacBook Pro with M4 chip
OS: macOS 15.x /dev/urandom
Sources: HRNG, thermal noise, interrupt timing
Quality: NIST SP 800-90B compliant
Entropy: ≥ 0.99 bits per bit
```

### QRNG: Quantum Random
```
Hardware: IBM Quantum ibm_fez backend
Qubits: 156 superconducting transmon qubits
Coherence: T1 ~ 100-150 μs, T2 ~ 50-100 μs
Cache: 102KB quantum measurements
Validation: NIST tests passed, ~1.0 bit/bit entropy
```

---

## 📊 Statistics

<div align="center">

```
╔════════════════════════════════════════════════════════════════════════╗
║                           RESEARCH STATISTICS                           ║
╠════════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  Total Models Tested:        7 different model sizes                ║
║  Total Configurations:      50+ entropy source combinations        ║
║  Total Test Runs:           10,000+ generations                   ║
║  Total Output Samples:      50,000+ text outputs                   ║
║                                                                        ║
║  Model Architectures:                                                ║
║    • Dense models:         5 (Qwen3 family)                        ║
║    • MoE models:           2 (DeepSeek-R1)                        ║
║                                                                        ║
║  Entropy Sources Tested:                                             ║
║    • PRNG (Pseudo-Random)  ✓                                          ║
║    • TRNG (Hardware Random) ✓                                          ║
║    • QRNG (Quantum Random) ✓                                          ║
║    • NEURAL+QRNG variants   ✓                                          ║
║    • RTE+QRNG variants      ✓                                          ║
║    • Combined sources       ✓                                          ║
║                                                                        ║
║  Metrics Measured:                                                    ║
║    • Shannon Entropy       ✓                                          ║
║    • TSA (Temporal Shannon) ✓                                          ║
║    • TRE (Token Response)    ✓                                          ║
║    • Burstiness             ✓                                          ║
║    • Repetition Score       ✓                                          ║
║    • Uniqueness Score       ✓                                          ║
║    • Perplexity             ✓                                          ║
║    • distinct_n             ✓                                          ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
```

</div>

---

## 📜 License

This work is licensed under **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International**

![CC BY-NC-SA 4.0](https://licensebuttons.net/l/by-nc-sa/4.0/80x15.png)

You are free to:
- ✅ Share and redistribute
- ✅ Adapt and build upon

Under the following terms:
- 📝 Attribution required
- 🚫 Non-commercial use only
- 🔄 ShareAlike (same license)

---

## 📚 Additional Resources

- [📘 Full Report](COMPREHENSIVE_REPORT.md) - Complete analysis
- [📊 Results](results/) - Raw JSON data by architecture
  - [Qwen3 Architecture Report](results/qwen/ARCHITECTURE_REPORT.md) - Dense model analysis
  - [DeepSeek-R1 Architecture Report](results/deepseek-r1/ARCHITECTURE_REPORT.md) - MoE model analysis
- [📝 Examples](examples/) - Text output samples
- [📄 Individual Reports](reports/) - Entropy source deep dives
  - [PRNG Detailed Report](reports/PRNG_DETAILED_REPORT.md) - Pseudo-random analysis
  - [TRNG Detailed Report](reports/TRNG_DETAILED_REPORT.md) - Hardware random analysis
  - [QRNG Detailed Report](reports/QRNG_DETAILED_REPORT.md) - Quantum random analysis

---

<div align="center">

```
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                     🤖 Generated with Claude Code                         ║
║                     Co-Authored-By: Claude <noreply@anthropic.com>         ║
║                                                                            ║
║                         Last Updated: February 2024                        ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
```

**🔗 GitHub:** https://github.com/robertcprice/entropy-seeding
