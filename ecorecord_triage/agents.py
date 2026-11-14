"""Reference and optional local Ollama agents."""
import json
import time
import urllib.request

from .constants import ISSUE_CODES, TOOL_NAMES, TRIAGE_ACTIONS, required_tools_for_record
from .policy import choose_triage_action
from .validators import run_tool


class RuleAgent:
    """Reference baseline: run every deterministic validator and apply triage policy."""
    name = "rules"

    def run(self, record):
        tool_outputs = {}
        issues = []
        selected_tools = required_tools_for_record(record)
        for tool_name in selected_tools:
            result = run_tool(tool_name, record)
            tool_outputs[tool_name] = result
            issues.extend(result)
        issues = sorted(set(issues))
        return {
            "issue_codes": issues,
            "triage_action": choose_triage_action(issues),
            "tool_calls": list(selected_tools),
            "tool_outputs": tool_outputs,
        }


ISSUE_DEFINITIONS = {
    "BASIS_OF_RECORD_INVALID": "basisOfRecord is not a Darwin Core basis-of-record value",
    "COORDINATES_MISSING": "decimalLatitude or decimalLongitude is missing",
    "COORDINATES_INVALID": "a coordinate is not a number",
    "COORDINATE_OUT_OF_RANGE": "latitude outside -90..90 or longitude outside -180..180",
    "ZERO_COORDINATE": "latitude and longitude are both exactly 0",
    "RECORDED_DATE_MISSING": "eventDate is missing",
    "RECORDED_DATE_INVALID": "eventDate is not a real ISO date",
    "RECORDED_DATE_FUTURE": "eventDate is after referenceDate",
    "RECORDED_DATE_MISMATCH": "year, month or day disagree with eventDate",
    "MEDIA_MISSING": "HumanObservation without media (hasMedia is not true)",
    "CAPTIVE_OR_CULTIVATED": "HumanObservation of a captive or cultivated organism",
    "INSUFFICIENT_IDENTIFICATIONS": "HumanObservation with fewer than 2 identifications",
    "LOW_IDENTIFICATION_CONSENSUS": "HumanObservation where agreeing identifications are 2/3 or less of the total",
    "TAXON_CONFLICT": "HumanObservation whose observationTaxon differs from communityTaxon",
}
POLICY_TEXT = (
    "Choose the action by this policy: TAXON_CONFLICT -> EXPERT_REVIEW; any metadata issue -> "
    "REQUEST_CORRECTION; otherwise any identification issue -> COMMUNITY_IDENTIFICATION; "
    "otherwise READY_FOR_RESEARCH_PIPELINE."
)
MAX_OUTPUT_TOKENS = 256  # a complete answer needs well under 100; the cap stops runaway generations
MODES = ("selective", "all_tools", "no_tools")


class OllamaAgent:
    """Local model agent in one of three conditions.

    * ``selective``: the model chooses which validators to run, the chosen tools run
      locally, and the model returns issues and an action from their outputs.
    * ``all_tools``: every validator applicable to the record type runs (the oracle
      plan), and the model returns issues and an action from their outputs.
    * ``no_tools``: the model reads the record and the issue definitions and returns
      issues and an action without any tool.

    With tools, reported issues are restricted to issues the tools returned; the
    model's unfiltered list is kept as ``raw_issue_codes`` so unsupported claims can
    be counted. The model never writes to the source record.
    """
    name = "ollama"

    PLAN_SCHEMA = {
        "type": "object",
        "properties": {
            "tool_calls": {
                "type": "array",
                "items": {"type": "string", "enum": TOOL_NAMES},
                "uniqueItems": True,
            }
        },
        "required": ["tool_calls"],
        "additionalProperties": False,
    }
    FINAL_SCHEMA = {
        "type": "object",
        "properties": {
            "issue_codes": {
                "type": "array",
                "items": {"type": "string", "enum": ISSUE_CODES},
                "uniqueItems": True,
            },
            "triage_action": {"type": "string", "enum": TRIAGE_ACTIONS},
        },
        "required": ["issue_codes", "triage_action"],
        "additionalProperties": False,
    }

    def __init__(self, model="qwen2.5:3b", base_url="http://localhost:11434",
                 seed=20261114, temperature=0.0, timeout=180, mode="selective"):
        if mode not in MODES:
            raise ValueError("mode must be one of {0}".format(", ".join(MODES)))
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.seed = seed
        self.temperature = temperature
        self.timeout = timeout
        self.mode = mode

    def _generate(self, prompt, schema):
        """Return (parsed dict or None, raw text, seconds)."""
        body = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": schema,
            "options": {"temperature": self.temperature, "seed": self.seed,
                        "num_predict": MAX_OUTPUT_TOKENS},
        }
        request = urllib.request.Request(
            self.base_url + "/api/generate",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        started = time.time()
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        raw = payload.get("response", "")
        try:
            parsed = json.loads(raw)
        except (TypeError, ValueError):
            parsed = None
        return (parsed if isinstance(parsed, dict) else None), raw, round(time.time() - started, 3)

    def runtime_info(self):
        """Ollama version and model digest for the run record. Best effort only."""
        info = {"ollama_version": None, "model_digest": None}
        try:
            with urllib.request.urlopen(self.base_url + "/api/version", timeout=10) as response:
                info["ollama_version"] = json.loads(response.read().decode("utf-8")).get("version")
            with urllib.request.urlopen(self.base_url + "/api/tags", timeout=10) as response:
                for item in json.loads(response.read().decode("utf-8")).get("models", []):
                    if self.model in (item.get("name"), item.get("model")):
                        info["model_digest"] = item.get("digest")
        except Exception:  # the run itself reports connection problems
            pass
        return info

    def plan_prompt(self, record):
        return (
            "You are a biodiversity occurrence-record quality triage agent. "
            "Choose every local read-only validator needed to assess this record. "
            "Do not infer issue labels yet. Return JSON with tool_calls only.\n"
            "Available tools: check_basis_of_record (validate the Darwin Core basis value), "
            "check_coordinates (missing, non-numeric, out-of-range and zero coordinates), "
            "check_dates (ISO date, future date and date-part consistency), "
            "check_verifiability (media and captive/cultivated checks), "
            "check_identification (identification count, simplified agreement and taxon conflict). "
            "The last two apply only to HumanObservation records; the first three apply to all record types.\n"
            "Record: " + json.dumps(record, sort_keys=True)
        )

    def final_prompt(self, record, tool_outputs):
        return (
            "Triage this biodiversity record using ONLY the supplied validator outputs. "
            "Do not add issues that the tools did not report. " + POLICY_TEXT + " "
            "Return exactly issue_codes and triage_action.\n"
            "Allowed issue codes: " + ", ".join(ISSUE_CODES) + "\n"
            "Allowed actions: " + ", ".join(TRIAGE_ACTIONS) + "\n"
            "Record: " + json.dumps(record, sort_keys=True) + "\n"
            "Executed tool outputs: " + json.dumps(tool_outputs, sort_keys=True)
        )

    def no_tool_prompt(self, record):
        definitions = "\n".join("- {0}: {1}".format(k, v) for k, v in ISSUE_DEFINITIONS.items())
        return (
            "You are a biodiversity occurrence-record quality triage agent. Check this record "
            "yourself and list every issue code that applies, or an empty list if none apply. "
            "Media, captive/cultivated and identification checks apply only to HumanObservation "
            "records; preserved specimens and other record types are not checked for them.\n"
            "Issue codes:\n" + definitions + "\n" + POLICY_TEXT + " "
            "Return exactly issue_codes and triage_action.\n"
            "Allowed actions: " + ", ".join(TRIAGE_ACTIONS) + "\n"
            "Record: " + json.dumps(record, sort_keys=True)
        )

    def run(self, record):
        raws, seconds, valid = [], 0.0, True
        tool_calls = []
        if self.mode == "selective":
            plan, raw, sec = self._generate(self.plan_prompt(record), self.PLAN_SCHEMA)
            raws.append(raw)
            seconds += sec
            requested = plan.get("tool_calls") if plan else None
            if not isinstance(requested, list):
                requested, valid = [], False
            for name in requested:
                if name in TOOL_NAMES and name not in tool_calls:
                    tool_calls.append(name)
        elif self.mode == "all_tools":
            tool_calls = list(required_tools_for_record(record))

        tool_outputs = {name: run_tool(name, record) for name in tool_calls}
        if self.mode == "no_tools":
            prompt = self.no_tool_prompt(record)
        else:
            prompt = self.final_prompt(record, tool_outputs)
        final, raw, sec = self._generate(prompt, self.FINAL_SCHEMA)
        raws.append(raw)
        seconds += sec
        if final is None:
            valid = False
            final = {}

        raw_issues = final.get("issue_codes", [])
        if not isinstance(raw_issues, list):
            raw_issues, valid = [], False
        raw_issues = sorted(set(x for x in raw_issues if x in ISSUE_CODES))
        if self.mode == "no_tools":
            issues = raw_issues
        else:
            reported = {issue for values in tool_outputs.values() for issue in values}
            issues = [x for x in raw_issues if x in reported]
        action = final.get("triage_action", "INVALID")
        if action not in TRIAGE_ACTIONS:
            action, valid = "INVALID", False
        return {
            "issue_codes": issues,
            "raw_issue_codes": raw_issues,
            "triage_action": action,
            "tool_calls": tool_calls,
            "tool_outputs": tool_outputs,
            "valid_output": valid,
            "raw_responses": raws,
            "seconds": round(seconds, 3),
        }
