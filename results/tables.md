# EcoRecordTriageBench results

114 synthetic records (19 scenario families x 6 variants). Brackets: 95% cluster-bootstrap intervals (2000 draws over the 19 families). Values are percentages.

| Metric | llama3.1:8b (all tools run) | llama3.1:8b (model picks tools) | llama3.1:8b (no tools) | qwen2.5:3b (all tools run) | qwen2.5:3b (model picks tools) | qwen2.5:3b (no tools) |
|---|---|---|---|---|---|---|
| Exact issue set | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 7.0 [0.0, 19.3] | 89.5 [73.7, 100.0] | 78.9 [57.9, 94.7] | 9.6 [0.0, 23.7] |
| Triage action | 84.2 [68.4, 100.0] | 78.9 [57.9, 94.7] | 26.3 [10.5, 47.4] | 89.5 [73.7, 100.0] | 84.2 [68.4, 100.0] | 24.6 [5.3, 44.7] |
| Issue precision | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 20.6 [8.4, 33.1] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 12.9 [4.1, 25.8] |
| Issue recall | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 31.6 [10.5, 56.2] | 89.5 [76.2, 100.0] | 78.9 [60.0, 94.7] | 31.6 [10.5, 56.2] |
| Clean records left clean | 100.0 [0.0, 100.0] | 100.0 [0.0, 100.0] | 0.0 [0.0, 0.0] | 100.0 [0.0, 100.0] | 100.0 [0.0, 100.0] | 41.7 [0.0, 83.3] |
| Observation rule on specimens | 33.3 [0.0, 100.0] | 33.3 [0.0, 100.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 22.2 [0.0, 66.7] | 100.0 [0.0, 100.0] |
| Unsupported issue claimed | 5.3 [0.0, 15.8] | 5.3 [0.0, 15.8] | 0.0 [0.0, 0.0] | 10.5 [0.0, 26.3] | 15.8 [0.0, 31.6] | 0.0 [0.0, 0.0] |
| Tool recall | 100.0 [100.0, 100.0] | 96.1 [92.3, 99.3] | 0.0 [0.0, 0.0] | 100.0 [100.0, 100.0] | 86.5 [82.8, 91.0] | 0.0 [0.0, 0.0] |
| Tool precision | 100.0 [100.0, 100.0] | 96.2 [91.7, 100.0] | 0.0 [0.0, 0.0] | 100.0 [100.0, 100.0] | 95.1 [88.8, 100.0] | 0.0 [0.0, 0.0] |
| Invalid output | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Tool metrics are only meaningful when the model picks tools. 'Observation rule on specimens' is the share of non-HumanObservation records for which the model's own list (before filtering) contained a media, captive or identification issue.

## Paired differences between conditions (same model, same draws)

| Model | Comparison | Metric | Difference [95% CI] |
|---|---|---|---|
| llama3.1:8b | selective minus all_tools | Exact issue set | 0.0 [0.0, 0.0] |
| llama3.1:8b | selective minus all_tools | Triage action | -5.3 [-15.8, 0.0] |
| llama3.1:8b | selective minus all_tools | Issue precision | 0.0 [0.0, 0.0] |
| llama3.1:8b | selective minus all_tools | Issue recall | 0.0 [0.0, 0.0] |
| llama3.1:8b | selective minus all_tools | Clean records left clean | 0.0 [0.0, 0.0] |
| llama3.1:8b | selective minus all_tools | Observation rule on specimens | 0.0 [0.0, 0.0] |
| llama3.1:8b | no_tools minus all_tools | Exact issue set | -93.0 [-100.0, -80.7] |
| llama3.1:8b | no_tools minus all_tools | Triage action | -57.9 [-84.2, -31.6] |
| llama3.1:8b | no_tools minus all_tools | Issue precision | -79.4 [-91.6, -66.9] |
| llama3.1:8b | no_tools minus all_tools | Issue recall | -68.4 [-89.5, -43.8] |
| llama3.1:8b | no_tools minus all_tools | Clean records left clean | -100.0 [-100.0, 0.0] |
| llama3.1:8b | no_tools minus all_tools | Observation rule on specimens | -33.3 [-100.0, 0.0] |
| qwen2.5:3b | selective minus all_tools | Exact issue set | -10.5 [-26.3, 0.0] |
| qwen2.5:3b | selective minus all_tools | Triage action | -5.3 [-15.8, 0.0] |
| qwen2.5:3b | selective minus all_tools | Issue precision | 0.0 [0.0, 0.0] |
| qwen2.5:3b | selective minus all_tools | Issue recall | -10.5 [-27.8, 0.0] |
| qwen2.5:3b | selective minus all_tools | Clean records left clean | 0.0 [0.0, 0.0] |
| qwen2.5:3b | selective minus all_tools | Observation rule on specimens | 22.2 [0.0, 66.7] |
| qwen2.5:3b | no_tools minus all_tools | Exact issue set | -79.8 [-95.6, -63.2] |
| qwen2.5:3b | no_tools minus all_tools | Triage action | -64.9 [-85.1, -44.7] |
| qwen2.5:3b | no_tools minus all_tools | Issue precision | -87.1 [-95.9, -74.2] |
| qwen2.5:3b | no_tools minus all_tools | Issue recall | -57.9 [-78.9, -35.0] |
| qwen2.5:3b | no_tools minus all_tools | Clean records left clean | -58.3 [-100.0, 0.0] |
| qwen2.5:3b | no_tools minus all_tools | Observation rule on specimens | 100.0 [0.0, 100.0] |

## Fully correct (issues and action) by scenario family

| Family | llama3.1:8b (all tools run) | llama3.1:8b (model picks tools) | llama3.1:8b (no tools) | qwen2.5:3b (all tools run) | qwen2.5:3b (model picks tools) | qwen2.5:3b (no tools) |
|---|---|---|---|---|---|---|
| captive_or_cultivated | 100.0 | 100.0 | 0.0 | 100.0 | 100.0 | 0.0 |
| clean_human_observation | 100.0 | 100.0 | 0.0 | 100.0 | 100.0 | 83.3 |
| coordinate_and_media | 100.0 | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| coordinate_out_of_range | 100.0 | 100.0 | 0.0 | 100.0 | 100.0 | 0.0 |
| coordinates_missing | 100.0 | 100.0 | 0.0 | 100.0 | 0.0 | 0.0 |
| coordinates_non_numeric | 100.0 | 0.0 | 0.0 | 100.0 | 0.0 | 0.0 |
| date_and_consensus | 0.0 | 0.0 | 0.0 | 100.0 | 100.0 | 0.0 |
| date_future | 100.0 | 100.0 | 0.0 | 100.0 | 100.0 | 0.0 |
| date_invalid | 100.0 | 100.0 | 0.0 | 100.0 | 100.0 | 0.0 |
| date_missing | 100.0 | 100.0 | 33.3 | 100.0 | 100.0 | 0.0 |
| date_parts_mismatch | 100.0 | 100.0 | 0.0 | 100.0 | 100.0 | 0.0 |
| identification_insufficient | 100.0 | 100.0 | 0.0 | 100.0 | 100.0 | 0.0 |
| identification_low_consensus | 100.0 | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| invalid_basis_of_record | 100.0 | 100.0 | 0.0 | 100.0 | 100.0 | 0.0 |
| media_missing | 100.0 | 100.0 | 0.0 | 100.0 | 100.0 | 0.0 |
| specimen_invalid_coordinates | 0.0 | 0.0 | 0.0 | 100.0 | 100.0 | 0.0 |
| specimen_no_media_no_ids_control | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| taxon_conflict | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| zero_coordinate | 100.0 | 100.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## Runs

- **llama3.1:8b (all tools run):** temperature 0.0, seed 20261114; Ollama 0.40.16; model digest 46e0c10c039e; macOS-27.2-arm64-arm-64bit
- **llama3.1:8b (model picks tools):** temperature 0.0, seed 20261114; Ollama 0.40.16; model digest 46e0c10c039e; macOS-27.2-arm64-arm-64bit
- **llama3.1:8b (no tools):** temperature 0.0, seed 20261114; Ollama 0.40.16; model digest 46e0c10c039e; macOS-27.2-arm64-arm-64bit
- **qwen2.5:3b (all tools run):** temperature 0.0, seed 20261114; Ollama 0.40.16; model digest 357c53fb659c; macOS-27.2-arm64-arm-64bit
- **qwen2.5:3b (model picks tools):** temperature 0.0, seed 20261114; Ollama 0.40.16; model digest 357c53fb659c; macOS-27.2-arm64-arm-64bit
- **qwen2.5:3b (no tools):** temperature 0.0, seed 20261114; Ollama 0.40.16; model digest 357c53fb659c; macOS-27.2-arm64-arm-64bit
