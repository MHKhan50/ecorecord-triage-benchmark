# Experiment protocol

## Objective

Measure whether an LLM agent can select and compose deterministic occurrence-record metadata validators and return the expected curator workflow action.

## Experimental conditions

1. `rules`: all validators applicable to the record type invoked, deterministic issue aggregation.
2. `ollama --mode all_tools`: oracle tool plan (every applicable validator runs); the model returns issues and an action from the outputs.
3. `ollama --mode selective`: the model chooses the tools, then returns issues and an action from their outputs.
4. `ollama --mode no_tools`: the model returns issues and an action from the record and the issue definitions alone.
5. Not implemented: random tool plan.

Models: `qwen2.5:3b` and `llama3.1:8b`, temperature 0, seed 20261114, at most 256 output tokens per call. With temperature 0 there is no sampling, so one run per condition is reported; repeats would test only determinism.

## Controls

- Dataset generation is seeded and checked into the repository.
- The temporal reference date is fixed at 2026-01-01.
- The dataset includes preserved-specimen controls to test record-type-specific rules.
- No network or external tool calls occur during benchmark execution.
- The model adapter is optional and separate from the deterministic baseline.

## Required reporting

Report the exact dataset hash, Python version, OS, Ollama version, model digest/tag, temperature, seed, number of repeated runs, all per-case outputs, metrics, and tool traces. For stochastic models, use at least five independent seeds and report mean, standard deviation and confidence intervals. Do not treat repeated runs on the same synthetic cases as independent real-world observations.

## Statistical analysis

For the current 114-case release, `scripts/analysis.py` reports point estimates with 95% cluster-bootstrap intervals over the 19 scenario families (2,000 draws), and paired differences between conditions of the same model using the same draws. These are descriptive. For a future expert-labelled real-record track, use paired comparisons on the same held-out records, bootstrap confidence intervals stratified by issue family, and appropriate correction for multiple metric comparisons. Report inter-annotator agreement and adjudication procedure.

## Stopping and safety

No agent may write to source records. Outputs are advisory labels only. A human curator retains control over any correction, publication, or suppression decision.
