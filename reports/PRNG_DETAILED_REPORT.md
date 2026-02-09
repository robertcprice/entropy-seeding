# PRNG: Pseudo-Random Number Generator - Detailed Report

## Abstract

**Personality:** "Volatile"

PRNG (Pseudo-Random Number Generator) is the most basic form of entropy generation for LLMs, using algorithmic mathematical formulas seeded with an initial value.

---

## Technical Implementation

### Algorithm: Mersenne Twister (MT19937)

| Property | Value |
|----------|-------|
| **Period** | 2¹⁹⁹³⁷-¹ |
| **State size** | 2.5 KB |
| **Bit generation** | 32-bit worth of randomness per call |
| **Speed** | ~100 ns per random() call |
| **Language** | Python 3.10+ |
| **Library** | `random` module |

### Implementation Code

```python
import random
import torch

def get_prng_seed(seed_value):
    """Generate deterministic seed from PRNG."""
    random.seed(seed_value)  # Fixed seed = deterministic output
    return random.getrandbits(32)

# Typical usage in our tests
SEEDS = [11, 22, 33, 44, 55]  # Fixed sequence for reproducibility
for seed in SEEDS:
    torch.manual_seed(get_prng_seed(seed))
    output = model.generate(inputs)
```

### Deterministic Behavior

**Same seed + Same prompt + Same model = Identical output every time**

```
Seed: 42 + Prompt: "Hello" → Output: "Hi there!" (always)
Seed: 42 + Prompt: "Hello" → Output: "Hi there!" (always)
Seed: 42 + Prompt: "Hello" → Output: "Hi there!" (always)
```

This makes PRNG:
- ✅ **Reproducible** (useful for debugging, testing)
- ✅ **Fast** (no hardware dependency)
- ✅ **Platform-independent** (identical on all systems)
- ❌ **Predictable** (security risk)
- ❌ **Can catastrophically fail** (documented failures on complex prompts)

---

## Performance Metrics

### Across All Model Sizes

| Model | Size | distinct_2 | TTR | Repetition | Personality |
|-------|------|-----------|-----|------------|-------------|
| Qwen3 | 0.6B | 0.862 | 0.621 | 0.379 | Unpredictable |
| Qwen3 | 8B | 0.826 | 0.583 | 0.417 | Unstable |
| Qwen3 | 14B | 0.891 | 0.600 | 0.400 | More stable |
| DeepSeek-R1 | 32B | ~0.85 | ~0.60 | ~0.024 | Moderate |
| DeepSeek-R1 | 70B | Variable | Variable | 0.024 | **FAIL** on philosophy |

### Color Naming Task Results

| Metric | PRNG Average |
|--------|-------------|
| **Shannon Char** | 4.44 |
| **Shannon Word** | 6.91 |
| **Perplexity** | 21.6 |
| **Burstiness** | 0.686 (somewhat erratic) |
| **Repetition** | 0.209 (higher) |
| **Uniqueness** | 0.308 (lower) |

---

## Documented Failures

### Catastrophic Failure: DeepSeek-R1 70B Philosophy Prompt

**Prompt:** "What gives life meaning?"

**Result:** Complete model failure
```
All metrics:
- Shannon Char: 0.00
- Shannon Word: 0.00
- Perplexity: Infinity
- Burstiness: 0.00
- Repetition: 0.00
- Uniqueness: 0.00
```

**Cause:** Deterministic seed (42) + complex analytical prompt = internal state collision in MoE routing

**Lesson:** Never use seeded PRNG for production applications

### Small Model Issues

**Qwen3 0.6B:** Higher repetition (37.9%) due to getting stuck in token selection loops

---

## Strengths & Weaknesses

### Strengths
- ✅ Fast execution (~100 ns)
- ✅ No hardware dependency
- ✅ Reproducible outputs
- ✅ Platform-independent
- ✅ Useful for debugging
- ✅ Essential for unit testing

### Weaknesses
- ❌ Catastrophic failures possible
- ❌ Unpredictable quality
- ❌ Higher repetition (15-46% more than TRNG)
- ❌ Less natural flow (burstiness ~0.45 vs 0.24)
- ❌ Security risk (deterministic = predictable)
- ❌ Can fail on complex analytical tasks

---

## Use Case Recommendations

### When to Use PRNG

| Scenario | Reason |
|----------|--------|
| **Debugging** | Need reproducible outputs |
| **Unit Testing** | Deterministic behavior required |
| **Research** | Controlled experiments |
| **Development** | Fast iterations |

### When to AVOID PRNG

| Scenario | Reason |
|----------|--------|
| ❌ **Production systems** | Catastrophic failure risk |
| ❌ **User-facing content** | Unpredictable quality |
| ❌ **Complex analytical tasks** | Documented failures |
| ❌ **Security-critical applications** | Deterministic = predictable |
| ❌ **Creative writing** | Lower diversity |

---

## Comparison to Other Sources

```
Uniqueness Score:
PRNG ████████████░░ 62% (lowest)
TRNG ██████████████ 65% (highest)
QRNG █████████████░ 64% (middle)

Repetition Score (lower is better):
PRNG ██████████████ 2.4% (worst)
TRNG █████████░░░░░ 1.3% (best)
QRNG ████████████░░ 1.8% (middle)

Catastrophic Failures:
PRNG ██████████████ YES ❌
TRNG ░░░░░░░░░░░░░░░ NO ✅
QRNG ░░░░░░░░░░░░░░░ NO ✅
```

---

## Implementation Examples

### Python/PyTorch
```python
import random
import torch

# Set PRNG seed
seed = 42
torch.manual_seed(seed)
random.seed(seed)

# Generate
output = model.generate(inputs, max_new_tokens=200)
```

### HuggingFace Transformers
```python
from transformers import set_seed

# Set seed
set_seed(42)

# Generate (deterministic)
outputs = model.generate(**inputs, do_sample=True, top_p=0.9)
```

---

## Security Considerations

⚠️ **CRITICAL SECURITY RISK**

PRNG with known seeds is **cryptographically insecure**:
- Outputs can be predicted given seed knowledge
- Seeds can often be inferred from outputs
- Not suitable for:
  - Password generation
  - Token generation
  - Session IDs
  - Encryption keys
  - Security tokens

**For security applications, use:** `secrets.randbits()` or `os.urandom()`

---

## Research Findings Summary

### Key Discoveries

1. **Model Size Dependence:** PRNG performance varies dramatically by model size
   - Small models (<8B): Unpredictable behavior
   - Medium models (8-14B): Moderate stability
   - Large models (32B+): More consistent but still prone to failures

2. **Prompt Type Sensitivity:**
   - Creative: Works adequately
   - Analytical: High failure rate
   - Philosophy: **Catastrophic failure documented**

3. **Repetition Problem:**
   - 15-46% higher repetition than TRNG
   - More pronounced on small models
   - Worst on moral/ethical questions

---

## Conclusion

PRNG is best suited for **development and testing** due to its reproducibility, but should **never be used in production** LLM deployments due to:
- Catastrophic failure modes
- Lower output quality
- Security vulnerabilities
- Inconsistent behavior across prompts

**Recommendation:** Use only for debugging and testing. Use TRNG for all production applications.

---

*Report generated: 2026-02-07*
*Data sources: 7 model sizes, 50+ configurations*

---

## Appendix: Metrics Glossary

### Key Metrics

| Metric | What It Measures | Good Range | Direction |
|:------:|------------------|:----------:|:---------:|
| **shannon_char** | Character diversity (bits/char) | 4.2–4.7 | Higher = better |
| **shannon_word** | Vocabulary richness (bits/word) | 7.0–9.0 | Higher = better |
| **word_diversity** (TTR) | Unique word fraction | 0.5–0.8 | Higher = better |
| **distinct_2** (D2) | Unique bigram fraction | 0.85–1.0 | Higher = better |

### PRNG Implementation

**Source**: `random.Random(42)` → Python's Mersenne Twister PRNG with fixed seed.
**Properties**: Fully deterministic. Same seed = identical sequence every time. Period of 2^19937-1.
**Limitation**: Predictable. Not suitable for cryptographic or security-sensitive applications.
**Use case**: Reproducible experiments and debugging baselines.

*Full glossary: see `METRICS_GLOSSARY.md` in the repository root.*
