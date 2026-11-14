# Experiment protocol

## Objective

Measure whether an LLM agent can select and compose deterministic occurrence-record metadata validators and return the expected curator workflow action.

## Experimental conditions

1. `rules`: all validators applicable to the record type invoked, deterministic issue aggregation.
2. `ollama`: model-selected tool plan, local tool execution, model-generated final issue set and action.
3. Future ablations (not implemented in v0.1.0): no-tool model, random tool plan, oracle tool plan.

## Controls

- Dataset generation is seeded and checked into the repository.
- The temporal reference date is fixed at 2026-01-01.
- The dataset includes preserved-specimen controls to test record-type-specific rules.
- No network or external tool calls occur during benchmark execution.
- The model adapter is optional and separate from the deterministic baseline.

## Required reporting

Report the exact dataset hash, Python version, OS, Ollama version, model digest/tag, temperature, seed, number of repeated runs, all per-case outputs, metrics, and tool traces. For stochastic models, use at least five independent seeds and report mean, standard deviation and confidence intervals. Do not treat repeated runs on the same synthetic cases as independent real-world observations.

## Statistical analysis

For the current 114-case release, report descriptive metrics only. For a future expert-labelled real-record track, use paired comparisons on the same held-out records, bootstrap confidence intervals stratified by issue family, and appropriate correction for multiple metric comparisons. Report inter-annotator agreement and adjudication procedure.

## Stopping and safety

No agent may write to source records. Outputs are advisory labels only. A human curator retains control over any correction, publication, or suppression decision.
