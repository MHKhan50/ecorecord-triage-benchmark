"""Deterministic, inspectable record-quality tools used by benchmark agents.

These checks operationalise a deliberately narrow subset of GBIF and iNaturalist
metadata-quality conventions. They are not a complete implementation of either
platform's production quality systems.
"""
from datetime import date

from .constants import BASIS_OF_RECORD_VALUES


def check_basis_of_record(record):
    value = record.get("basisOfRecord")
    if value not in BASIS_OF_RECORD_VALUES:
        return ["BASIS_OF_RECORD_INVALID"]
    return []


def check_coordinates(record):
    lat = record.get("decimalLatitude")
    lon = record.get("decimalLongitude")
    if lat is None or lon is None or lat == "" or lon == "":
        return ["COORDINATES_MISSING"]
    try:
        lat = float(lat)
        lon = float(lon)
    except (TypeError, ValueError):
        return ["COORDINATES_INVALID"]
    issues = []
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        issues.append("COORDINATE_OUT_OF_RANGE")
    if lat == 0.0 and lon == 0.0:
        issues.append("ZERO_COORDINATE")
    return issues


def check_dates(record):
    event_date = record.get("eventDate")
    if not event_date:
        return ["RECORDED_DATE_MISSING"]
    try:
        parsed = date.fromisoformat(str(event_date))
    except (TypeError, ValueError):
        return ["RECORDED_DATE_INVALID"]

    issues = []
    reference_date = record.get("referenceDate", "2026-01-01")
    try:
        reference = date.fromisoformat(str(reference_date))
    except (TypeError, ValueError):
        reference = date(2026, 1, 1)
    if parsed > reference:
        issues.append("RECORDED_DATE_FUTURE")

    supplied_parts = (record.get("year"), record.get("month"), record.get("day"))
    if all(part is not None for part in supplied_parts):
        try:
            parts = tuple(int(part) for part in supplied_parts)
        except (TypeError, ValueError):
            issues.append("RECORDED_DATE_MISMATCH")
        else:
            if parts != (parsed.year, parsed.month, parsed.day):
                issues.append("RECORDED_DATE_MISMATCH")
    return issues


def check_verifiability(record):
    """Apply iNaturalist-like media/wildness checks to human observations only."""
    if record.get("basisOfRecord") != "HumanObservation":
        return []
    issues = []
    if record.get("hasMedia") is not True:
        issues.append("MEDIA_MISSING")
    if record.get("isCaptiveOrCultivated") is True:
        issues.append("CAPTIVE_OR_CULTIVATED")
    return issues


def check_identification(record):
    """A simplified consensus proxy; not a reimplementation of iNaturalist's algorithm."""
    if record.get("basisOfRecord") != "HumanObservation":
        return []
    issues = []
    try:
        total = int(record.get("identificationCount", 0))
        agreeing = int(record.get("agreementCount", 0))
    except (TypeError, ValueError):
        return ["INSUFFICIENT_IDENTIFICATIONS"]

    if total < 2:
        issues.append("INSUFFICIENT_IDENTIFICATIONS")
    elif total > 0 and (agreeing / float(total)) <= (2.0 / 3.0):
        issues.append("LOW_IDENTIFICATION_CONSENSUS")

    observation_taxon = record.get("observationTaxon")
    community_taxon = record.get("communityTaxon")
    if observation_taxon and community_taxon and observation_taxon != community_taxon:
        issues.append("TAXON_CONFLICT")
    return issues


TOOL_FUNCTIONS = {
    "check_basis_of_record": check_basis_of_record,
    "check_coordinates": check_coordinates,
    "check_dates": check_dates,
    "check_verifiability": check_verifiability,
    "check_identification": check_identification,
}


def run_tool(name, record):
    if name not in TOOL_FUNCTIONS:
        raise ValueError("Unknown tool: {0}".format(name))
    return TOOL_FUNCTIONS[name](record)
