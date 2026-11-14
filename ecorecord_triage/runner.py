"""Run benchmark agents and write reproducible outputs.

Model runs append every call to ``calls.jsonl`` as it finishes, so a stopped run
resumes where it stopped when the same command is run again.
"""
import csv
import datetime as dt
import json
import platform
import statistics
import sys
import time
from pathlib import Path

from . import __version__
from .metrics import evaluate

KEEP = ("issue_codes", "raw_issue_codes", "triage_action", "tool_calls", "valid_output")


class CallCache:
    def __init__(self, path, settings):
        self.path = Path(path)
        self.settings = settings
        self.done = {}
        if self.path.exists():
            with self.path.open(encoding="utf-8") as handle:
                for line in handle:
                    if not line.strip():
                        continue
                    row = json.loads(line)
                    if any(row.get(k) != v for k, v in settings.items()):
                        raise ValueError("{0} holds calls made with other settings; use another --output-dir"
                                         .format(self.path))
                    self.done[row["case_id"]] = row["prediction"]

    def add(self, case_id, prediction, raw, seconds):
        row = dict(self.settings)
        row.update({"case_id": case_id, "prediction": prediction, "raw_responses": raw, "seconds": seconds})
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        self.done[case_id] = prediction


def _call(agent, record, case_id, attempts=4):
    for attempt in range(attempts):
        try:
            return agent.run(record)
        except Exception as error:  # timeout, connection reset, model still loading
            if attempt == attempts - 1:
                raise RuntimeError("Model call failed for {0}: {1}. Check that Ollama is running, then run "
                                   "the same command again; finished calls are kept.".format(case_id, error)) from None
            time.sleep(10 * (attempt + 1))


def run_benchmark(agent, cases, output_dir, cache=False, progress=False):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    is_model = getattr(agent, "name", "") == "ollama"
    store = None
    if is_model and cache:
        store = CallCache(output_dir / "calls.jsonl", {
            "model": agent.model, "mode": agent.mode, "temperature": agent.temperature, "seed": agent.seed})
    started = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    runtime = agent.runtime_info() if is_model else {}
    predictions, timed = [], []
    for i, case in enumerate(cases, 1):
        pred = store.done.get(case["case_id"]) if store else None
        if pred is None:
            result = _call(agent, case["record"], case["case_id"]) if is_model else agent.run(case["record"])
            pred = {k: result[k] for k in KEEP if k in result}
            if is_model:
                timed.append(result.get("seconds", 0.0))
                if store:
                    store.add(case["case_id"], pred, result.get("raw_responses"), result.get("seconds"))
        if progress and is_model and (i % 12 == 0 or i == len(cases)):
            left = ""
            if timed:
                left = ", about {0:.0f} min left".format(statistics.mean(timed) * (len(cases) - i) / 60.0)
            print("  {0} {1}: {2}/{3} cases{4}".format(agent.model, agent.mode, i, len(cases), left), flush=True)
        row = {"case_id": case["case_id"]}
        row.update(pred)
        row["issue_codes"] = sorted(set(row.get("issue_codes", [])))
        predictions.append(row)

    environment = {"python": sys.version.split()[0], "platform": platform.platform(), "started_utc": started,
                   "finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    environment.update(runtime)
    if timed:
        environment["mean_seconds_per_new_case"] = round(statistics.mean(timed), 3)
    summary = {
        "benchmark": "EcoRecordTriageBench",
        "version": __version__,
        "agent": getattr(agent, "name", agent.__class__.__name__),
        "model": getattr(agent, "model", None) if is_model else None,
        "mode": getattr(agent, "mode", None) if is_model else None,
        "temperature": getattr(agent, "temperature", None) if is_model else None,
        "seed": getattr(agent, "seed", None) if is_model else None,
        "synthetic_cases": len(cases),
        "environment": environment,
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
            "raw_issue_codes", "expected_triage_action", "predicted_triage_action", "tool_calls",
            "valid_output",
        ], lineterminator="\n")
        writer.writeheader()
        for case in cases:
            pred = by_id[case["case_id"]]
            writer.writerow({
                "case_id": case["case_id"],
                "scenario_family": case["scenario_family"],
                "expected_issue_codes": json.dumps(case["expected_issue_codes"]),
                "predicted_issue_codes": json.dumps(pred["issue_codes"]),
                "raw_issue_codes": json.dumps(pred.get("raw_issue_codes", pred["issue_codes"])),
                "expected_triage_action": case["expected_triage_action"],
                "predicted_triage_action": pred.get("triage_action", "INVALID"),
                "tool_calls": json.dumps(pred.get("tool_calls", [])),
                "valid_output": pred.get("valid_output", True),
            })
    return summary
