# Entropy Source Effects on Large Language Model Output

> **⚠️ DATA INTEGRITY NOTICE:** Portions of this repository contain invalid experimental data. See [DATA_INTEGRITY.md](DATA_INTEGRITY.md) for details on which results are valid and which are not.

A comparative analysis of how different entropy sources affect text generation quality across multiple model architectures and scales.

## Overview

This repository contains experimental data comparing three entropy sources used in LLM text generation:

- **PRNG** (Pseudo-Random Number Generator): Mersenne Twister MT19937 algorithm
- **TRNG** (True Random Number Generator): Hardware entropy from `/dev/urandom` (Apple M4 Pro)
- **QRNG** (Quantum Random Number Generator): IBM Quantum ibm_fez backend (156 superconducting qubits)

## Data Integrity Status

**⚠️ CRITICAL:** A significant portion of the Qwen model results contain invalid data where different entropy seeds produced identical outputs.

### Valid Data (✅)
- **DeepSeek-R1 32B and 70B** entropy comparisons show genuine PRNG vs TRNG vs QRNG differences
- Documented catastrophic PRNG failure on philosophy prompt (DeepSeek-R1 70B)
- Qualitative analysis of text output characteristics

### Invalid Data (⚠️)
- **Qwen 0.6B, 1.7B, 8B, 14B** results with `hidden_variance_selfseed` format
- ~85% of these results show identical outputs across seeds 11, 22, 33, 44, 55
- Statistical significance tests for these models are based on flawed comparisons

**See [DATA_INTEGRITY.md](DATA_INTEGRITY.md) for detailed assessment.**

## Research Questions

1. ~~How does entropy source selection affect text generation metrics?~~ **Partially Answered** (valid only for DeepSeek-R1)
2. ~~Does model size mediate entropy source effects?~~ **Cannot Be Determined** (invalid Qwen data)
3. ~~Do different architectures (Dense vs MoE) respond differently to entropy variation?~~ **Insufficient Valid Data**
4. **Are there edge cases or failure modes specific to certain entropy sources?** **YES** - PRNG catastrophic failure documented

## Models Tested

| Model Family | Architecture | Models Tested | Data Status |
|--------------|--------------|---------------|-------------|
| Qwen3 | Dense Transformer | 0.6B, 1.7B, 4B, 8B, 14B, 32B | ⚠️ **INVALID** (identical outputs) |
| DeepSeek-R1 | Mixture of Experts | 32B, 70B | ✅ **VALID** |
| Qwen2.5 | Dense Transformer | 72B | ⚠️ **QUESTIONABLE** |

**Valid Results:** Only DeepSeek-R1 32B and 70B have confirmed valid entropy source comparisons.

## Repository Structure

```
entropy-seeding/
├── README.md                           # This file
├── DATA_INTEGRITY.md                    # Data validity assessment
├── COMPREHENSIVE_REPORT.md              # Original analysis report
├── COMPREHENSIVE_ENTROPY_SEEDING_EXPERIMENT_2026-02-09.md  # Full comprehensive report
├── METRICS_GLOSSARY.md                  # Metric definitions and interpretation guide
│
├── reports/
│   ├── PRNG_DETAILED_REPORT.md          # PRNG entropy source detailed analysis
│   ├── TRNG_DETAILED_REPORT.md          # TRNG entropy source detailed analysis
│   ├── QRNG_DETAILED_REPORT.md          # QRNG entropy source detailed analysis
│   ├── FINGERPRINT_CLASSIFIER_REPORT.md # Fingerprint classification experiment
│   └── NEBULA_ENTROPY_SOURCE_EXPLAINED.md # Nebula 5-layer entropy explainer
│
├── results/
│   ├── fingerprint/                     # Fingerprint classifier results
│   │   └── fingerprint_classifier_qwen3_8b_results.json
│   │
│   ├── valid_entropy_comparisons/       # Validated entropy comparison data
│   │   ├── qwen/                        # Qwen 0.6B → 8B results
│   │   ├── llama/                       # Llama 3.1-8B results
│   │   ├── mistral/                     # Mistral 7B results
│   │   └── deepseek/                    # DeepSeek-R1 32B/70B results
│   │
│   ├── entropy_source_comparisons/      # Original PRNG/TRNG/QRNG comparisons
│   │   ├── deepseek_r1/
│   │   ├── qwen_models/
│   │   ├── prng_trng_qrng/
│   │   └── documentation/
│   │
│   ├── cross_architecture/              # Dense vs SWA vs GQA comparison
│   ├── significance/                    # Statistical significance tests
│   └── formatted_summaries/             # Summary reports per model
│
└── scripts/                             # Analysis and experiment scripts
```

## Unified File Naming Convention

**All entropy comparison files use: `{model}_prng_trng_qrng.json`**

- `*_extended.json` = Tests 7 QRNG variants (INT, FLOAT, HASH, BITS, TEMP, MOD)
- `*_v2.json` = Repeated experiment run
- `*_qualitative_findings.md` = Qualitative analysis
- `*_evidence_summary.md` = Statistical evidence summary

**Note:** Other directories contain unrelated experiments:
- `quantum_activation/` = Neural network activation functions (NOT QRNG)
- `hidden_variance_selfseed/` = Invalid data (identical outputs across seeds)

## Key Findings (Based on Valid Data Only)

### ✅ VALID FINDING: QRNG Causes Catastrophic Mode Shifts (Qwen3-8B, Qwen3-14B)

**Documentation:** `/results/valid_entropy_comparisons/QUANTUM_RNG_QUALITATIVE_ANALYSIS_2026-02-04.md`

**Qwen 14B - QRNG_INT Mode Shift:**
- Started with: "The old lighthouse keeper had never seen anything like it."
- **Suddenly switched to:** Multiple-choice test format with "A. operating at full capacity / B. visited by tourists / C. abandoned / D. under repair"
- **Then added meta-commentary:** "Okay, let's see. The question is about..."

**Interpretation:** QRNG_INT caused the model to completely switch modes from narrative generation to test-taking mode, then become self-aware about it.

---

### ✅ VALID FINDING: TRNG Causes Language Mixing (Qwen3-8B)

**Documentation:** `/results/valid_entropy_comparisons/QUANTUM_RNG_QUALITATIVE_ANALYSIS_2026-02-04.md`

**TRNG Language Mixing:**
> Prompt: "She opened the letter, and everything changed."
> Output: "...What's the next sentence? The next sentence could be... 翻译句子并解析句子成分..."

**Translation:** "Translate the sentence and analyze the sentence components..."

**Interpretation:** TRNG caused the model to switch from English to Chinese mid-generation, then back to English.

---

### ✅ VALID FINDING: Different Entropy Sources = Different "Personalities"

**Table: Text Generation Characteristics by Entropy Source**

| Entropy Source | Creativity | Coherence | Meta-Cognition | Glitches |
|----------------|------------|-----------|----------------|----------|
| **PRNG** | Medium | **High** | Moderate | Repetition, perspective shifts |
| **TRNG** | High | Medium | **High** | **Language mixing**, self-aware breaks |
| **QRNG_INT** | **Highest** | Low | **Very High** | **Catastrophic mode shifts** |

**Key Insight:** QRNG produces the most creative outputs but also the most severe glitches. This is a fundamental trade-off.

---

### ✅ VALID FINDING: PRNG Catastrophic Failure (DeepSeek-R1 70B)

**Prompt:** Philosophy question about consciousness
**Entropy:** PRNG (seed=42)
**Result:** All metrics = 0.00, Perplexity = ∞, complete generation failure

Same model with TRNG: Normal generation (Shannon = 4.44, Perplexity = 195.74)

**Implication:** Deterministic PRNG seeds can cause internal state collisions in MoE architectures, leading to complete generation failure.

### 2. Different Entropy Sources Produce Different Outputs (VALID)

**Color Naming Task (DeepSeek-R1 70B):**
- **PRNG:** Named color "Elyndor" (fantasy theme), structured headers, academic tone
- **TRNG:** Named color "Aurorin" (celestial theme), emotive language, flowing description
- **QRNG:** Named color "Lunaris" (astronomical theme), analytical tone, highly organized format

### ✅ VALID FINDING: Entropy Source Fingerprints Partially Detectable (Qwen3-8B)

**Documentation:** [`reports/FINGERPRINT_CLASSIFIER_REPORT.md`](reports/FINGERPRINT_CLASSIFIER_REPORT.md)

A Random Forest classifier trained to detect which entropy source was used from text features alone, using LeaveOneGroupOut CV to prevent prompt leakage:

- **7-way multiclass:** 18.0% accuracy (14.3% baseline) — marginal, signal too weak for universal detection
- **Pairwise binary:** **9 of 21 pairs above 60%**, best pair **prng vs self_seed_sfc = 85.7%**
- **nebula_bible ~50% vs everything** — SHA256 hash chain makes it indistinguishable from PRNG

**Key insight:** Sources with fundamentally different seed mechanisms (deterministic PRNG vs feedback-loop self-seeding) leave clearly distinguishable traces. Hash-chain sources (Nebula) successfully mask their origin.

**Top discriminating features:** prompt-normalized hidden entropy trajectory (slope, ratio), sentence length variation, diversity ratios.

---

### ✅ VALID FINDING: Nebula 5-Layer Hierarchical Entropy (Text-Derived RNG)

**Documentation:** [`reports/NEBULA_ENTROPY_SOURCE_EXPLAINED.md`](reports/NEBULA_ENTROPY_SOURCE_EXPLAINED.md)

Nebula extracts entropy from literary texts through 5 orthogonal layers (chunk hashes, frequency signatures, word boundaries, positional encoding, cross-chunk entanglement) combined via prime-number gear ratios. Key properties:

- **Reduces text-induced bias by 23.8%** vs single-layer literary hash chain
- **Indistinguishable from PRNG** via text-feature classifier at 8B scale (SHA256 Paradox)
- **Still measurably affects generation** — Bible KJV shows -25.2% D2 and 2.1x first-person pronouns vs PRNG
- **22 literary texts** available as entropy sources from Project Gutenberg corpus

---

### 3. ~~Model Size Effects~~ (INVALID DATA - CANNOT DETERMINE)

The Qwen model data showing size-dependent effects contains identical outputs across different seeds and **cannot be used** for this analysis.

### 4. ~~Architecture-Specific Responses~~ (INSUFFICIENT VALID DATA)

Claims about Qwen3 vs Qwen2.5 patterns are based on invalid data. Only DeepSeek-R1 has valid entropy comparisons.

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

### Completed (Feb 2026)
- ~~Test additional architectures~~ — Llama 3.1-8B (GQA) and Mistral 7B (SWA) now tested alongside Qwen3-8B (Dense)
- ~~Expand prompt diversity~~ — 15 single-turn + 3 multi-turn = 360 generations per model
- ~~Explore hybrid entropy sources~~ — 10 entropy sources tested including self-seeding, hidden variance, Nebula

### Open Research Directions
1. **Nebula genre sweep at scale** — Test all 22 literary texts as entropy sources on 8B+ models to quantify genre-specific coloring effects
2. **Nebula layer ablation** — Systematically measure each of the 5 layers' contribution to debiasing and coloring
3. **Token-level fingerprint features** — Current text-feature classifier is marginal; token-ID sequences, softmax entropy trajectories, or generation perplexity curves may carry stronger signal
4. **Power-up sample sizes** — n=70 per source is insufficient for statistical significance on many metrics; target n=300+
5. **Entropy-based style transfer** — Test whether different literary entropy sources can steer generation style without model modification
6. **Entropy watermarking system** — Use private literary texts as watermark keys, detect via statistical correlation with Nebula walk pattern
7. **SHA256 Paradox formalization** — Prove theoretically why sequential hash consumption preserves structural information (information theory paper)
8. **Recursive modulation dynamics** — Map the phase space of RecursiveModulation feedback_gain × modulation_mode × base_source
9. **Fingerprint at smaller scales** — 0.6B models may be more susceptible to entropy source effects; repeat classifier experiment at that scale

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
