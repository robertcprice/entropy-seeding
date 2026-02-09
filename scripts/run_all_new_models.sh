#!/bin/bash
# Run comprehensive experiments on all 3 new models sequentially
# Each produces 360 generations (15 single-turn + 3 multi-turn × 3 sources × 5 samples)

PYTHON="/Users/bobbyprice/projects/entropy/.venv/bin/python"
SCRIPT="/Users/bobbyprice/projects/entropy/entropy-seeding/scripts/run_comprehensive_experiment.py"

echo "=============================================="
echo "Starting 3-model comprehensive experiment run"
echo "Time: $(date)"
echo "=============================================="

echo ""
echo ">>> MODEL 1/3: gemma3 (Google, 4B, Gemma3 Architecture)"
echo ">>> Start: $(date)"
$PYTHON "$SCRIPT" --model gemma3 --samples 5
echo ">>> Finished gemma3: $(date)"

echo ""
echo ">>> MODEL 2/3: phi4-mini (Microsoft, 3.8B)"
echo ">>> Start: $(date)"
$PYTHON "$SCRIPT" --model phi4-mini --samples 5
echo ">>> Finished phi4-mini: $(date)"

echo ""
echo ">>> MODEL 3/3: llama3.2:3b (Meta, 3B, GQA)"
echo ">>> Start: $(date)"
$PYTHON "$SCRIPT" --model llama3.2:3b --samples 5
echo ">>> Finished llama3.2:3b: $(date)"

echo ""
echo "=============================================="
echo "ALL 3 EXPERIMENTS COMPLETE: $(date)"
echo "=============================================="
