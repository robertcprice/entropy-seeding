# Experiment Run Plan

## Why This Order

The seed bottleneck means effects shrink as models get bigger. Start where effects are strongest (small models), confirm with proper stats, then scale up to find the crossover point. Then skip the bottleneck entirely with direct injection.

## Phase 1: Small Models (where we KNOW effects exist)

These run via ollama on your Mac. Each takes ~2-4 hours.

```bash
# Step 1: Smallest model first — fastest iteration
python scripts/run_comprehensive_experiment_v2.py \
    --model qwen3:0.6b --samples 10 --temperature 0.7 --single-stream

# Step 2: Analyze immediately
python scripts/statistical_analysis_v2.py results/v2_experiments/qwen/<latest>.json

# Step 3: If effects detected, run full 5-stream version
python scripts/run_comprehensive_experiment_v2.py \
    --model qwen3:0.6b --samples 10 --temperature 0.7

# Step 4: Run the control experiment to verify mechanism
python scripts/run_control_experiment.py --model qwen3:0.6b --seeds-per-source 20
```

## Phase 2: Scale Ladder (find the crossover)

Run each model, analyze, compare. Go in order of size.

```bash
# 1.7B
python scripts/run_comprehensive_experiment_v2.py \
    --model qwen3:1.7b --samples 10 --single-stream

# 3B
python scripts/run_comprehensive_experiment_v2.py \
    --model llama3.2:3b --samples 10 --single-stream

# 4B (Gemma showed effects here in v1)
python scripts/run_comprehensive_experiment_v2.py \
    --model gemma3:4b --samples 10 --single-stream

# 4B (Qwen showed NO effects — architecture comparison)
python scripts/run_comprehensive_experiment_v2.py \
    --model qwen3:4b --samples 10 --single-stream

# 8B
python scripts/run_comprehensive_experiment_v2.py \
    --model qwen3:8b --samples 10 --single-stream
```

After each, run analysis and compare effect sizes across scales:
```bash
python scripts/statistical_analysis_v2.py results/v2_experiments/<family>/<file>.json
```

## Phase 3: Direct Entropy Injection (skip the bottleneck)

This is the real experiment — entropy modifies the sampling process directly,
not through a 32-bit seed. Uses HuggingFace transformers, not ollama.

```bash
# Small model first
python scripts/run_direct_injection_experiment.py \
    --model distilgpt2 --samples 20

# Then scale up
python scripts/run_direct_injection_experiment.py \
    --model gpt2 --samples 20

python scripts/run_direct_injection_experiment.py \
    --model gpt2-medium --samples 20
```

## Phase 4: Scale Up Seed Experiment (if Phase 1-2 show anything)

Only if Phase 1-2 show real effects after FDR correction:

```bash
# Increase samples to 20+ per condition
python scripts/run_comprehensive_experiment_v2.py \
    --model <model_with_effects> --samples 20
```

## What to Look For

After each analysis, check these numbers:

1. **BH-corrected significance**: Are ANY tests significant after FDR correction?
   - If yes → real effect, investigate further
   - If no → either no effect or underpowered

2. **Power**: Is the test adequately powered (power >= 0.80)?
   - If no → can't conclude anything, need more samples
   - If yes AND not significant → genuine null result

3. **Seed distributions**: Are the sources actually different?
   - If distributions are identical → no mechanism for effect
   - If distributions differ → mechanism exists

4. **Mixed-effects vs paired**: Does the mixed-effects model find something the paired test missed?
   - Mixed-effects uses all samples (more power)
   - If mixed-effects finds it but paired doesn't → real but small effect

## Decision Tree

```
Start with 0.6B
  ├── Effects survive FDR?
  │   ├── YES → Scale up (1.7B, 3B, 4B, 8B)
  │   │         Find where effects disappear
  │   │         Publish scale-dependent finding
  │   └── NO  → Check power
  │       ├── Underpowered → increase samples to 20
  │       └── Adequately powered, still nothing
  │           → Seed effects don't exist even at 0.6B
  │           → Focus on direct injection (Phase 3)
  │
  Direct injection experiment
  ├── Logit perturbation shows effects?
  │   ├── YES → This proves entropy matters when it
  │   │         actually touches the sampling process
  │   └── NO  → LLMs are robust to entropy source
  │            regardless of injection method
```
