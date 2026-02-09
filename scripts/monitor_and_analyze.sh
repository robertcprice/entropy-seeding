#!/bin/bash
# Monitor experiment progress and trigger analysis when models complete
# Usage: nohup bash scripts/monitor_and_analyze.sh &

cd /Users/bobbyprice/projects/entropy/entropy-seeding

LAST_QWEN8B_LINES=0
LAST_MISTRAL_LINES=0
LAST_LLAMA_LINES=0

check_completion() {
    local log_file=$1
    local model_name=$2

    if [ -f "$log_file" ]; then
        if grep -q "ALL EXPERIMENTS COMPLETE\|Results saved:" "$log_file" 2>/dev/null; then
            echo "$(date): $model_name COMPLETE"
            return 0
        fi
    fi
    return 1
}

while true; do
    # Check qwen3:8b
    if check_completion /tmp/entropy_experiment_qwen3_8b.log "qwen3:8b"; then
        if [ ! -f /tmp/.qwen8b_analyzed ]; then
            echo "$(date): Analyzing qwen3:8b..."
            touch /tmp/.qwen8b_analyzed
        fi
    fi

    # Check mistral
    if check_completion /tmp/entropy_experiment_mistral.log "mistral:latest"; then
        if [ ! -f /tmp/.mistral_analyzed ]; then
            echo "$(date): Analyzing mistral..."
            touch /tmp/.mistral_analyzed
        fi
    fi

    # Check llama
    if check_completion /tmp/entropy_experiment_llama.log "llama3.1:8b"; then
        if [ ! -f /tmp/.llama_analyzed ]; then
            echo "$(date): Analyzing llama3.1:8b..."
            touch /tmp/.llama_analyzed
        fi
    fi

    # Progress report
    Q8=$(grep -c "chars$" /tmp/entropy_experiment_qwen3_8b.log 2>/dev/null || echo 0)
    MI=$(grep -c "chars$" /tmp/entropy_experiment_mistral.log 2>/dev/null || echo 0)
    LL=$(grep -c "chars$" /tmp/entropy_experiment_llama.log 2>/dev/null || echo 0)
    echo "$(date '+%H:%M'): qwen3:8b=$Q8/360  mistral=$MI/360  llama=$LL/360"

    # Check if all done
    if [ -f /tmp/.qwen8b_analyzed ] && [ -f /tmp/.mistral_analyzed ] && [ -f /tmp/.llama_analyzed ]; then
        echo "$(date): ALL MODELS COMPLETE AND ANALYZED"
        break
    fi

    sleep 120
done
