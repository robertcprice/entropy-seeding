# Entropy Source Effects on Large Language Model Output

A comparative analysis of how different entropy sources affect text generation quality across multiple model architectures and scales.

## Overview

This repository contains experimental data comparing three entropy sources used in LLM text generation:

- **PRNG** (Pseudo-Random Number Generator): Mersenne Twister MT19937 algorithm
- **TRNG** (True Random Number Generator): Hardware entropy from `/dev/urandom` (Apple M4 Pro)
- **QRNG** (Quantum Random Number Generator): IBM Quantum ibm_fez backend (156 superconducting qubits)

## Research Questions

1. How does entropy source selection affect text generation metrics?
2. Does model size mediate entropy source effects?
3. Do different architectures (Dense vs MoE) respond differently to entropy variation?
4. Are there edge cases or failure modes specific to certain entropy sources?

## Models Tested

| Model Family | Architecture | Models Tested | Parameter Range |
|--------------|--------------|---------------|-----------------|
| Qwen3 | Dense Transformer | 0.6B, 1.7B, 4B, 8B, 14B, 32B | 0.6B - 32B |
| DeepSeek-R1 | Mixture of Experts | 32B, 70B | 32B - 70B |
| Qwen2.5 | Dense Transformer | 72B | 72B |

**Total:** 9 models with comprehensive PRNG/TRNG/QRNG testing

## Repository Structure

```
entropy-seeding/
├── README.md                           # This file
├── COMPREHENSIVE_REPORT.md              # Full analysis
│
├── results/                             # Experimental data
│   ├── qwen/                            # Qwen3 family results
│   │   ├── qwen3_0.6b_full_results.json
│   │   ├── qwen3_0.6b_summary.json
│   │   ├── qwen3_1.7b_full_results.json
│   │   ├── qwen3_1.7b_summary.json
│   │   ├── qwen3_4b/                    # Colored entropy variants
│   │   ├── qwen3_8b_full_results.json
│   │   ├── qwen3_14b_full_results.json
│   │   ├── qwen3_32b_full_results.json
│   │   ├── colored_entropy_9configs.json
│   │   └── ARCHITECTURE_REPORT.md
│   │
│   ├── qwen2.5/                         # Qwen2.5 72B (opposite pattern)
│   │   ├── hidden_variance_selfseed_qwen2_5-72b_*.json
│   │   ├── significance_qwen2_5-72b.json
│   │   └── significance_qwen2_5-72b.md
│   │
│   ├── deepseek-r1/                     # MoE architecture results
│   │   ├── deepseek-r1_32b_summary.json
│   │   ├── deepseek-r1_70b_full_results.json
│   │   └── ARCHITECTURE_REPORT.md
│   │
│   ├── cross_architecture/              # Cross-model comparisons
│   │   ├── CROSS_ARCHITECTURE_ANALYSIS.md
│   │   └── gemma2_27b_tre_experiment.json
│   │
│   ├── significance/                    # Statistical analysis
│   │   ├── significance_qwen3-8b.json
│   │   ├── significance_qwen3-8b.md
│   │   ├── significance_qwen3-14b.json
│   │   └── significance_qwen3-14b.md
│   │
│   ├── mixtral_8x22b/                   # Additional MoE data
│   ├── deepseek_r1_llama70b/            # Llama 70B data
│   ├── llama/                           # Llama architecture notes
│   ├── mistral/                         # Mistral architecture notes
│   │
│   ├── QUALITATIVE_ANALYSIS_ANOMALIES.md # Personality framework
│   ├── correlation_analysis.json        # Neuron correlations
│   ├── neural_modulation_rng_comparison.md
│   └── neural_quantum_rng_comparison.md
│
└── reports/                             # Individual entropy source reports
    ├── PRNG_DETAILED_REPORT.md
    ├── TRNG_DETAILED_REPORT.md
    └── QRNG_DETAILED_REPORT.md
```

## Key Findings

### 1. Architecture-Specific Responses

Different model families respond differently to entropy sources:

| Architecture | Typical Pattern | Exceptions |
|--------------|-----------------|------------|
| Qwen3 (Dense) | TRNG > QRNG > PRNG (8B+) | Small models (<8B) show higher sensitivity |
| Qwen2.5 (Dense) | **PRNG > TRNG ≈ QRNG** | Opposite pattern to Qwen3 |
| DeepSeek-R1 (MoE) | TRNG > PRNG | PRNG can cause catastrophic failure |

**Note:** The Qwen2.5 72B finding is particularly notable—it shows the opposite pattern of other tested models, with PRNG outperforming TRNG and QRNG on vocabulary diversity metrics.

### 2. Model Size Effects

Entropy source effects diminish as model size increases:

| Parameter Range | Sensitivity | TRNG Advantage (where present) |
|-----------------|-------------|-------------------------------|
| 0.6B - 1.7B | High | Critical for quality |
| 4B - 8B | Moderate | Noticeable improvement |
| 14B+ | Low | Minimal impact |

### 3. MoE Architecture Vulnerability

DeepSeek-R1 (Mixture of Experts) exhibited a catastrophic failure mode with PRNG:

**Prompt:** "What gives life meaning?"
**Entropy:** PRNG (seed=42)
**Result:** All metrics = 0.00, Perplexity = ∞, complete generation failure

Same model with TRNG or QRNG: Normal generation.

**Hypothesis:** Deterministic PRNG seeds can cause routing collisions in MoE architectures, leading to internal state deadlocks.

### 4. Textual Characteristics

Qualitative analysis reveals consistent output patterns by entropy source:

**PRNG Outputs:**
- More volatile quality
- Higher repetition on average
- Can fail catastrophically on certain prompts
- More conversational/academic tone observed

**TRNG Outputs:**
- More consistent quality
- Lower repetition rates
- Higher vocabulary diversity
- More natural text flow

**QRNG Outputs:**
- Highly structured formatting
- Lower repetition than PRNG
- More organized output structure
- Can appear overly constrained

## Example Outputs

### DeepSeek-R1 70B - Color Naming Task

**PRNG Output (seed=42):**
> "What a fascinating and imaginative question!
>
> ### Description of Elyndor:
> Elyndor is a shimmering, iridescent hue that shifts between luminous silver-gold and soft lavender..."

**Characteristics:** Academic tone, structured with headers, named color "Elyndor" (fantasy theme)

---

**TRNG Output (hardware seed):**
> "**Aurorin: The Celestial Color**
>
> Imagine a color named Aurorin—a mesmerizing blend of shimmering blues and greens that dance across the visual spectrum like the aurora borealis..."

**Characteristics:** Emotive language, natural flow, named color "Aurorin" (celestial theme)

---

**QRNG Output (quantum seed):**
> "### **The Color: "Lunaris"**
> **Name:** *Lunaris*
> ---
>
> ### **Emotions Evoked by Lunaris**
> 1. **Mystery**: The unknown depth of space..."

**Characteristics:** Highly organized, formatted structure, named color "Lunaris" (astronomical theme)

## Metrics

The following metrics were used to evaluate generation quality:

| Metric | Description | Interpretation |
|--------|-------------|----------------|
| distinct_2 | Unique bigram proportion | Higher = more diverse |
| TTR | Type-Token Ratio | Higher = richer vocabulary |
| Repetition | Character-level repetition | Lower = less repetitive |
| Shannon Entropy | Text information density | Higher = more unpredictable |
| Burstiness | Sentence length variance | Lower = more natural flow |
| Perplexity | Model confidence | Lower = more confident |

## Usage

### TRNG Implementation

```python
import struct

def get_trng_seed():
    """Generate seed from hardware entropy."""
    with open("/dev/urandom", "rb") as f:
        return struct.unpack("I", f.read(4))[0]
```

### QRNG Implementation

See repository for cached QRNG implementation using IBM Quantum measurements.

## Statistical Analysis

Results include statistical significance testing where applicable:

- Qwen3 8B: TRNG vs PRNG (distinct_2): p < 0.05
- Qwen3 14B: TRNG vs PRNG (distinct_2): p = 0.367 (not significant)
- Qwen2.5 72B: TRNG vs PRNG (distinct_2): p = 0.099 (trending negative)

See `results/significance/` for detailed statistical analyses.

## Limitations

1. **Sample Size:** Limited prompt set (14 prompts × 5 seeds per configuration)
2. **Architecture Coverage:** Not all model families tested
3. **Task Diversity:** Focused on creative/analytical tasks
4. **Single Hardware:** TRNG tested only on Apple M4 Pro
5. **QRNG Cache:** Quantum measurements pre-generated and cached

## Future Directions

1. Test additional architectures (Gemma, Llama, Mistral baseline)
2. Expand prompt diversity and sample sizes
3. Investigate Qwen2.5 opposite pattern
4. Test on different hardware platforms
5. Explore hybrid entropy sources

## Citation

If you use this data or research, please cite:

```bibtex
@software{entropy_seeding_2026,
  title={Entropy Source Effects on Large Language Model Output},
  author={Price, Robert},
  year={2026},
  url={https://github.com/robertcprice/entropy-seeding}
}
```

## License

Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International

## Acknowledgments

Inspired by Jordan Thelen's video "How to Summon AI Demons with LLMs"

---

**GitHub:** https://github.com/robertcprice/entropy-seeding
**Last Updated:** February 2026
