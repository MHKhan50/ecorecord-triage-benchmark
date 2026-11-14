"""Run benchmark agents and write reproducible outputs."""
import csv
import json
from pathlib import Path

from .metrics import evaluate


def run_benchmark(agent, cases, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    predictions = []
    for case in cases:
        result = agent.run(case["record"])
        predictions.append({
            "case_id": case["case_id"],
            "issue_codes": sorted(set(result.get("issue_codes", []))),
            "triage_action": result.get("triage_action", "INVALID"),
            "tool_calls": list(result.get("tool_calls", [])),
        })

    summary = {
        "benchmark": "EcoRecordTriageBench",
        "version": "0.1.0",
        "agent": getattr(agent, "name", agent.__class__.__name__),
        "synthetic_cases": len(cases),
        "metrics": evaluate(cases, predictions),
        "note": "Synthetic controlled benchmark results; not evidence of field performance.",
    }
    with open(output_dir / "summary.json", "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")

    by_id = {row["case_id"]: row for row in predictions}
    with open(output_dir / "per_case.csv", "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "case_id", "scenario_family", "expected_issue_codes", "predicted_issue_codes",
            "expected_triage_action", "predicted_triage_action", "tool_calls",
        ], lineterminator="\n")
        writer.writeheader()
        for case in cases:
            pred = by_id[case["case_id"]]
            writer.writerow({
                "case_id": case["case_id"],
                "scenario_family": case["scenario_family"],
                "expected_issue_codes": json.dumps(case["expected_issue_codes"]),
                "predicted_issue_codes": json.dumps(pred["issue_codes"]),
                "expected_triage_action": case["expected_triage_action"],
                "predicted_triage_action": pred["triage_action"],
                "tool_calls": json.dumps(pred["tool_calls"]),
            })
    return summary
