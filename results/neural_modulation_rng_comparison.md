================================================================================
RNG COMPARISON EXPERIMENT ANALYSIS
================================================================================

## SUMMARY OF CONFIGURATIONS
--------------------------------------------------------------------------------
Model    Temp       RNG        Avg Len    Entropy    Diversity 
--------------------------------------------------------------------------------
14b      neural     prng       105.2      4.20       0.629     
14b      neural     qrng_int   103.0      4.18       0.583     
14b      neural     trng       89.7       4.51       0.701     
14b      standard   prng       107.0      4.17       0.678     
14b      standard   qrng_int   94.2       4.39       0.692     
14b      standard   trng       108.8      4.16       0.596     
8b       neural     prng       109.3      4.12       0.529     
8b       neural     qrng_int   107.5      4.15       0.625     
8b       neural     trng       94.7       4.39       0.732     
8b       standard   prng       108.8      4.10       0.540     
8b       standard   qrng_int   96.0       4.35       0.614     
8b       standard   trng       109.3      4.15       0.590     


## RNG SEED COMPARISON (Aggregated)
--------------------------------------------------------------------------------

### Average Token Count

PRNG vs TRNG:
  PRNG: 107.583 ± 1.644
  TRNG: 100.625 ± 8.643
  p-value: 0.6612 ns

PRNG vs QRNG_INT:
  PRNG: 107.583 ± 1.644
  QRNG: 100.167 ± 5.366
  p-value: 0.1143 ns

TRNG vs QRNG_INT:
  TRNG: 100.625 ± 8.643
  QRNG: 100.167 ± 5.366
  p-value: 0.8857 ns

### Text Entropy (bits)

PRNG vs TRNG:
  PRNG: 4.148 ± 0.041
  TRNG: 4.301 ± 0.153
  p-value: 0.3429 ns

PRNG vs QRNG_INT:
  PRNG: 4.148 ± 0.041
  QRNG: 4.268 ± 0.102
  p-value: 0.2000 ns

TRNG vs QRNG_INT:
  TRNG: 4.301 ± 0.153
  QRNG: 4.268 ± 0.102
  p-value: 0.6857 ns

### Lexical Diversity

PRNG vs TRNG:
  PRNG: 0.594 ± 0.062
  TRNG: 0.655 ± 0.062
  p-value: 0.3429 ns

PRNG vs QRNG_INT:
  PRNG: 0.594 ± 0.062
  QRNG: 0.629 ± 0.040
  p-value: 0.6857 ns

TRNG vs QRNG_INT:
  TRNG: 0.655 ± 0.062
  QRNG: 0.629 ± 0.040
  p-value: 0.6857 ns

### Unique 5-grams

PRNG vs TRNG:
  PRNG: 584.500 ± 27.391
  TRNG: 566.250 ± 45.686
  p-value: 0.6857 ns

PRNG vs QRNG_INT:
  PRNG: 584.500 ± 27.391
  QRNG: 556.250 ± 37.765
  p-value: 0.3429 ns

TRNG vs QRNG_INT:
  TRNG: 566.250 ± 45.686
  QRNG: 556.250 ± 37.765
  p-value: 0.8857 ns


## MODEL-SPECIFIC ANALYSIS
================================================================================

### Qwen 8B
--------------------------------------------------------------------------------

Average Token Count:
  PRNG: 109.083 ± 0.250
  TRNG: 102.000 ± 7.333
  QRNG: 101.750 ± 5.750

Text Entropy:
  PRNG: 4.109 ± 0.008
  TRNG: 4.272 ± 0.120
  QRNG: 4.251 ± 0.100

Lexical Diversity:
  PRNG: 0.535 ± 0.005
  TRNG: 0.661 ± 0.071
  QRNG: 0.619 ± 0.006

### Qwen 14B
--------------------------------------------------------------------------------

Average Token Count:
  PRNG: 106.083 ± 0.917
  TRNG: 99.250 ± 9.583
  QRNG: 98.583 ± 4.417

Text Entropy:
  PRNG: 4.187 ± 0.017
  TRNG: 4.330 ± 0.175
  QRNG: 4.284 ± 0.101

Lexical Diversity:
  PRNG: 0.654 ± 0.024
  TRNG: 0.648 ± 0.052
  QRNG: 0.638 ± 0.055


## TEMPERATURE MODE COMPARISON
================================================================================

### Qwen 8B
Average Token Count:
  Standard: 104.722 ± 6.171
  Neural: 103.833 ± 6.525
  p-value: 0.8248 ns
Text Entropy:
  Standard: 4.201 ± 0.108
  Neural: 4.220 ± 0.123
  p-value: 1.0000 ns
Lexical Diversity:
  Standard: 0.581 ± 0.031
  Neural: 0.629 ± 0.083
  p-value: 0.7000 ns

### Qwen 14B
Average Token Count:
  Standard: 103.333 ± 6.525
  Neural: 99.278 ± 6.853
  p-value: 0.4000 ns
Text Entropy:
  Standard: 4.237 ± 0.105
  Neural: 4.297 ± 0.147
  p-value: 0.4000 ns
Lexical Diversity:
  Standard: 0.655 ± 0.042
  Neural: 0.638 ± 0.048
  p-value: 1.0000 ns


## SAMPLE TEXTS
================================================================================

### 14B | neural | prng
Seed: 42
Text:  The sea was heaving with great, dark waves, and the wind was howling like a thousand wolves. The sky was a swirling mass of gray, and the rain was coming down in sheets. It was the kind of night that...

### 14B | neural | qrng_int
Seed: 347338331
Text:  For the first time in 25 years, the lighthouse was_.
A. operating at full capacity
B. visited by tourists
C. abandoned
D. under repair

Okay, let's see. The question is about an old lighthouse keeper...

### 14B | neural | trng
Seed: 1735754245
Text:  The sea was churning in violent, frothing waves, and the wind howled through the rocks like a banshee. The lighthouse beam had long since died, its bulb burned out, leaving the world in darkness. The...

### 14B | standard | prng
Seed: 42
Text: The sea was churning with such force that it looked like a great white beast, roaring and thrashing against the cliffs. The wind howled through the rocks, and the waves crashed against the tower with ...

### 14B | standard | qrng_int
Seed: 347338331
Text: The sea was calm, but the air was electric with a strange energy. He stood on the cliff, watching the horizon where the sky and sea met. The sun was just beginning to set, casting an orange glow acros...

### 14B | standard | trng
Seed: 3287014838
Text: The storm was so fierce that it shook the ground, and the winds were howling like a pack of wolves. The sea was a churning mass of white and black, and the waves were so high that they looked like mou...

### 8B | neural | prng
Seed: 42
Text:  The sea was a violent, roiling mass of green and white, and the air was thick with the sound of wind howling through the cliffs. The waves crashed against the rocks below with a force that seemed to ...

### 8B | neural | qrng_int
Seed: 347338331
Text:  The sea was a flat, glassy, black thing, and the sky was the same color, and the wind had stopped. Even the waves had stopped. It was as if the world had been held in a vice and crushed until all the...

### 8B | neural | trng
Seed: 3120615489
Text:  The storm had come out of nowhere, and in less than an hour, the sea had risen more than three feet. The waves were monstrous, and the wind howled like a wounded beast. The lighthouse, which had stoo...

### 8B | standard | prng
Seed: 42
Text: The storm had passed, and the sea was calm again. But the sea floor was different. The old lighthouse keeper had spent his whole life near the sea, and he knew the sea floor better than anyone in the ...

### 8B | standard | qrng_int
Seed: 347338331
Text: The sea was a flat, glassy surface, not a breath of wind. The water was so still that the waves were like a mirror. It was so quiet that the only sound was the creak of the lighthouse. The old man had...

### 8B | standard | trng
Seed: 2304490869
Text: The sea was a violent, churning mass of white, and the wind screamed like a banshee. The storm had been raging for days, and the lighthouse was being battered by the waves. As the keeper stood at the ...

================================================================================
END OF REPORT
================================================================================