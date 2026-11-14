"""Post-hoc analysis for the paper: apply the triage policy in code to each model's own issue list.

For every model run in outputs/llm/<model>_<condition>/per_case.csv this script compares
(a) the action the model chose with (b) the action the fixed policy gives for the issues the
model reported. Intervals are 95% percentile cluster-bootstrap intervals over the 19 scenario
families (2,000 draws), as in scripts/analysis.py.

Usage: python3 scripts/policy_in_code.py
"""
import csv
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ecorecord_triage.policy import choose_triage_action  # noqa: E402

DRAWS = 2000
SEED = 20261114


def bootstrap(by_family, draws=DRAWS, seed=SEED):
    rng = random.Random(seed)
    families = sorted(by_family)
    values = []
    for _ in range(draws):
        sample = [rng.choice(families) for _ in families]
        cells = [x for f in sample for x in by_family[f]]
        values.append(100.0 * sum(cells) / len(cells))
    values.sort()
    return values[int(0.025 * draws)], values[int(0.975 * draws) - 1]


def main():
    print("| Run | Model action | Policy in code | Difference [95% CI] | Escalated to expert review |")
    print("|---|---|---|---|---|")
    for run in sorted((ROOT / "outputs" / "llm").glob("*/per_case.csv")):
        rows = list(csv.DictReader(run.open()))
        diff, model_ok, code_ok = {}, 0, 0
        for r in rows:
            exp = r["expected_triage_action"]
            m = r["predicted_triage_action"] == exp
            c = choose_triage_action(json.loads(r["predicted_issue_codes"])) == exp
            model_ok += m
            code_ok += c
            diff.setdefault(r["scenario_family"], []).append(int(c) - int(m))
        n = len(rows)
        lo, hi = bootstrap(diff)
        expert = Counter(r["predicted_triage_action"] for r in rows)["EXPERT_REVIEW"]
        print("| {} | {:.1f} | {:.1f} | {:+.1f} [{:.1f}, {:.1f}] | {:.1f} |".format(
            run.parent.name, 100 * model_ok / n, 100 * code_ok / n,
            100 * (code_ok - model_ok) / n, lo, hi, 100 * expert / n))


if __name__ == "__main__":
    main()
