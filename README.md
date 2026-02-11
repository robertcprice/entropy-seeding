# Entropy Seeding in Large Language Models

**How randomness sources affect AI-generated text**

---

## Key Terms

| Term | Meaning |
|------|---------|
| **Entropy** | Randomness used by AI models to make creative choices |
| **PRNG** | Pseudo-Random Number Generator (software-based, deterministic) |
| **TRNG** | True Random Number Generator (hardware-based, physical) |
| **QRNG** | Quantum Random Number Generator (quantum physics-based) |
| **Seed** | The starting number that initializes random generation |
| **Temperature** | A setting that controls how "random" or "creative" model outputs are |
| **Perplexity** | A measure of how "surprised" a model is by text (lower = more confident) |
| **Shannon Entropy** | Information density—how unpredictable the text is |

---

## What This Project Explores

When an AI like ChatGPT generates text, it uses randomness to choose which words come next. This project asks: **Does the source of that randomness matter?**

We compare three ways of generating randomness:
- **PRNG** (Mersenne Twister algorithm) — standard software randomness
- **TRNG** (hardware entropy from `/dev/urandom`) — physical randomness from your computer
- **QRNG** (IBM Quantum ibm_fez) — randomness from quantum measurements

And we test whether these different sources produce meaningfully different text.

---

## Main Findings

### 1. Different Entropy Sources Produce Different Text Qualities

Each entropy source seems to give text a different "personality":

| Source | Creativity | Coherence | Notable Characteristics |
|--------|------------|-----------|-------------------------|
| **PRNG** | Medium | High | More structured, can fail catastrophically on certain prompts |
| **TRNG** | High | Medium | Natural flow, richer vocabulary, sometimes switches languages |
| **QRNG** | Highest | Lower | Very creative but prone to bizarre glitches and mode shifts |

### 2. Documented PRNG Catastrophic Failure

On DeepSeek-R1 70B with a philosophy prompt, using PRNG seed=42 caused **complete generation failure**:

```
Prompt: "What gives life meaning?"
PRNG (seed=42):  All metrics = 0.0, Perplexity = ∞  →  FAILED
TRNG:              Shannon = 4.44, Perplexity = 195.74  →  WORKING
```

**Why?** In "Mixture of Experts" architectures like DeepSeek-R1, deterministic PRNG seeds can cause internal routing collisions—like traffic getting stuck in a roundabout forever.

### 3. QRNG Causes Catastrophic Mode Shifts

On Qwen3-14B, QRNG_INT caused the model to suddenly switch from storytelling to test-taking:

> **Started with:** "The old lighthouse keeper had never seen anything like it."
> **Suddenly:** "A. operating at full capacity / B. visited by tourists / C. abandoned / D. under repair"
> **Then:** "Okay, let's see. The question is about..."

The model became self-aware about its mode change—a fascinating glitch.

### 4. TRNG Causes Language Mixing

On Qwen3-8B, TRNG caused the model to switch from English to Chinese mid-generation:

> Prompt: "She opened the letter, and everything changed."
> Output: "...What's the next sentence? The next sentence could be... **翻译句子并解析句子成分**..."

Translation: "Translate the sentence and analyze the sentence components..."

Then it switched back to English as if nothing happened.

### 5. Color Naming Task — Different Names for Different Sources

When asked to invent and describe a new color, DeepSeek-R1 70B gave different answers based on entropy source:

| Source | Color Name | Theme |
|--------|------------|-------|
| **PRNG** | Elyndor | Fantasy |
| **TRNG** | Aurorin | Celestial |
| **QRNG** | Lunaris | Astronomical |

Same model, same prompt, different randomness → different creative choices.

---

## Fingerprinting Experiment

Can we detect which entropy source was used just by reading the text?

We trained a Random Forest classifier on text features alone:

| Task | Accuracy | Baseline |
|------|----------|----------|
| 7-way multiclass | 18.0% | 14.3% |
| Best binary pair | **85.7%** | 50% |

**Key insight:** Sources with fundamentally different mechanisms (deterministic vs. feedback-loop) leave clearly distinguishable traces. But hash-chain sources are virtually indistinguishable from PRNG—the "SHA256 Paradox."

**Top detecting features:**
- Hidden entropy trajectory patterns
- Sentence length variation
- Vocabulary diversity ratios

---

## Nebula: Text-Derived Entropy

We also developed **Nebula**, a system that extracts entropy from literary texts through 5 orthogonal layers:

1. Chunk hashes
2. Frequency signatures
3. Word boundaries
4. Positional encoding
5. Cross-chunk entanglement

Combined via prime-number gear ratios, Nebula:
- Reduces text-induced bias by 23.8% vs. single-layer literary hash chain
- Is indistinguishable from PRNG via text-feature classifier (SHA256 Paradox)
- Still measurably affects generation—Bible KJV shows -25.2% repetition and 2.1× more first-person pronouns vs. PRNG
- Has 22 literary texts available as entropy sources from Project Gutenberg

---

## Models Tested

| Model | Architecture | Status |
|-------|--------------|--------|
| **DeepSeek-R1** 32B, 70B | Mixture of Experts | ✅ Valid |
| Qwen3 0.6B, 4B, 8B, 14B, 32B | Dense Transformer | ⚠️ Partial |
| Llama 3.2-1B, 3.2-3B | Dense (GQA) | ✅ Valid |
| Mistral 7B | Dense (SLA) | ✅ Valid |

**Note:** Some Qwen experiments had data integrity issues where different seeds produced identical outputs. Those results have been removed from this repository.

---

## Repository Structure

```
entropy-seeding/
├── README.md                           # This file
├── METRICS_GLOSSARY.md                 # Metric definitions
│
├── reports/
│   ├── PRNG_DETAILED_REPORT.md         # PRNG entropy source analysis
│   ├── TRNG_DETAILED_REPORT.md         # TRNG entropy source analysis
│   ├── QRNG_DETAILED_REPORT.md         # QRNG entropy source analysis
│   ├── FINGERPRINT_CLASSIFIER_REPORT.md # Fingerprint classification
│   └── NEBULA_ENTROPY_SOURCE_EXPLAINED.md # Nebula explainer
│
├── results/
│   ├── entropy_source_comparisons/     # PRNG/TRNG/QRNG comparisons
│   │   ├── deepseek_r1/                # DeepSeek-R1 32B/70B results
│   │   ├── prng_trng_qrng/             # Direct comparisons
│   │   └── documentation/              # Qualitative analysis
│   │
│   ├── valid_entropy_comparisons/      # Validated comparisons
│   │   ├── deepseek/                   # DeepSeek results
│   │   ├── qwen/                       # Qwen quantum activation results
│   │   └── llama/                      # Llama results
│   │
│   └── fingerprint/                    # Fingerprint classifier results
│
└── scripts/                            # Analysis and experiment scripts
```

---

## Metrics We Track

| Metric | What It Measures | What It Means |
|--------|------------------|---------------|
| **distinct_2** | Unique bigram proportion | Higher = more diverse word pairs |
| **TTR** | Type-Token Ratio | Higher = richer vocabulary |
| **Repetition** | Character-level repetition | Lower = less repetitive |
| **Shannon Entropy** | Text information density | Higher = more unpredictable |
| **Burstiness** | Sentence length variance | Lower = more natural flow |
| **Perplexity** | Model confidence | Lower = more confident |

---

## Usage Examples

### Using TRNG (Hardware Randomness)

```python
import struct

def get_trng_seed():
    """Generate seed from hardware entropy."""
    with open("/dev/urandom", "rb") as f:
        return struct.unpack("I", f.read(4))[0]

# Use in your model
seed = get_trng_seed()
```

### Using QRNG (Quantum Randomness)

See repository for cached QRNG implementation using IBM Quantum measurements.

---

## Limitations

1. **Sample Size:** Limited prompt set per configuration
2. **Hardware:** TRNG tested only on Apple M4 Pro
3. **QRNG Cache:** Quantum measurements pre-generated and cached
4. **Task Focus:** Primarily creative/analytical writing tasks
5. **Architecture Coverage:** Not all model families tested

---

## Future Directions

### Completed (Feb 2026)
- ✅ Llama 3.1-8B (GQA) and Mistral 7B (SLA) tested
- ✅ Expanded prompt diversity (15 single-turn + 3 multi-turn)
- ✅ Explored hybrid entropy sources (10 variants tested)

### Open Research Questions
1. **Nebula genre sweep** — Test all 22 literary texts as entropy sources on 8B+ models
2. **Nebula layer ablation** — Measure each layer's contribution to debiasing
3. **Token-level fingerprinting** — Token-ID sequences may carry stronger signal
4. **Power-up sample sizes** — Target n=300+ per source for significance
5. **Entropy-based style transfer** — Can literary entropy sources steer generation style?
6. **Entropy watermarking** — Use private texts as watermark keys
7. **SHA256 Paradox formalization** — Why does hash consumption preserve structural info?

---

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

---

## License

Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International

---

## Acknowledgments

Inspired by Jordan Thelen's video "How to Summon AI Demons with LLMs"

---

**GitHub:** https://github.com/robertcprice/entropy-seeding
**Last Updated:** February 2026
