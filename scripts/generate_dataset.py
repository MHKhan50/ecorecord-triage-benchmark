from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ecorecord_triage.dataset import write_dataset

count = write_dataset(ROOT / "data" / "scenarios.jsonl")
print("Wrote {0} synthetic cases to data/scenarios.jsonl".format(count))
