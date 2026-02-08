# Mistral Architecture: Entropy Source Testing Notes

## Models Tested

**Note:** Mistral models were tested as part of the neural_feedback_quantum experiments, which compared PRNG vs QRNG with standard generation (no neural modulation data available).

### Mistral 7B
- **Test configurations:** PRNG, QRNG (standard generation only)
- **Tests:** Basic entropy source comparison
- **Status:** Limited data - no neural modulation tests found

## Key Findings

### Configurations Tested:
- `standard + prng` - Baseline generation with pseudo-random
- `standard + qrng_int` - Quantum integer seeding

### General Pattern:
Mistral 7B showed expected differences between PRNG and QRNG:
- QRNG produced more structured/organized output
- PRNG produced more variable output
- Similar to patterns observed in other 7B models

## Data Availability

Full results are available in the main `/results/neural_feedback_quantum/` directory with individual test folders for each configuration.

**Note:** For comprehensive PRNG vs TRNG vs QRNG comparisons, see the Qwen and DeepSeek-R1 architecture reports. Mistral was not included in the main entropy source study due to limited test coverage.

---

*Mistral 7B is a dense transformer architecture similar to Qwen3, but with different training data and initialization. Results may vary due to these differences.*
