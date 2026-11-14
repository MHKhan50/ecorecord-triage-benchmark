"""Shared benchmark vocabulary and evaluation policy."""

TOOL_NAMES = [
    "check_basis_of_record",
    "check_coordinates",
    "check_dates",
    "check_verifiability",
    "check_identification",
]

BASIS_OF_RECORD_VALUES = {
    "HumanObservation",
    "MachineObservation",
    "PreservedSpecimen",
    "FossilSpecimen",
    "LivingSpecimen",
    "MaterialSample",
    "Occurrence",
    "Event",
    "Taxon",
}

ISSUE_CODES = [
    "BASIS_OF_RECORD_INVALID",
    "COORDINATES_MISSING",
    "COORDINATES_INVALID",
    "COORDINATE_OUT_OF_RANGE",
    "ZERO_COORDINATE",
    "RECORDED_DATE_MISSING",
    "RECORDED_DATE_INVALID",
    "RECORDED_DATE_FUTURE",
    "RECORDED_DATE_MISMATCH",
    "MEDIA_MISSING",
    "CAPTIVE_OR_CULTIVATED",
    "INSUFFICIENT_IDENTIFICATIONS",
    "LOW_IDENTIFICATION_CONSENSUS",
    "TAXON_CONFLICT",
]

TRIAGE_ACTIONS = [
    "READY_FOR_RESEARCH_PIPELINE",
    "REQUEST_CORRECTION",
    "COMMUNITY_IDENTIFICATION",
    "EXPERT_REVIEW",
]

METADATA_ISSUES = {
    "BASIS_OF_RECORD_INVALID",
    "COORDINATES_MISSING",
    "COORDINATES_INVALID",
    "COORDINATE_OUT_OF_RANGE",
    "ZERO_COORDINATE",
    "RECORDED_DATE_MISSING",
    "RECORDED_DATE_INVALID",
    "RECORDED_DATE_FUTURE",
    "RECORDED_DATE_MISMATCH",
    "MEDIA_MISSING",
    "CAPTIVE_OR_CULTIVATED",
}
IDENTIFICATION_ISSUES = {
    "INSUFFICIENT_IDENTIFICATIONS",
    "LOW_IDENTIFICATION_CONSENSUS",
}

ISSUE_TO_TOOL = {
    "BASIS_OF_RECORD_INVALID": "check_basis_of_record",
    "COORDINATES_MISSING": "check_coordinates",
    "COORDINATES_INVALID": "check_coordinates",
    "COORDINATE_OUT_OF_RANGE": "check_coordinates",
    "ZERO_COORDINATE": "check_coordinates",
    "RECORDED_DATE_MISSING": "check_dates",
    "RECORDED_DATE_INVALID": "check_dates",
    "RECORDED_DATE_FUTURE": "check_dates",
    "RECORDED_DATE_MISMATCH": "check_dates",
    "MEDIA_MISSING": "check_verifiability",
    "CAPTIVE_OR_CULTIVATED": "check_verifiability",
    "INSUFFICIENT_IDENTIFICATIONS": "check_identification",
    "LOW_IDENTIFICATION_CONSENSUS": "check_identification",
    "TAXON_CONFLICT": "check_identification",
}


def required_tools_for_record(record):
    """Return validators applicable to this Darwin Core-style record type."""
    common = ["check_basis_of_record", "check_coordinates", "check_dates"]
    if record.get("basisOfRecord") == "HumanObservation":
        return common + ["check_verifiability", "check_identification"]
    return common
