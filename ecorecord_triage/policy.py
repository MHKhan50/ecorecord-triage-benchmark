"""Deterministic mapping from issue sets to curator-facing triage actions."""
from .constants import IDENTIFICATION_ISSUES, METADATA_ISSUES


def choose_triage_action(issue_codes):
    issues = set(issue_codes)
    if "TAXON_CONFLICT" in issues:
        return "EXPERT_REVIEW"
    if issues.intersection(METADATA_ISSUES):
        return "REQUEST_CORRECTION"
    if issues.intersection(IDENTIFICATION_ISSUES):
        return "COMMUNITY_IDENTIFICATION"
    return "READY_FOR_RESEARCH_PIPELINE"
