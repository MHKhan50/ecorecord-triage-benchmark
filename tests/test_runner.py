import json
import tempfile
import unittest
from pathlib import Path

from ecorecord_triage.agents import RuleAgent
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


if __name__ == "__main__":
    unittest.main()
