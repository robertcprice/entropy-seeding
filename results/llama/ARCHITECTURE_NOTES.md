# Llama Architecture: Entropy Source Testing Notes

## Models Tested

**Note:** Llama models were tested as part of the neural_feedback_quantum experiments, which compared PRNG vs QRNG with and without neural modulation. These were not full PRNG vs TRNG vs QRNG comparisons like the main study.

### Llama 1B
- **Test configurations:** PRNG, QRNG (with/without neural modulation)
- **Tests:** Comprehensive neural feedback experiments
- **Status:** Limited data - primarily for neural modulation studies

### Llama 8B
- **Test configurations:** PRNG, QRNG (with/without neural modulation)
- **Tests:** Comprehensive neural feedback experiments
- **Status:** Limited data - primarily for neural modulation studies

## Key Findings from Neural+QRNG Tests

### Configurations Tested:
- `standard + prng` - Baseline generation with pseudo-random
- `standard + qrng_int` - Quantum integer seeding
- `neural + prng` - Neural feedback modulation + PRNG
- `neural + qrng_int` - Neural feedback modulation + QRNG

### General Pattern:
Llama models showed similar patterns to Qwen models:
- Neural modulation changed output characteristics
- QRNG produced different behavior than PRNG
- Effects varied by model size

## Data Availability

Full results are available in the main `/results/neural_feedback_quantum/` directory with individual test folders for each configuration.

**Note:** For comprehensive PRNG vs TRNG vs QRNG comparisons, see the Qwen and DeepSeek-R1 architecture reports.

---

*For more details on neural modulation techniques, see the comprehensive report section on advanced techniques.*
