# Data card: EcoRecordTriageBench v0.1.0

- **Dataset name:** EcoRecordTriageBench synthetic occurrence-record QA set
- **Version:** 0.1.0
- **Instances:** 114
- **Format:** JSON Lines (`scenarios.jsonl`)
- **Generation:** deterministic Python generator; 19 scenario families × 6 variants
- **Seed:** no random sampling is used in the v0.1.0 generator; variant IDs are deterministic
- **Source status:** fully synthetic records, informed by public metadata standards and quality guidance
- **Real observations included:** none
- **Personal data:** none
- **Images/audio:** none
- **Intended use:** software tests and controlled research on tool-using metadata triage agents
- **Out-of-scope use:** species identification, ecological inference, automated rejection of records, or claims about real-world record error prevalence
- **Known biases:** issue types and frequencies are hand-designed and balanced by scenario family; they do not reflect real-world frequency or severity
- **Labels:** generated from explicit mutation recipes, independent of the validator implementation
- **License:** CC0-1.0

The synthetic records are not observations of actual organisms or locations. Coordinates are test values and must not be mapped or interpreted ecologically.
