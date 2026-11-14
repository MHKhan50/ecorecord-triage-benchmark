"""Command-line entry point."""
import argparse
from pathlib import Path

from .agents import MODES, OllamaAgent, RuleAgent
from .dataset import load_dataset
from .runner import run_benchmark


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run EcoRecordTriageBench")
    parser.add_argument("--agent", choices=["rules", "ollama"], default="rules")
    parser.add_argument("--model", default="qwen2.5:3b")
    parser.add_argument("--mode", choices=MODES, default="selective",
                        help="selective: model picks tools; all_tools: every applicable tool runs; "
                             "no_tools: model judges the record without tools")
    parser.add_argument("--base-url", default="http://localhost:11434")
    parser.add_argument("--seed", type=int, default=20261114)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--dataset", default="data/scenarios.jsonl")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args(argv)

    cases = load_dataset(args.dataset)
    if args.limit > 0:
        cases = cases[:args.limit]
    if args.agent == "rules":
        agent = RuleAgent()
        output_dir = args.output_dir or "outputs/run"
    else:
        agent = OllamaAgent(model=args.model, base_url=args.base_url, seed=args.seed,
                            temperature=args.temperature, mode=args.mode)
        output_dir = args.output_dir or "outputs/llm/{0}_{1}".format(
            args.model.replace(":", "-").replace("/", "-"), args.mode)
    args.output_dir = output_dir
    summary = run_benchmark(agent, cases, output_dir, cache=args.agent == "ollama", progress=True)
    print("Agent: {0}".format(summary["agent"]))
    print("Cases: {0}".format(summary["synthetic_cases"]))
    print("Metrics:")
    for key, value in summary["metrics"].items():
        print("  {0}: {1}".format(key, value))
    print("Summary: {0}".format(Path(args.output_dir) / "summary.json"))
    print("Per-case CSV: {0}".format(Path(args.output_dir) / "per_case.csv"))


if __name__ == "__main__":
    main()
