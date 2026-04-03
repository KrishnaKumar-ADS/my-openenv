#!/usr/bin/env bash
set -euo pipefail

export API_BASE_URL="${API_BASE_URL:-https://router.huggingface.co/v1}"
export MODEL_NAME="${MODEL_NAME:-Qwen/Qwen2.5-72B-Instruct}"
export HF_TOKEN="${HF_TOKEN:?Please set HF_TOKEN}"
export CS_ENV_URL="${CS_ENV_URL:-http://localhost:7860}"
export TEMPERATURE="${TEMPERATURE:-0.3}"

if [ -x "./.venv311/Scripts/python.exe" ]; then
	PYTHON_BIN="./.venv311/Scripts/python.exe"
elif [ -x "./.venv/Scripts/python.exe" ]; then
	PYTHON_BIN="./.venv/Scripts/python.exe"
elif command -v python >/dev/null 2>&1; then
	PYTHON_BIN="python"
elif command -v python3 >/dev/null 2>&1; then
	PYTHON_BIN="python3"
else
	echo "No Python interpreter found. Set PYTHON_BIN or install Python in PATH."
	exit 1
fi

for TASK in easy medium hard; do
	echo ""
	echo "========== Running task: $TASK =========="
	"$PYTHON_BIN" inference.py --task "$TASK"
done

echo ""
echo "All tasks completed."
