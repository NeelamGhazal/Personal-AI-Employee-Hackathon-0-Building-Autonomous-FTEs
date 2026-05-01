#!/bin/bash
# run_ai_employee.sh - Scheduled script to run AI Employee tasks
# This script is called by cron every 5 minutes

# Set paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VAULT_PATH="/mnt/e/Full-Time-Equivalent-Hackathon-0/Full-Time-Equivalent-0/AI_Employee_Vault"
LOG_FILE="$VAULT_PATH/Logs/cron_$(date +%Y-%m-%d).log"

# Change to project directory
cd "$PROJECT_DIR"

# Log start
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting AI Employee scheduled run" >> "$LOG_FILE"

# Run reasoning loop (process Needs_Action items)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Running reasoning loop..." >> "$LOG_FILE"
/home/neela/.local/bin/uv run python src/ai_employee_watchers/reasoning_loop.py --once >> "$LOG_FILE" 2>&1

# Run approval orchestrator (process Approved items)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Running approval orchestrator..." >> "$LOG_FILE"
/home/neela/.local/bin/uv run python src/ai_employee_watchers/approval_orchestrator.py --once >> "$LOG_FILE" 2>&1

# Log completion
echo "[$(date '+%Y-%m-%d %H:%M:%S')] AI Employee scheduled run complete" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
