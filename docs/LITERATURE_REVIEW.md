# Focused literature and overlap review

**Search cut-off:** 14 November 2026. This is a focused scoping review for project selection, not a registered systematic review.

## Problem evidence

Biodiversity occurrence records are exchanged using Darwin Core, a maintained vocabulary and conceptual model for taxa, occurrences, events, locations, identifications and media. GBIF documents more than 60 occurrence issues and flags, including zero/out-of-range coordinates, invalid dates and date-component mismatches. These are not hypothetical concerns: they are established data-publishing and downstream data-use quality problems.

iNaturalist applies a distinct community DQA. Its public guidance defines verifiable observations using date, georeferencing, media and wild/cultivated status, and describes Research Grade as a community identification outcome. The Community Taxon and Observation Taxon are separate concepts; the production algorithm is more nuanced than a simple vote count. Campbell et al. (2023) empirically analyse the identifier ecosystem and discuss the importance and biases of community identification for research use.

## Existing methods and adjacent AI literature

- **Deterministic infrastructure:** Darwin Core provides the data vocabulary; GBIF exposes occurrence issue flags; iNaturalist combines record-quality criteria with community identification. These systems should be treated as authoritative reference points, not replaced by an LLM.
- **Ecological LLM evaluation:** Dorm et al. (2026) benchmark general-purpose LLMs on species-level taxonomy, distribution, conservation status, threats and traits. Their task-level differences motivate careful domain-specific evaluation, but their task unit is not the controlled orchestration of occurrence-metadata validators.
- **Community quality processes:** Campbell et al. (2023) show that identifier participation and consensus processes are central to iNaturalist's research relevance, while also noting unevenness and identification bias.

## Candidate gap and novelty boundary

The focused search found mature deterministic record-quality systems and recent LLM ecology benchmarks, but did not identify a directly matching, peer-reviewed benchmark for **LLM agents selecting read-only occurrence-metadata validators and routing records to a bounded curator workflow with record-type-specific exceptions**. This is a candidate gap, not proof of novelty: absence from a targeted search cannot establish that no related work exists. A full systematic search across biodiversity informatics, citizen-science quality assurance, ecological AI and agent tool-use evaluation is required before any “first” or “novel benchmark” claim.

The proposed contribution is therefore deliberately modest: a transparent, synthetic, reproducible test harness for the tool-selection and triage layer. It does not claim new ecological knowledge, a new data-quality standard, taxonomic identification, or real-world quality estimation.

## Portfolio overlap assessment

The project is distinct in task and application domain from the user's listed agent reliability, memory, cancellation, retry, pagination, policy and decomposition benchmarks, and from their Pakistan climate, water, flood, air-quality, price and agriculture projects. It does not reuse those datasets or rename their research questions. The shared high-level use of an agent benchmark is a research-method pattern, not a substantive task overlap.

## Feasibility

The v0.1.0 package uses Python's standard library, 114 synthetic records, five small deterministic tools and an optional two-stage Ollama adapter. No fine-tuning, vector database, GIS stack, GPU, image model or external API is required for the baseline. This is compatible with a 16 GB MacBook Air development workflow. The package is a pilot research instrument only; credible empirical claims require expert-reviewed real records, source-specific licences, careful location handling and a broader held-out evaluation.

## Sources

1. TDWG, Darwin Core: https://dwc.tdwg.org/
2. GBIF, Occurrence issues and flags: https://techdocs.gbif.org/en/data-use/occurrence-issues-and-flags
3. iNaturalist, DQA and Research Grade: https://help.inaturalist.org/en/support/solutions/articles/151000169936
4. iNaturalist, Community Taxon and Observation Taxon: https://help.inaturalist.org/en/support/solutions/articles/151000173076
5. Campbell et al. (2023), *BioScience*, 73(7), 533–541: https://doi.org/10.1093/biosci/biad051
6. Dorm et al. (2026), *Ecological Informatics*, 95, 103699: https://doi.org/10.1016/j.ecoinf.2026.103699
