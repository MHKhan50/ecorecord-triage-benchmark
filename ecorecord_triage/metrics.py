"""Metrics for issue detection, triage action selection and tool coverage."""
from .constants import ISSUE_CODES, required_tools_for_record

# Issues that only exist for HumanObservation records (iNaturalist-style checks).
OBSERVATION_ONLY = {"MEDIA_MISSING", "CAPTIVE_OR_CULTIVATED", "INSUFFICIENT_IDENTIFICATIONS",
                    "LOW_IDENTIFICATION_CONSENSUS", "TAXON_CONFLICT"}


def _safe_div(numerator, denominator):
    return numerator / float(denominator) if denominator else 0.0


def evaluate(cases, predictions):
    by_id = {row["case_id"]: row for row in predictions}
    tp = fp = fn = 0
    per_label_f1 = []
    action_correct = 0
    exact_sets = 0
    clean_total = clean_correct = 0
    false_positive_cases = 0
    tool_tp = tool_fp = tool_fn = 0
    invalid = unsupported_cases = 0
    non_obs = non_obs_wrong_rule = 0

    for case in cases:
        pred = by_id[case["case_id"]]
        expected = set(case["expected_issue_codes"])
        actual = set(pred.get("issue_codes", []))
        tp += len(expected & actual)
        fp += len(actual - expected)
        fn += len(expected - actual)
        exact_sets += int(expected == actual)
        action_correct += int(pred.get("triage_action") == case["expected_triage_action"])
        if not expected:
            clean_total += 1
            clean_correct += int(not actual)
        if not expected and actual:
            false_positive_cases += 1

        invalid += int(pred.get("valid_output", True) is False or pred.get("triage_action") == "INVALID")
        raw = set(pred.get("raw_issue_codes", actual))
        unsupported_cases += int(bool(raw - actual))
        if case["record"].get("basisOfRecord") != "HumanObservation":
            non_obs += 1
            non_obs_wrong_rule += int(bool(raw & OBSERVATION_ONLY))

        expected_tools = set(required_tools_for_record(case["record"]))
        called_tools = set(pred.get("tool_calls", []))
        tool_tp += len(expected_tools & called_tools)
        tool_fp += len(called_tools - expected_tools)
        tool_fn += len(expected_tools - called_tools)

    micro_precision = _safe_div(tp, tp + fp)
    micro_recall = _safe_div(tp, tp + fn)
    micro_f1 = _safe_div(2 * micro_precision * micro_recall, micro_precision + micro_recall)

    for label in ISSUE_CODES:
        ltp = lfp = lfn = 0
        for case in cases:
            expected = label in case["expected_issue_codes"]
            actual = label in by_id[case["case_id"]].get("issue_codes", [])
            ltp += int(expected and actual)
            lfp += int((not expected) and actual)
            lfn += int(expected and (not actual))
        precision = _safe_div(ltp, ltp + lfp)
        recall = _safe_div(ltp, ltp + lfn)
        if ltp + lfp + lfn > 0:
            per_label_f1.append(_safe_div(2 * precision * recall, precision + recall))

    tool_precision = _safe_div(tool_tp, tool_tp + tool_fp)
    tool_recall = _safe_div(tool_tp, tool_tp + tool_fn)
    return {
        "cases": len(cases),
        "issue_micro_precision": round(micro_precision, 6),
        "issue_micro_recall": round(micro_recall, 6),
        "issue_micro_f1": round(micro_f1, 6),
        "issue_macro_f1": round(sum(per_label_f1) / len(per_label_f1), 6) if per_label_f1 else 0.0,
        "exact_issue_set_accuracy": round(_safe_div(exact_sets, len(cases)), 6),
        "triage_action_accuracy": round(_safe_div(action_correct, len(cases)), 6),
        "clean_case_specificity": round(_safe_div(clean_correct, clean_total), 6),
        "false_positive_clean_case_rate": round(_safe_div(false_positive_cases, clean_total), 6),
        "tool_precision": round(tool_precision, 6),
        "tool_recall": round(tool_recall, 6),
        "invalid_output_rate": round(_safe_div(invalid, len(cases)), 6),
        "unsupported_claim_case_rate": round(_safe_div(unsupported_cases, len(cases)), 6),
        "observation_rule_on_non_observation_rate": round(_safe_div(non_obs_wrong_rule, non_obs), 6),
    }
