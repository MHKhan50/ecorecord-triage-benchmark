"""Analyse finished EcoRecordTriageBench model runs.

Reads every outputs/llm/<model>_<mode>/per_case.csv, recomputes metrics with the
package's scorer and adds 95% cluster-bootstrap intervals that resample the 19
scenario families (the six variants of a family are near copies, so the family is
the unit). Paired differences between conditions of the same model use the same
draws. Writes results/tables.md, results/results.json and, if matplotlib is
installed, results/fig_conditions.png.
"""
import argparse
import csv
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ecorecord_triage.dataset import load_dataset  # noqa: E402
from ecorecord_triage.metrics import evaluate  # noqa: E402

METRICS = [
    ("exact_issue_set_accuracy", "Exact issue set"),
    ("triage_action_accuracy", "Triage action"),
    ("issue_micro_precision", "Issue precision"),
    ("issue_micro_recall", "Issue recall"),
    ("clean_case_specificity", "Clean records left clean"),
    ("observation_rule_on_non_observation_rate", "Observation rule on specimens"),
    ("unsupported_claim_case_rate", "Unsupported issue claimed"),
    ("tool_recall", "Tool recall"),
    ("tool_precision", "Tool precision"),
    ("invalid_output_rate", "Invalid output"),
]
MODES = ["all_tools", "selective", "no_tools"]
MODE_LABEL = {"all_tools": "all tools run", "selective": "model picks tools", "no_tools": "no tools"}
COLOURS = {"all_tools": "#1F4E9C", "selective": "#E3A800", "no_tools": "#C8102E"}


def load_run(directory):
    preds = []
    with (directory / "per_case.csv").open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            preds.append({
                "case_id": row["case_id"],
                "issue_codes": json.loads(row["predicted_issue_codes"]),
                "raw_issue_codes": json.loads(row.get("raw_issue_codes") or row["predicted_issue_codes"]),
                "triage_action": row["predicted_triage_action"],
                "tool_calls": json.loads(row["tool_calls"]),
                "valid_output": row.get("valid_output", "True") != "False",
            })
    return json.loads((directory / "summary.json").read_text(encoding="utf-8")), preds


def score(cases, preds, families=None):
    if families is None:
        return evaluate(cases, preds)
    by_fam = defaultdict(list)
    for c in cases:
        by_fam[c["scenario_family"]].append(c)
    pmap = {p["case_id"]: p for p in preds}
    chosen, cp = [], []
    for k, fam in enumerate(families):
        for c in by_fam[fam]:
            new_id = "{0}#{1}".format(c["case_id"], k)
            chosen.append(dict(c, case_id=new_id))
            cp.append(dict(pmap[c["case_id"]], case_id=new_id))
    return evaluate(chosen, cp)


def interval(values):
    v = sorted(values)
    return [v[int(0.025 * (len(v) - 1))], v[int(0.975 * (len(v) - 1))]]


def pct(x):
    return "{0:.1f}".format(100 * x)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20261114)
    args = ap.parse_args(argv)
    cases = load_dataset(ROOT / "data" / "scenarios.jsonl")
    families = sorted({c["scenario_family"] for c in cases})
    runs = {}
    for d in sorted((ROOT / "outputs" / "llm").glob("*")):
        if not (d / "per_case.csv").exists():
            continue
        summary, preds = load_run(d)
        if summary["synthetic_cases"] != len(cases):
            print("skipping {0}: limited run".format(d.name))
            continue
        runs[(summary["model"], summary["mode"])] = (summary, preds)
    if not runs:
        raise SystemExit("No complete model runs under outputs/llm")
    models = sorted({m for m, _ in runs})
    order = [(m, mode) for m in models for mode in MODES if (m, mode) in runs]

    rng = random.Random(args.seed)
    draws = [[rng.choice(families) for _ in families] for _ in range(args.draws)]
    point = {k: score(cases, runs[k][1]) for k in order}
    boot = {k: defaultdict(list) for k in order}
    for fams in draws:
        for k in order:
            m = score(cases, runs[k][1], fams)
            for key, _ in METRICS:
                boot[k][key].append(m[key])
    ci = {k: {key: interval(boot[k][key]) for key, _ in METRICS} for k in order}

    paired = []
    for m in models:
        for a, b in [("selective", "all_tools"), ("no_tools", "all_tools")]:
            if (m, a) in runs and (m, b) in runs:
                for key, label in METRICS[:6]:
                    diffs = [x - y for x, y in zip(boot[(m, a)][key], boot[(m, b)][key])]
                    paired.append({"model": m, "comparison": "{0} minus {1}".format(a, b), "metric": key,
                                   "label": label, "difference": point[(m, a)][key] - point[(m, b)][key],
                                   "ci": interval(diffs)})

    fam_acc = {}
    by_id = {c["case_id"]: c for c in cases}
    for k in order:
        acc = defaultdict(lambda: [0, 0])
        for p in runs[k][1]:
            c = by_id[p["case_id"]]
            ok = set(p["issue_codes"]) == set(c["expected_issue_codes"]) and p["triage_action"] == c["expected_triage_action"]
            acc[c["scenario_family"]][0] += ok
            acc[c["scenario_family"]][1] += 1
        fam_acc[k] = {f: acc[f][0] / acc[f][1] for f in families}

    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    name = {k: "{0} ({1})".format(k[0], MODE_LABEL[k[1]]) for k in order}
    results = {"bootstrap": {"draws": args.draws, "unit": "scenario family (19)"},
               "configs": {name[k]: {"model": k[0], "mode": k[1], "environment": runs[k][0].get("environment"),
                                     "metrics": point[k], "ci95": ci[k], "family_accuracy": fam_acc[k]}
                           for k in order},
               "paired": paired}
    (out / "results.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    L = ["# EcoRecordTriageBench results", "",
         "114 synthetic records (19 scenario families x 6 variants). Brackets: 95% cluster-bootstrap intervals "
         "({0} draws over the 19 families). Values are percentages.".format(args.draws), "",
         "| Metric | " + " | ".join(name[k] for k in order) + " |", "|" + "---|" * (len(order) + 1)]
    for key, label in METRICS:
        L.append("| {0} | {1} |".format(label, " | ".join(
            "{0} [{1}, {2}]".format(pct(point[k][key]), pct(ci[k][key][0]), pct(ci[k][key][1])) for k in order)))
    L += ["", "Tool metrics are only meaningful when the model picks tools. 'Observation rule on specimens' is the "
          "share of non-HumanObservation records for which the model's own list (before filtering) contained a "
          "media, captive or identification issue.", "",
          "## Paired differences between conditions (same model, same draws)", "",
          "| Model | Comparison | Metric | Difference [95% CI] |", "|---|---|---|---|"]
    for r in paired:
        L.append("| {0} | {1} | {2} | {3} [{4}, {5}] |".format(r["model"], r["comparison"], r["label"],
                                                              pct(r["difference"]), pct(r["ci"][0]), pct(r["ci"][1])))
    L += ["", "## Fully correct (issues and action) by scenario family", "",
          "| Family | " + " | ".join(name[k] for k in order) + " |", "|" + "---|" * (len(order) + 1)]
    for f in families:
        L.append("| {0} | {1} |".format(f, " | ".join(pct(fam_acc[k][f]) for k in order)))
    L += ["", "## Runs", ""]
    for k in order:
        env = runs[k][0].get("environment", {})
        L.append("- **{0}:** temperature {1}, seed {2}; Ollama {3}; model digest {4}; {5}".format(
            name[k], runs[k][0].get("temperature"), runs[k][0].get("seed"), env.get("ollama_version"),
            (env.get("model_digest") or "n/a")[:12], env.get("platform")))
    (out / "tables.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed: skipping the chart")
        return
    keys = ["exact_issue_set_accuracy", "triage_action_accuracy", "issue_micro_recall", "clean_case_specificity"]
    labels = {k: l for k, l in METRICS}
    fig, axes = plt.subplots(1, len(models), figsize=(5.2 * len(models), 4.6), sharey=True, squeeze=False)
    for ax, m in zip(axes[0], models):
        present = [mode for mode in MODES if (m, mode) in runs]
        w = 0.8 / len(present)
        for i, mode in enumerate(present):
            k = (m, mode)
            xs = [j + (i - (len(present) - 1) / 2) * w for j in range(len(keys))]
            ys = [100 * point[k][x] for x in keys]
            lo = [100 * (point[k][x] - ci[k][x][0]) for x in keys]
            hi = [100 * (ci[k][x][1] - point[k][x]) for x in keys]
            ax.bar(xs, ys, w * 0.92, color=COLOURS[mode], label=MODE_LABEL[mode], edgecolor="white",
                   yerr=[lo, hi], error_kw={"elinewidth": 1, "capsize": 2, "ecolor": "#555555"})
        ax.set_xticks(range(len(keys)))
        ax.set_xticklabels([labels[x].replace(" ", "\n", 1) for x in keys], fontsize=8.5)
        ax.set_title(m, fontsize=10, loc="left")
        ax.set_ylim(0, 105)
        ax.grid(axis="y", color="#e5e5e5")
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    axes[0][0].set_ylabel("%")
    h, l = axes[0][0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, frameon=False, fontsize=9)
    fig.suptitle("EcoRecordTriageBench: 114 synthetic occurrence records", x=0.02, ha="left", fontsize=11)
    fig.tight_layout(rect=(0, 0.08, 1, 0.94))
    fig.savefig(out / "fig_conditions.png", dpi=200)
    print("Chart: results/fig_conditions.png")


if __name__ == "__main__":
    main()
