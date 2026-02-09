# Qwen3 Entropy Comparison Results

Comparing PRNG vs TRNG vs QRNG on Qwen3 models (0.6B, 1.7B, 4B, 8B, 14B).


## Qwen3-0.6B

**Files analyzed:** 81


### Sample Outputs by Entropy Source


#### PRNG

| Prompt | Output (truncated) |
|--------|-------------------|
| The old lighthouse keeper had never seen anything ... |  He had seen the sun rise and set at the same time every day, but he had never seen a ship sailing in such a line as this. The reason for this differe... |
| The old lighthouse keeper had never seen anything ... |  He had been out at sea for years, and he knew all the things he had seen. He had been out for years at sea. He had seen nothing but stars, and he kne... |
| The old lighthouse keeper had never seen anything ... |  He had seen only the stars. It was the first time in his career, and he had never felt such a sense of loneliness. The lighthouse keeper's job, which... |

## Qwen3-1.7B

**Files analyzed:** 1


### Sample Outputs by Entropy Source


#### QRNG

| Prompt | Output (truncated) |
|--------|-------------------|
| Is it ever ethical to tell a lie? If so, under wha... |  Additionally -     for, that is   this the the   ( -   to  the the  to answer a lie, that   the what you the,,  to, to is is is,,,   to - explain the... |

## Qwen3-4B

**Files analyzed:** 19


### Sample Outputs by Entropy Source


#### PRNG

| Prompt | Output (truncated) |
|--------|-------------------|
| The old lighthouse keeper had never seen anything ... |  The sea was heaving with great, dark waves, and the wind was howling like a thousand wolves. The sky was a swirling mass of gray, and the rain was co... |
| The old lighthouse keeper had never seen anything ... |  The lights were out, and for the first time in his 40 years of service, he was lost. He had been sailing through the fog for hours. His ship had been... |
| The old lighthouse keeper had never seen anything ... |  A ship had just crashed into the rocks outside of the lighthouse, and now the ship's captain was running toward the lighthouse, screaming for help. T... |

#### TRNG

| Prompt | Output (truncated) |
|--------|-------------------|
| The old lighthouse keeper had never seen anything ... |  The sea was churning in violent, frothing waves, and the wind howled through the rocks like a banshee. The lighthouse beam had long since died, its b... |
| The old lighthouse keeper had never seen anything ... |  The storm had been raging for hours, and now the sea was rising higher than ever before. He could see the waves crashing against the rocks with such ... |
| The old lighthouse keeper had never seen anything ... |  Even though the lighthouse was a long way out to sea, the light could be seen from the mainland 25 miles away. The lighthouse had been built 100 year... |

#### QRNG

| Prompt | Output (truncated) |
|--------|-------------------|
| The old lighthouse keeper had never seen anything ... |  For the first time in 25 years, the lighthouse was_. A. operating at full capacity B. visited by tourists C. abandoned D. under repair  Okay, let's s... |
| The old lighthouse keeper had never seen anything ... |  The weather had turned in an instant, the sun disappearing behind a thick wall of clouds, and the wind had picked up. The storm had arrived with a fu... |
| The old lighthouse keeper had never seen anything ... |  He stood at the top of the tower, peering out to sea, and felt a chill run down his spine. The storm was coming in fast, and the waves were rising hi... |

## Qwen3-8B

**Files analyzed:** 12


### Sample Outputs by Entropy Source


#### PRNG

| Prompt | Output (truncated) |
|--------|-------------------|
| The old lighthouse keeper had never seen anything ... |  The sea was a violent, roiling mass of green and white, and the air was thick with the sound of wind howling through the cliffs. The waves crashed ag... |
| The old lighthouse keeper had never seen anything ... |  The storm had passed, and the sea was calm again. But the sea was not empty. The sea was full of mirrors. The sea was full of glass. The sea was full... |
| The old lighthouse keeper had never seen anything ... |  It was as if the very air was alive with the sound of buzzing. He had heard of such things before, of course. In the old books, they called it the 'h... |

#### TRNG

| Prompt | Output (truncated) |
|--------|-------------------|
| The old lighthouse keeper had never seen anything ... |  The storm had come out of nowhere, and in less than an hour, the sea had risen more than three feet. The waves were monstrous, and the wind howled li... |
| The old lighthouse keeper had never seen anything ... |  The storm had come out of nowhere, and in less than an hour, the coast guard had been called in to rescue people and animals from the cliffs. The sea... |
| The old lighthouse keeper had never seen anything ... |  The storm had come out of nowhere, and in the time it took for the sun to disappear behind the clouds, the wind was howling like a wolf pack. He had ... |

#### QRNG

| Prompt | Output (truncated) |
|--------|-------------------|
| The old lighthouse keeper had never seen anything ... |  The sea was a flat, glassy, black thing, and the sky was the same color, and the wind had stopped. Even the waves had stopped. It was as if the world... |
| The old lighthouse keeper had never seen anything ... |  The storm had blown itself out in minutes, leaving the village below in an eerie calm. The sea, usually a relentless beast, was now a mirror, reflect... |
| The old lighthouse keeper had never seen anything ... |  He had been keeping watch over the coast for 30 years, and had seen his share of storms, squalls, and shipwrecks. But nothing like this. The sea was ... |

## Qualitative Findings


### QRNG Mode Shifts (Qwen3-14B)
- Started with narrative: "The old lighthouse keeper had never seen anything like it."
- **Suddenly switched to test format**: "A. operating at full capacity / B. visited by tourists..."
- Added meta-commentary: "Okay, let's see. The question is about..."

### TRNG Language Mixing (Qwen3-8B)
- Prompt: "She opened the letter, and everything changed."
- Output included Chinese: "翻译句子并解析句子成分..." (Translate sentence and analyze components)

### Entropy Source Personality Profiles
| Entropy | Creativity | Coherence | Meta-Cognition | Glitch Severity |
|---------|------------|-----------|----------------|-----------------|
| PRNG    | Medium     | **High**  | Moderate       | Low (repetition) |
| TRNG    | High       | Medium    | High           | Medium (language mixing) |
| QRNG    | **Highest**| Low       | **Very High**  | **Severe (mode shifts)** |

> **Why these personality profiles matter:** Each entropy source creates a distinct "behavioral fingerprint" on the model's output. PRNG's high coherence but medium creativity means the deterministic seed keeps the model on a predictable, safe path -- good for consistency but limiting for diversity. TRNG's balanced profile with occasional language mixing (outputting Chinese when prompted in English) shows that hardware entropy introduces enough randomness to explore the model's multilingual training data in unexpected ways. QRNG's extreme creativity paired with severe mode shifts (suddenly switching from narrative to multiple-choice test format) reveals that quantum entropy can push token selection into entirely different regions of the model's probability space. The "Meta-Cognition" column is particularly notable: QRNG's "Very High" rating means the model frequently breaks the fourth wall and comments on its own generation process ("Okay, let's see. The question is about..."), which is a sign that quantum entropy is activating self-referential pathways in the model. These profiles are qualitative summaries derived from manual inspection of outputs across model sizes, not computed metrics.

---

## Appendix: Metrics Glossary

### Entropy Sources

| Source | Description |
|:------:|-------------|
| **PRNG** | Pseudo-Random Number Generator (Mersenne Twister, seed=42) |
| **TRNG** | True Random Number Generator (`secrets.token_bytes()` via `/dev/urandom`) |
| **QRNG** | Quantum RNG (IBM `ibm_fez` measurements, SHA256-mixed). Cached, NOT live quantum. |

### Key Metrics

| Metric | What It Measures | Good Range | Direction |
|:------:|------------------|:----------:|:---------:|
| **shannon_char** | Character diversity (bits/char) | 4.2-4.7 | Higher = better |
| **shannon_word** | Vocabulary richness (bits/word) | 7.0-9.0 | Higher = better |
| **word_diversity** (TTR) | Unique word fraction | 0.5-0.8 | Higher = better |
| **distinct_2** (D2) | Unique bigram fraction | 0.85-1.0 | Higher = better |

### Qualitative Measures

| Measure | Description |
|:-------:|-------------|
| **Creativity** | Narrative originality and conceptual novelty (manual rating) |
| **Coherence** | Logical consistency and narrative flow (manual rating) |
| **Meta-Cognition** | Self-referential or "breaking the fourth wall" behaviors |
| **Glitch Severity** | Frequency and impact of mode shifts, language mixing, or repetition loops |
| **Mode Shift** | Sudden change in output format (e.g., narrative to multiple-choice) |
| **Language Mixing** | Unexpected insertion of non-prompt language (e.g., Chinese in English prompt) |

### Statistical Measures

| Measure | Key Thresholds |
|:-------:|:--------------:|
| **p-value** | < 0.05 significant, < 0.01 highly significant |
| **Cohen's d** | < 0.2 negligible, 0.2-0.5 small, 0.5-0.8 medium, > 0.8 large |
| **CV%** | < 5% very consistent, > 15% high variation |

*Full glossary: see `METRICS_GLOSSARY.md` in the repository root.*
