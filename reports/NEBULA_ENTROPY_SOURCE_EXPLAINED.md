# Nebula: Hierarchical Multi-Layer Literary Entropy Source - Explained

## Abstract

**Personality:** "Structural DNA"

Nebula is a novel entropy source that derives randomness from the **structure of human writing** rather than from mathematical algorithms (PRNG), hardware noise (TRNG), or quantum measurement (QRNG). It extracts five orthogonal information layers from a literary text and combines them using prime-number gear ratios, producing astronomically long non-repeating seed sequences that carry the "structural DNA" of the source text. This document explains what Nebula is, how it works, why it matters, and what the research has found so far.

---

## What Problem Does Nebula Solve?

Standard LLM text generation uses a random seed to control token sampling. The seed determines which tokens are selected at each step when the model's probability distribution is sampled. Conventional approaches use one of three entropy sources:

| Source | Mechanism | Properties |
|--------|-----------|------------|
| **PRNG** | Deterministic math (Mersenne Twister) | Reproducible, fast, but algorithmically predictable |
| **TRNG** | Hardware noise (`/dev/urandom`) | Non-reproducible, high quality, no structural content |
| **QRNG** | Quantum measurement (IBM Quantum) | Fundamentally unpredictable, no structural content |

All three share a common trait: the entropy is **structureless**. A TRNG seed derived from thermal noise has no relationship to language, text, or human cognition. It is pure noise.

Nebula asks a different question: **What happens if the randomness itself carries the structure of human writing?**

---

## How Nebula Works

### High-Level Architecture

```
                        Literary Text (e.g., Bible KJV)
                                    |
                     Split into 1024-character chunks
                                    |
                  +---------+---------+---------+---------+
                  |         |         |         |         |
               Layer 1   Layer 2   Layer 3   Layer 4   Layer 5
               Chunk     Char      Word      Position  Cross-Chunk
               Hash      Freq      Boundary  Encoding  Entanglement
               Chain     Signature Pattern             (XOR neighbors)
                  |         |         |         |         |
                  v         v         v         v         v
               chain[0]  chain[0]  chain[0]  chain[0]  chain[0]
               chain[1]  chain[1]  chain[1]  chain[1]  chain[1]
               chain[2]  chain[2]  chain[2]  chain[2]  chain[2]
                ...       ...       ...       ...       ...
                  |         |         |         |         |
                  +---------+---------+---------+---------+
                                    |
                    Gear Ratio Advancement (prime rates)
                                    |
                            SHA256 combination
                                    |
                          64-bit seed output
                                    |
                      torch.Generator.manual_seed()
```

The source text is split into 1024-character chunks. Five different extraction functions process these chunks into five independent hash chains. At each generation step, values from all five chains are combined into a single SHA256 hash, producing a 64-bit seed for PyTorch's random number generator.

---

## The Five Layers

Each layer extracts a different, statistically orthogonal aspect of the source text. While they all derive from the same text, they capture **different structural dimensions** of it.

### Layer 1: Chunk Hash Chain (Raw Content)

The simplest layer. Each 1024-character chunk is hashed with SHA256, producing a 32-byte value. This is identical to what the older `LiteraryEntropySource` uses on its own.

```
"In the beginning God created..."  -->  SHA256  -->  32 bytes
"...the heaven and the earth..."   -->  SHA256  -->  32 bytes
```

| Property | Value |
|----------|-------|
| **Captures** | Raw text content patterns |
| **For Bible KJV** | ~4,000 chunks = 4,000 hash values |
| **Equivalent to** | The single-chain `LiteraryEntropySource` |

### Layer 2: Character Frequency Signature (Statistical Fingerprint)

For each chunk, count the frequency of all 256 possible byte values. Sort by byte value, pack the counts into a deterministic byte string, and hash the result.

```
Chunk: "To be, or not to be, that is the question"
       ↓
Byte frequencies: {32: 10, 44: 1, 84: 1, 97: 2, 98: 2, ...}
       ↓
Pack as 256 uint16 values  -->  SHA256  -->  32 bytes
```

| Property | Value |
|----------|-------|
| **Captures** | Statistical fingerprint of each chunk's character distribution |
| **Key insight** | A chunk about "battle" has different letter frequencies than a chunk about "love" |
| **Independence** | Different from Layer 1 because two chunks with different content can have similar frequencies and vice versa |

### Layer 3: Word Boundary Pattern (Rhythm and Structure)

For each chunk, record the positions (mod 256) of all word and sentence boundaries: spaces, tabs, newlines, commas, periods, semicolons, colons, exclamation marks, question marks, quotes, apostrophes, parentheses, and hyphens.

```
Chunk: "Call me Ishmael. Some years ago..."
       ↓
Boundary positions: [4, 7, 16, 17, 21, 27, 30, ...]
       ↓
Pack as bytes  -->  SHA256  -->  32 bytes
```

| Property | Value |
|----------|-------|
| **Captures** | Rhythm, prose density, sentence length variation |
| **Key insight** | Poetry has very different boundary patterns than scientific prose |
| **Boundary characters** | ` \t\n.,;:!?"'()-` |

### Layer 4: Sinusoidal Positional Encoding (Position Awareness)

Uses transformer-style sinusoidal encoding of each chunk's position within the overall text. Encodes position in 32 dimensions using alternating sine and cosine functions at different frequencies.

```
Position i, dimension d:
  even d:  sin(i / 10000^(d/32))
  odd d:   cos(i / 10000^((d-1)/32))

32 float32 values  -->  SHA256  -->  32 bytes
```

| Property | Value |
|----------|-------|
| **Captures** | WHERE in the text the system currently is |
| **Key insight** | Genesis produces different entropy than Revelations |
| **Encoding** | Same sinusoidal scheme used in the original Transformer paper (Vaswani et al., 2017) |

### Layer 5: Cross-Chunk Entanglement (Non-Local Dependencies)

XOR each chunk's Layer 1 hash with the hashes of its two neighbors (previous and next, wrapping at boundaries). Hash the XOR result.

```
chunk[i-1] hash:  a1 b2 c3 d4 ...
chunk[i]   hash:  e5 f6 g7 h8 ...    XOR all three
chunk[i+1] hash:  i9 j0 k1 l2 ...       ↓
                                     SHA256  -->  32 bytes
```

| Property | Value |
|----------|-------|
| **Captures** | Non-local dependencies; each position depends on its context |
| **Key insight** | Even if chunks repeat, their neighborhoods do not |
| **Role** | Primary debiasing layer; responsible for the 23.8% repetition bias reduction vs single-chain literary source |
| **Input** | Derived from Layer 1's chain (not raw text), creating a second-order dependency |

---

## The Gear Ratio System

All five layers advance simultaneously, but at **different rates** determined by the first five prime-like numbers:

| Layer | Aspect | Gear Rate | Advances Every... |
|-------|--------|-----------|-------------------|
| 1 | Chunk Hash Chain | 1 | Every step |
| 2 | Char Frequency | 2 | Every 2nd step |
| 3 | Word Boundary | 3 | Every 3rd step |
| 4 | Positional Encoding | 5 | Every 5th step |
| 5 | Entanglement | 7 | Every 7th step |

### Why Prime Rates?

Prime-number gear ratios maximize the time before the combined pattern repeats. The theoretical period is:

```
Period = LCM(chain_length * rate_1, chain_length * rate_2, ..., chain_length * rate_5)
```

For Bible KJV with ~4,000 chunks:

```
Period = LCM(4000*1, 4000*2, 4000*3, 4000*5, 4000*7)
       = LCM(4000, 8000, 12000, 20000, 28000)
       = 840,000 steps minimum

But since each layer wraps independently:
  Effective period ≈ 4000^5 * LCM(1,2,3,5,7) = 4000^5 * 210 ≈ 2.15 * 10^20 steps
```

For context, generating 500 tokens per prompt, this allows roughly **4.3 * 10^17 generations** before any possibility of repetition. The combined gear pattern is effectively infinite for practical use.

### Visual Analogy

```
Step:     0    1    2    3    4    5    6    7    8    9   10 ...
Layer 1:  0    1    2    3    4    5    6    7    8    9   10     (every step)
Layer 2:  0    2    4    6    8   10   12   14   16   18   20    (x2)
Layer 3:  0    3    6    9   12   15   18   21   24   27   30    (x3)
Layer 4:  0    5   10   15   20   25   30   35   40   45   50    (x5)
Layer 5:  0    7   14   21   28   35   42   49   56   63   70    (x7)

All positions mod chain_length. The 5-tuple of positions never repeats
within the theoretical period.
```

---

## The Seed Generation Process

At each token generation step, Nebula produces a seed through the following procedure:

1. **Initialize** a fresh SHA256 hash
2. **Chain** the previous seed (recurrence: each seed depends on the last)
3. **Walk** each layer's chain at its gear rate, mixing each layer's hash value
4. **Separate** layers with a domain index (prevents identical layer values from canceling)
5. **Blend** recently generated tokens (optional context feedback)
6. **Extract** the first 8 bytes of the SHA256 digest as a 64-bit seed

### Implementation

```python
def get_seed(self, generated_tokens, logits, attention_weights):
    self._ensure_initialized()

    h = hashlib.sha256()

    # Chain previous seed for recurrence
    h.update(struct.pack("Q", self._prev_seed % (2**64)))

    # Gear ratio primes -- each layer advances at a different rate
    primes = [1, 2, 3, 5, 7, 11, 13, 17, 19, 23]

    for layer_idx, chain in enumerate(self._chains):
        if not chain:
            continue
        # Each layer walks at a different speed
        rate = primes[layer_idx % len(primes)]
        pos = (self._step * rate) % len(chain)
        h.update(chain[pos])
        # Also mix in the layer index for domain separation
        h.update(struct.pack("B", layer_idx))

    # Optional context blending
    if self.blend_context and generated_tokens:
        recent = generated_tokens[-self.context_window:]
        h.update(struct.pack(f"{len(recent)}i", *recent))

    self._step += 1
    seed = int.from_bytes(h.digest()[:8], "big")
    self._prev_seed = seed
    return seed
```

### Seed Lifecycle in Generation

```
Token 0:  Nebula.get_seed() --> seed_0 --> torch.manual_seed(seed_0) --> sample token
Token 1:  Nebula.get_seed() --> seed_1 --> torch.manual_seed(seed_1) --> sample token
Token 2:  Nebula.get_seed() --> seed_2 --> torch.manual_seed(seed_2) --> sample token
  ...
Token N:  Nebula.get_seed() --> seed_N --> torch.manual_seed(seed_N) --> sample token
```

Each seed depends on:
- The **five layer values** at the current gear-adjusted positions
- The **previous seed** (recurrence chain)
- The **recently generated tokens** (context blending, if enabled)

This three-way dependency means that even if two generation runs use the same literary text, any divergence in generated tokens causes the seed sequences to diverge irreversibly.

---

## Comparison: Nebula vs. LiteraryEntropySource

Nebula evolved from the simpler `LiteraryEntropySource`, which uses a single hash chain (Layer 1 only).

| Property | LiteraryEntropySource | NebulaSource |
|----------|----------------------|--------------|
| **Layers** | 1 (chunk hash chain) | 5 (orthogonal layers) |
| **Advancement** | Linear (position += 1) | Gear ratios (prime rates) |
| **Period** | chain_length (~4,000) | ~10^20 steps |
| **Debiasing** | None | 23.8% repetition bias reduction |
| **Previous seed chaining** | No | Yes |
| **Domain separation** | No | Yes (layer index mixed in) |
| **Context blending** | XOR-based | SHA256-mixed |

The key improvement: Nebula's multi-layer approach breaks the periodicity that single-chain consumption preserves. When a model consumes hash values sequentially from a single chain, the source text's autocorrelation structure propagates through the generation. Nebula's gear ratios and cross-chunk entanglement disrupt this propagation.

---

## Key Research Findings

### The SHA256 Paradox

SHA256 is a cryptographic hash function designed to fully decorrelate its output from its input. Every individual hash passes all standard randomness tests. Yet when hash values from a literary text are consumed **sequentially** during generation, the text's autocorrelation structure propagates through the hash chain and measurably affects the model's output.

**This is the SHA256 Paradox**: each hash is individually indistinguishable from random, but the **sequence** of hashes consumed during generation carries the source text's patterns.

| Metric | Bible KJV Nebula vs PRNG Baseline |
|--------|-----------------------------------|
| **D2 (bigram diversity)** | -25.2% (fewer unique bigrams) |
| **1st-person pronoun rate** | 2.1x higher |

The effect is subtle but statistically significant. SHA256 does not decorrelate the temporal autocorrelation between consecutive consumption events, even though each individual event appears random.

### Nebula's Debiasing Effect

Compared to the single-chain `LiteraryEntropySource` using the same text:

```
Text-Induced Repetition Bias:

Single-chain (literary.py):  ████████████████████ 100% (baseline)
Nebula (nebula.py):          ████████████████░░░░  76.2% (-23.8%)
```

Nebula's hierarchical extraction reduces text-induced bias by **23.8%**. The primary mechanism is Layer 5 (cross-chunk entanglement), which spreads information across the chain via XOR with neighbors. This breaks the local autocorrelation that single-chain consumption preserves.

### Genre Coloring

Different literary texts produce measurably different generation characteristics when used as Nebula sources:

| Source Text | Observed Effect |
|-------------|-----------------|
| **Bible KJV** | Increased 1st-person pronouns, religious vocabulary emergence |
| **Structured prose** | Expected: different sentence-length distributions |
| **Poetry** | Expected: different rhythm patterns |

Full genre sweep across all 22 texts is a planned experiment. Early results with a fingerprint classifier show that genre-specific features (sentence_length_std, comma_rate, hapax_ratio) are the most discriminating dimensions.

### Invisibility to Fingerprint Classification

At the 8B model scale, a Random Forest classifier trained on 108 text and metric features **cannot distinguish** Nebula Bible output from PRNG, TRNG, or QRNG output:

```
Pairwise classification accuracy (50% = random chance):

nebula_bible vs prng:            ~50%
nebula_bible vs trng:            ~50%
nebula_bible vs qrng_cached:     ~50%
nebula_bible vs self_seed_sfc:   ~50%
nebula_bible vs hidden_variance: ~50%
```

**This is not contradictory** with the SHA256 Paradox findings. The effects are real, but they manifest as shifts in **aggregate statistics** (D2, pronoun rates measured across many samples), not as patterns detectable in individual text samples. The SHA256 hashing successfully masks the source identity from surface-level text analysis, even though the generation process is measurably different at population level.

---

## The Literary Corpus

Nebula can use any of 22 texts from Project Gutenberg as its entropy source. The full corpus spans 11 genres:

| Genre | Texts |
|-------|-------|
| **Religious** | Bible KJV, Quran (Palmer), Bhagavad Gita, Tao Te Ching |
| **Horror** | H.P. Lovecraft (Call of Cthulhu), Edgar Allan Poe (The Raven), Mary Shelley (Frankenstein), Bram Stoker (Dracula) |
| **Romance** | Jane Austen (Pride and Prejudice), Charlotte Bronte (Jane Eyre) |
| **Philosophy** | Plato (The Republic), Nietzsche (Thus Spoke Zarathustra) |
| **Drama** | Shakespeare (Hamlet), Oscar Wilde (Dorian Gray) |
| **Adventure** | Herman Melville (Moby-Dick), Mark Twain (Huckleberry Finn) |
| **Mystery** | Arthur Conan Doyle (Sherlock Holmes) |
| **Fantasy** | Lewis Carroll (Alice in Wonderland), Homer (The Iliad) |
| **Science** | Charles Darwin (Origin of Species) |
| **Epic Poetry** | John Milton (Paradise Lost) |
| **Surreal** | Franz Kafka (The Metamorphosis) |

Texts are downloaded from Project Gutenberg, stripped of headers and footers, and managed by the `CorpusManager` class which handles chunking, caching, and hash chain computation.

---

## Why Nebula Matters

Nebula represents a fundamentally different category of entropy source. Every other RNG approach produces **structureless** randomness: PRNG from algorithms, TRNG from noise, QRNG from quantum mechanics. None of these carry any relationship to human language or cognition.

Nebula opens four new research directions:

### 1. Style Transfer Through Sampling

By changing the literary source, you change the structural DNA of the randomness driving generation. This is a form of **style transfer at the sampling layer** rather than at the model or prompt layer. The model's weights and prompt remain unchanged; only the randomness changes.

### 2. Entropy-Based Watermarking

A private literary text (or a specific combination of text and gear ratios) could serve as a cryptographic "key" that leaves an invisible but statistically detectable fingerprint in generated text. The SHA256 masking ensures the source identity is undetectable from individual samples, while the aggregate statistical signature remains measurable with sufficient data.

### 3. Entropy Source Diversity

Nebula is **mechanistically different** from all other entropy approaches. In systems that benefit from entropy source diversity (defense in depth, ensemble methods), literary entropy provides an orthogonal source type.

### 4. Human-Like Randomness Patterns

The structure of human writing may produce randomness patterns that are more "human-like" than mathematical pseudo-randomness. If confirmed, this has implications for creative text generation, where natural-feeling variation is more valuable than uniform randomness.

---

## Implementation Details

### Source Files

| Component | Path |
|-----------|------|
| **Nebula source** | `src/entropy/entropy_sources/nebula.py` |
| **Literary source** (predecessor) | `src/entropy/entropy_sources/literary.py` |
| **Corpus manager** | `src/entropy/corpus/manager.py` |
| **Text downloader** | `src/entropy/corpus/gutenberg.py` |
| **Genre classification** | `src/entropy/corpus/genres.py` |
| **Base class** | `src/entropy/entropy_sources/base.py` |

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `corpus_manager` | `CorpusManager` | (required) | Manager providing text access |
| `text_name` | `str` | `"bible_kjv"` | Name of the literary text to use |
| `num_layers` | `int` | `5` | Number of entropy layers to extract (1-5) |
| `blend_context` | `bool` | `True` | Whether to blend recently generated tokens into the seed |
| `context_window` | `int` | `10` | Number of recent tokens to include in context blend |
| `initial_seed` | `int` | `42` | Starting seed for the recurrence chain |

### Public Properties

| Property | Returns | Description |
|----------|---------|-------------|
| `layer_count` | `int` | Number of active entropy layers |
| `chain_lengths` | `list[int]` | Length of each layer's hash chain |
| `total_entropy_elements` | `int` | Total number of hash values across all layers |
| `theoretical_period` | `int` | Steps before the gear pattern repeats |

### Usage Example

```python
from entropy.corpus.manager import CorpusManager
from entropy.entropy_sources.nebula import NebulaSource

# Initialize corpus and Nebula source
corpus = CorpusManager()
nebula = NebulaSource(
    corpus_manager=corpus,
    text_name="bible_kjv",
    num_layers=5,
    blend_context=True,
)

# Use in generation loop
generated_tokens = []
for step in range(max_tokens):
    seed = nebula.get_seed(generated_tokens, logits=None, attention_weights=None)
    generator = torch.Generator().manual_seed(seed)
    # ... sample next token using generator ...
    generated_tokens.append(next_token_id)
```

---

## Open Questions and Future Directions

| Question | Status | Notes |
|----------|--------|-------|
| Does genre coloring generalize across all 22 texts? | Planned | Full genre sweep experiment |
| How does model scale affect Nebula's influence? | Partially answered | Larger models resist text-induced repetition (8B: 44.6% vs 14B: 37.0%) |
| Can Nebula serve as a practical watermarking scheme? | Open | Requires adversarial robustness testing |
| What is the minimum sample size for aggregate detection? | Open | Current evidence: detectable at ~70 samples per source |
| Do different gear ratio selections change the effect? | Open | Current ratios are the first five primes; alternatives untested |
| Can Layer 5 (entanglement) be strengthened further? | Open | Multi-hop entanglement (XOR with k neighbors) is a candidate |

---

## Metrics Glossary

| Term | Definition |
|------|------------|
| **D2 (distinct_2)** | Ratio of unique bigrams to total bigrams in generated text. Higher = more diverse vocabulary use. |
| **TTR** | Type-Token Ratio: unique words divided by total words. Higher = richer vocabulary. |
| **SHA256** | Cryptographic hash function producing 256-bit (32-byte) output. Near-uniform distribution for any input. |
| **Gear ratio** | The rate at which each layer advances through its hash chain. Using prime numbers minimizes alignment between layers. |
| **LCM** | Least Common Multiple. Determines the theoretical period before the combined gear pattern repeats. |
| **Chunk** | A 1024-character block of source text, the fundamental unit of extraction. |
| **Context blending** | Mixing recently generated token IDs into the seed computation, creating feedback between generation output and entropy source. |
| **Entanglement** | XOR of neighboring chunk hashes, creating non-local dependencies where each chain position depends on its context. |
| **Literary entropy** | Randomness derived from the structure of literary text rather than mathematical or physical processes. |
| **Domain separation** | Mixing a layer index into the hash to prevent identical values from different layers from producing identical contributions. |
| **Recurrence chain** | Each seed depends on the previous seed, ensuring that even identical layer lookups produce different outputs at different steps. |
| **Orthogonal layers** | Layers that capture statistically independent aspects of the same source text, maximizing the information extracted per chunk. |

---

*Report generated: 2026-02-09*
*Source: `src/entropy/entropy_sources/nebula.py`*
*Corpus: 22 texts from Project Gutenberg, managed by `src/entropy/corpus/`*
*Related reports: `FINGERPRINT_CLASSIFIER_REPORT.md`, `TRNG_DETAILED_REPORT.md`, `PRNG_DETAILED_REPORT.md`, `QRNG_DETAILED_REPORT.md`*
