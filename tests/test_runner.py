import json
import tempfile
import unittest
from pathlib import Path

from unittest.mock import patch

from ecorecord_triage.agents import OllamaAgent, RuleAgent
from ecorecord_triage.dataset import build_dataset
from ecorecord_triage.runner import run_benchmark


class RunnerTests(unittest.TestCase):
    def test_runner_writes_summary_and_csv(self):
        with tempfile.TemporaryDirectory() as temp:
            summary = run_benchmark(RuleAgent(), build_dataset()[4:10], temp)
            self.assertEqual(summary["synthetic_cases"], 6)
            self.assertTrue((Path(temp) / "summary.json").exists())
            self.assertTrue((Path(temp) / "per_case.csv").exists())
            loaded = json.loads((Path(temp) / "summary.json").read_text())
            self.assertEqual(loaded["metrics"]["issue_micro_f1"], 1.0)


    def test_model_run_resumes_from_call_cache(self):
        cases = build_dataset()[:12]
        rule = RuleAgent()
        calls, down = [], {"ERT-0008"}

        def fake_run(agent, record):
            calls.append(record["occurrenceID"])
            if record["occurrenceID"].endswith("0008") and down:
                raise ConnectionError("simulated drop")
            out = rule.run(record)
            out.update(raw_issue_codes=out["issue_codes"], valid_output=True, raw_responses=["{}"], seconds=0.01)
            return out

        with tempfile.TemporaryDirectory() as temp, \
                patch.object(OllamaAgent, "run", fake_run), \
                patch.object(OllamaAgent, "runtime_info", lambda a: {}), \
                patch("ecorecord_triage.runner.time.sleep", lambda s: None):
            with self.assertRaises(RuntimeError):
                run_benchmark(OllamaAgent(), cases, temp, cache=True)
            self.assertEqual(len((Path(temp) / "calls.jsonl").read_text().splitlines()), 7)
            calls.clear()
            down.clear()
            summary = run_benchmark(OllamaAgent(), cases, temp, cache=True)
        self.assertEqual(len(calls), 5)  # only the cases that were not finished
        self.assertEqual(summary["metrics"]["exact_issue_set_accuracy"], 1.0)


if __name__ == "__main__":
    unittest.main()
