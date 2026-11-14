# Changelog

## 0.1.0 — 2026-11-14

- 114 synthetic occurrence records (19 scenario families x 6 variants) with recipe-based labels.
- Five read-only validators, a fixed triage policy and an all-checks rule baseline.
- Local Ollama agent in three conditions: all applicable tools run, model picks tools, no tools.
- Resumable model runs (`calls.jsonl`), invalid-output and unsupported-claim metrics, a specimen-rule metric.
- `scripts/run_all.sh` and `scripts/analysis.py` with cluster-bootstrap intervals over scenario families and charts.
- Results of the local run (two models, three conditions) in the README and `results/`.
- References checked on 14 November 2026.
