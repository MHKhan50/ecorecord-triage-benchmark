# Data dictionary

All rows in `data/scenarios.jsonl` are synthetic test fixtures. The outer JSON object contains:

| Field | Type | Meaning |
|---|---|---|
| `case_id` | string | Stable synthetic case identifier (`ERT-0001` etc.) |
| `scenario_family` | string | Controlled mutation family |
| `record` | object | Darwin Core-style occurrence metadata |
| `expected_issue_codes` | list[string] | Gold issue labels assigned by mutation recipe |
| `expected_triage_action` | string | Expected curator workflow action |
| `synthetic` | boolean | Always `true` in v0.1.0 |

Record fields:

| Field | Type | Meaning |
|---|---|---|
| `occurrenceID` | string | Synthetic occurrence identifier (URN; not a real record) |
| `basisOfRecord` | string | Darwin Core-style basis of record |
| `eventDate` | ISO date string or null | Observation/collection date |
| `year`, `month`, `day` | integer or null | Redundant date components used for consistency checks |
| `decimalLatitude` | number/string/null | Latitude in decimal degrees |
| `decimalLongitude` | number/string/null | Longitude in decimal degrees |
| `hasMedia` | boolean | Whether the synthetic human observation has media evidence |
| `isCaptiveOrCultivated` | boolean | Whether the organism is captive/cultivated |
| `observationTaxon` | string/null | Taxon attached to the observation |
| `communityTaxon` | string/null | Community-agreed taxon |
| `identificationCount` | integer | Synthetic number of identifications |
| `agreementCount` | integer | Synthetic number of agreeing identifications |
| `referenceDate` | ISO date string | Fixed temporal cutoff for future-date detection |

Issue codes and actions are defined in `ecorecord_triage/constants.py`.

## Standard terms versus benchmark extensions

The fields `basisOfRecord`, `eventDate`, `year`, `month`, `day`, `decimalLatitude`, `decimalLongitude` and `occurrenceID` are aligned with Darwin Core terms. `hasMedia`, `isCaptiveOrCultivated`, `observationTaxon`, `communityTaxon`, `identificationCount`, `agreementCount` and `referenceDate` are benchmark/platform-inspired extensions used to model iNaturalist-style verifiability and identification state. They are not presented as Darwin Core terms.
