# EcoRecordTriageBench v0.1.0

**Tool-using agent triage of citizen-science biodiversity occurrence records**

Suggested repository: `MHKhan50/ecorecord-triage-benchmark`

## Why this project

Biodiversity occurrence records are useful only when their metadata can be interpreted responsibly. GBIF documents more than 60 occurrence issues and flags, including invalid/zero coordinates, invalid dates and date-component mismatches. iNaturalist uses a separate community Data Quality Assessment: a verifiable observation needs a date, georeferencing, media evidence and a wild/not-captive status; Research Grade additionally depends on community identification agreement and agreement between observation and community taxa. These are related but not identical quality systems.

Recent peer-reviewed LLM work in ecology has benchmarked species-level tasks such as taxonomy, geographic distribution, conservation status and threat identification. That work reports substantial task-dependent performance differences. EcoRecordTriageBench deliberately studies a narrower, different question: **can a tool-using agent correctly orchestrate deterministic metadata checks and route a record to a sensible curator action without treating every record type as if it were a casual field observation?**

This is a controlled methods benchmark, not a claim that an LLM should replace biodiversity curators, taxonomists or GBIF/iNaturalist quality systems. It is distinct from generic historical reasoning and species-knowledge benchmarks because its unit of evaluation is an occurrence-record metadata bundle plus tool-selection and triage behaviour.

## Research gap and novelty boundary

The existing infrastructure already supplies mature deterministic flags and community review workflows. Therefore, this project does **not** claim to invent occurrence validation, species identification, or a new biodiversity quality standard. The narrower research question is the evaluation of an LLM agent that selects and composes existing read-only validators, then maps their outputs to a bounded curator workflow. The initial dataset is synthetic and controlled; a defensible publication claim would require later expert annotation and evaluation on real, appropriately licensed occurrence records. The gap is provisional and must be revisited through a fuller systematic review before journal submission.

## Research questions

- **RQ1:** How accurately can a tool-using LLM agent identify controlled metadata-quality issues compared with a deterministic all-checks baseline?
- **RQ2:** How does selective validator invocation affect issue recall, tool precision/recall and false-positive burden?
- **RQ3:** Do record-type-aware exceptions (for example, preserved specimens not requiring the same media/identification checks as human observations) reduce inappropriate triage?

## Falsifiable hypotheses

- **H1:** The deterministic reference agent will achieve perfect agreement with the controlled labels because the labels are generated from explicit mutation recipes; this is a pipeline sanity check, not a model-performance result.
- **H2:** On this small synthetic set, a local LLM agent will have lower issue-set exact match than the deterministic baseline unless its tool plan covers all relevant validator families.
- **H3:** Including preserved-specimen controls will expose false positives from agents that apply human-observation rules indiscriminately.

These hypotheses are not findings. No LLM experiment has been run as part of this release.

## Scope and dataset

- 114 **synthetic** cases: 19 scenario families × 6 deterministic variants.
- Scenario families cover valid human observations, coordinate/date errors, missing media, captive/cultivated status, limited identification agreement, taxon conflicts, multi-issue cases, and preserved-specimen controls.
- Each case includes a `record` using Darwin Core occurrence fields plus explicitly documented platform-inspired extension fields, a controlled expected issue set, a triage action, and an explicit `synthetic: true` marker.
- No real citizen-science observations, personal observer identifiers, images, or sensitive locations are included.
- The fixed reference date (`2026-01-01`) makes future-date checks reproducible and independent of the day the benchmark is run.

**Important:** the dataset is a test fixture, not a sample of real biodiversity records. The synthetic labels measure implementation behaviour under known perturbations; they do not estimate real-world prevalence or ecological validity.

## Methodology

The agent receives one record and a menu of five read-only local tools:

1. `check_basis_of_record`
2. `check_coordinates`
3. `check_dates`
4. `check_verifiability`
5. `check_identification`

The optional Ollama adapter has two stages: (a) select validator tools using a constrained JSON plan; (b) execute the selected tools locally and return issue codes plus a triage action using a second constrained JSON output. The model cannot mutate records or access the network through tools. The deterministic baseline invokes every validator applicable to the record type; human observations use all five, while specimen/non-observation records skip iNaturalist-specific media and community-identification checks.

### Baselines

- **All-checks rule agent:** invokes all five validators and applies the published triage precedence.
- **Ollama tool-using agent:** optional local model adapter; no model results are supplied in this release.
- **Ablations to add in a later study:** no-tool LLM, random tool selection, and oracle tool selection. Do not compare models until prompts, model hashes, seeds, and run counts are frozen.

### Metrics

- issue micro precision, recall and F1;
- issue macro F1;
- exact issue-set accuracy;
- triage-action accuracy;
- clean-case specificity and false-positive clean-case rate;
- tool precision and tool recall against the validator families applicable to each record type.

Report per-issue confusion counts and bootstrap confidence intervals in a substantive paper. With only 114 synthetic cases, aggregate point estimates are descriptive and should not be generalised to field records.

## Reproduction

Python 3.9+; standard library only. No model download is required for the deterministic baseline.

```bash
python3 -m unittest discover -s tests -v
python3 scripts/generate_dataset.py
python3 -m ecorecord_triage.cli --agent rules --output-dir outputs/rules
```

Optional local model run (requires Ollama and a locally available model):

```bash
ollama pull qwen2.5:3b
python3 -m ecorecord_triage.cli --agent ollama --model qwen2.5:3b --temperature 0 --seed 20261114 --output-dir outputs/qwen25-3b
```

The Ollama adapter uses the local `/api/generate` endpoint and JSON Schema output. Model outputs can vary by Ollama/model version; record the exact model tag, Ollama version and run environment with any published results.

## Experiment protocol for a publishable extension

1. Freeze the current synthetic v0.1.0 dataset and run the test suite.
2. Conduct a systematic literature search across biodiversity informatics, citizen science, data quality, LLM agents and tool-using evaluation.
3. Ask biodiversity data curators to review the rule definitions and triage mapping before creating a real-record track.
4. Build a separate, consented/licensed real-record test set. Preserve source licence, source ID, retrieval date and any coordinate generalisation; do not redistribute restricted coordinates or media.
5. Separate development and held-out records by source dataset and taxon to reduce leakage.
6. Compare the all-checks baseline, no-tool LLM, tool-using LLM and oracle-tool ablation across at least 5 seeds where model sampling permits.
7. Report per-issue precision/recall, macro F1, triage accuracy, tool coverage, false-positive burden, latency and token/call cost.
8. Have at least two qualified reviewers independently annotate real-record cases; report agreement and adjudication. Do not treat iNaturalist Research Grade as infallible ground truth.
9. Publish prompts, model versions, exact data licences, annotation guidelines, raw per-case outputs and analysis scripts.

## Limitations

- Synthetic cases cannot establish performance on noisy real submissions, ecological plausibility, geographic range or species identity.
- The benchmark omits country-polygon checks, taxonomic synonym resolution, image/audio verification, phenology and sampling bias.
- The identification consensus check is intentionally simplified. iNaturalist's production community-taxon algorithm is more nuanced than a raw agreement-count ratio.
- A correct metadata triage action does not establish that a species identification is correct or that a record is fit for every downstream analysis.
- The deterministic baseline is expected to dominate on rules it directly implements; this is a diagnostic reference, not an argument for LLM autonomy.
- Legal, ecological and platform-specific decisions remain with qualified humans and the authoritative data providers.

## Ethics and responsible use

- Do not use this package to automatically delete, reject or downgrade observations.
- Do not infer observer competence or intent from metadata anomalies.
- A flagged record means “inspect or correct this field,” not “the observation is false.”
- Avoid exposing precise locations of threatened species or sensitive taxa in any future real-data track.
- Respect iNaturalist observation-level licences and GBIF dataset licences; do not assume all records are freely redistributable.
- The current dataset is synthetic and contains no personal data.

## Data dictionary and project files

See [`docs/LITERATURE_REVIEW.md`](docs/LITERATURE_REVIEW.md), [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md), [`docs/EXPERIMENT_PROTOCOL.md`](docs/EXPERIMENT_PROTOCOL.md) and [`data/DATA_CARD.md`](data/DATA_CARD.md).

## References and provenance

1. Darwin Core / TDWG, current biodiversity data-sharing standard: https://dwc.tdwg.org/
2. GBIF, Occurrence issues and flags: https://techdocs.gbif.org/en/data-use/occurrence-issues-and-flags
3. iNaturalist, Data Quality Assessment and Research Grade criteria: https://help.inaturalist.org/en/support/solutions/articles/151000169936
4. iNaturalist, Community Taxon and Observation Taxon definitions and algorithm: https://help.inaturalist.org/en/support/solutions/articles/151000173076
5. Johnston et al. (2023), “Identifying the identifiers: How iNaturalist facilitates collaborative, research-relevant data generation and why it matters for biodiversity science,” *BioScience*: https://doi.org/10.1093/biosci/biad051
6. Dorm et al. (2026), “Large language models possess some ecological knowledge, but how much?”, *Ecological Informatics*, 95, 103699: https://doi.org/10.1016/j.ecoinf.2026.103699
7. GBIF, data-quality handling guide: https://training.gbif.org/en/data-use/data-quality

## License

Code: MIT. Synthetic dataset: CC0-1.0. See `LICENSE` and `data/DATA_CARD.md`.
