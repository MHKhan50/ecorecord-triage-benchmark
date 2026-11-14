"""Load and generate the controlled synthetic benchmark dataset."""
import json
from pathlib import Path



def load_dataset(path):
    rows = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _gold_triage_action(issue_codes):
    """Independent label-oracle implementation for the controlled recipes."""
    issues = set(issue_codes)
    if "TAXON_CONFLICT" in issues:
        return "EXPERT_REVIEW"
    metadata = {
        "BASIS_OF_RECORD_INVALID", "COORDINATES_MISSING", "COORDINATES_INVALID",
        "COORDINATE_OUT_OF_RANGE", "ZERO_COORDINATE", "RECORDED_DATE_MISSING",
        "RECORDED_DATE_INVALID", "RECORDED_DATE_FUTURE", "RECORDED_DATE_MISMATCH",
        "MEDIA_MISSING", "CAPTIVE_OR_CULTIVATED",
    }
    if issues.intersection(metadata):
        return "REQUEST_CORRECTION"
    if issues.intersection({"INSUFFICIENT_IDENTIFICATIONS", "LOW_IDENTIFICATION_CONSENSUS"}):
        return "COMMUNITY_IDENTIFICATION"
    return "READY_FOR_RESEARCH_PIPELINE"


def _base_record(index):
    day = (index % 24) + 1
    lat = 12.345 + ((index % 7) * 0.01)
    lon = 67.890 + ((index % 9) * 0.01)
    return {
        "occurrenceID": "urn:synthetic:ecorecord:{0:04d}".format(index),
        "basisOfRecord": "HumanObservation",
        "eventDate": "2024-06-{0:02d}".format(day),
        "year": 2024,
        "month": 6,
        "day": day,
        "decimalLatitude": round(lat, 5),
        "decimalLongitude": round(lon, 5),
        "hasMedia": True,
        "isCaptiveOrCultivated": False,
        "observationTaxon": "Falco peregrinus",
        "communityTaxon": "Falco peregrinus",
        "identificationCount": 3,
        "agreementCount": 3,
        "referenceDate": "2026-01-01",
    }


def build_dataset():
    """Return 114 controlled cases (19 scenario families x 6 variants).

    Every case is synthetic. Labels are assigned by the mutation recipe, not
    inferred by running the reference validators, avoiding label/implementation
    circularity. The data are designed for method testing, not ecological inference.
    """
    families = [
        ("invalid_basis_of_record", ["BASIS_OF_RECORD_INVALID"], lambda r: r.update({"basisOfRecord": "UnrecognisedRecordType"})),
        ("clean_human_observation", [], lambda r: None),
        ("coordinate_out_of_range", ["COORDINATE_OUT_OF_RANGE"], lambda r: r.update({"decimalLatitude": 95.0})),
        ("zero_coordinate", ["ZERO_COORDINATE"], lambda r: r.update({"decimalLatitude": 0.0, "decimalLongitude": 0.0})),
        ("coordinates_missing", ["COORDINATES_MISSING"], lambda r: r.update({"decimalLatitude": None, "decimalLongitude": None})),
        ("coordinates_non_numeric", ["COORDINATES_INVALID"], lambda r: r.update({"decimalLatitude": "north", "decimalLongitude": "west"})),
        ("date_invalid", ["RECORDED_DATE_INVALID"], lambda r: r.update({"eventDate": "2024-02-30"})),
        ("date_future", ["RECORDED_DATE_FUTURE"], lambda r: r.update({"eventDate": "2027-02-01", "year": 2027, "month": 2, "day": 1})),
        ("date_missing", ["RECORDED_DATE_MISSING"], lambda r: r.update({"eventDate": None})),
        ("date_parts_mismatch", ["RECORDED_DATE_MISMATCH"], lambda r: r.update({"year": 2023})),
        ("media_missing", ["MEDIA_MISSING"], lambda r: r.update({"hasMedia": False})),
        ("captive_or_cultivated", ["CAPTIVE_OR_CULTIVATED"], lambda r: r.update({"isCaptiveOrCultivated": True})),
        ("identification_insufficient", ["INSUFFICIENT_IDENTIFICATIONS"], lambda r: r.update({"identificationCount": 1, "agreementCount": 1})),
        ("identification_low_consensus", ["LOW_IDENTIFICATION_CONSENSUS"], lambda r: r.update({"identificationCount": 4, "agreementCount": 2})),
        ("taxon_conflict", ["TAXON_CONFLICT"], lambda r: r.update({"communityTaxon": "Accipiter nisus"})),
        ("coordinate_and_media", ["COORDINATE_OUT_OF_RANGE", "MEDIA_MISSING"], lambda r: r.update({"decimalLongitude": 181.0, "hasMedia": False})),
        ("date_and_consensus", ["RECORDED_DATE_MISMATCH", "LOW_IDENTIFICATION_CONSENSUS"], lambda r: r.update({"year": 2023, "identificationCount": 4, "agreementCount": 2})),
        ("specimen_no_media_no_ids_control", [], lambda r: r.update({"basisOfRecord": "PreservedSpecimen", "eventDate": "1890-04-03", "year": 1890, "month": 4, "day": 3, "hasMedia": False, "identificationCount": 0, "agreementCount": 0})),
        ("specimen_invalid_coordinates", ["COORDINATE_OUT_OF_RANGE"], lambda r: r.update({"basisOfRecord": "PreservedSpecimen", "eventDate": "1890-04-03", "year": 1890, "month": 4, "day": 3, "hasMedia": False, "identificationCount": 0, "agreementCount": 0, "decimalLatitude": 91.0})),
    ]
    cases = []
    index = 1
    for family_name, issue_codes, mutate in families:
        for variant in range(6):
            record = _base_record(index)
            mutate(record)
            # The date-mismatch family intentionally keeps eventDate fixed and
            # changes only the redundant year field; this is a cross-field test.
            expected = sorted(issue_codes)
            case = {
                "case_id": "ERT-{0:04d}".format(index),
                "scenario_family": family_name,
                "record": record,
                "expected_issue_codes": expected,
                "expected_triage_action": _gold_triage_action(expected),
                "synthetic": True,
            }
            cases.append(case)
            index += 1
    return cases


def write_dataset(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cases = build_dataset()
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        for case in cases:
            handle.write(json.dumps(case, ensure_ascii=False, sort_keys=True) + "\n")
    return len(cases)
