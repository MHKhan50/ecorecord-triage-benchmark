#!/bin/sh
# Full EcoRecordTriageBench study with local models through Ollama.
# 2 models x 3 conditions x 114 records = 684 records, 912 model calls
# (the "model picks tools" condition makes two calls per record).
# Every record is saved as it finishes; if the run stops, run this script again and it resumes.
set -eu
cd "$(dirname "$0")/.."
MODELS="${MODELS:-qwen2.5:3b llama3.1:8b}"

if ! curl -s http://localhost:11434/api/version >/dev/null; then
  echo "Ollama is not running. Open the Ollama app (or run: ollama serve) and try again."
  exit 1
fi
for m in $MODELS; do
  if ! ollama list | awk 'NR>1 {print $1}' | grep -qx "$m"; then
    echo "Model $m is not installed. Run: ollama pull $m"
    exit 1
  fi
done

python3 -m unittest discover -s tests
python3 -m ecorecord_triage.cli --agent rules >/dev/null
echo "Rule baseline done."

for m in $MODELS; do
  for mode in all_tools selective no_tools; do
    echo "== $m, $mode"
    python3 -m ecorecord_triage.cli --agent ollama --model "$m" --mode "$mode" --temperature 0 \
      | grep -E "cases|exact_issue_set_accuracy|triage_action_accuracy"
  done
done

python3 scripts/analysis.py
