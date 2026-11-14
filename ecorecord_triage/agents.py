"""Reference and optional local Ollama agents."""
import json
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


class OllamaAgent:
    """Two-stage local agent: plan validator calls, execute tools, then triage.

    The model never writes to the source record. All validation tools are local,
    deterministic and read-only. This is a benchmark adapter, not a production
    biodiversity decision system.
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
                 seed=20261114, temperature=0.0, timeout=180):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.seed = seed
        self.temperature = temperature
        self.timeout = timeout

    def _generate(self, prompt, schema):
        body = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": schema,
            "options": {"temperature": self.temperature, "seed": self.seed},
        }
        request = urllib.request.Request(
            self.base_url + "/api/generate",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        raw = payload.get("response", "")
        try:
            parsed = json.loads(raw)
        except (TypeError, ValueError):
            parsed = {}
        return parsed if isinstance(parsed, dict) else {}

    def run(self, record):
        plan_prompt = (
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
        plan = self._generate(plan_prompt, self.PLAN_SCHEMA)
        requested = plan.get("tool_calls", [])
        if not isinstance(requested, list):
            requested = []
        tool_calls = []
        for name in requested:
            if name in TOOL_NAMES and name not in tool_calls:
                tool_calls.append(name)

        tool_outputs = {}
        for name in tool_calls:
            tool_outputs[name] = run_tool(name, record)

        final_prompt = (
            "Triage this biodiversity record using ONLY the supplied validator outputs. "
            "Do not add issues that the tools did not report. Choose the action by this policy: "
            "TAXON_CONFLICT -> EXPERT_REVIEW; any metadata issue -> REQUEST_CORRECTION; "
            "otherwise any identification issue -> COMMUNITY_IDENTIFICATION; "
            "otherwise READY_FOR_RESEARCH_PIPELINE. Return exactly issue_codes and triage_action.\n"
            "Allowed issue codes: " + ", ".join(ISSUE_CODES) + "\n"
            "Allowed actions: " + ", ".join(TRIAGE_ACTIONS) + "\n"
            "Record: " + json.dumps(record, sort_keys=True) + "\n"
            "Executed tool outputs: " + json.dumps(tool_outputs, sort_keys=True)
        )
        final = self._generate(final_prompt, self.FINAL_SCHEMA)
        predicted_issues = final.get("issue_codes", [])
        if not isinstance(predicted_issues, list):
            predicted_issues = []
        tool_reported_issues = {
            issue for values in tool_outputs.values() for issue in values
        }
        predicted_issues = sorted(set(
            x for x in predicted_issues if x in ISSUE_CODES and x in tool_reported_issues
        ))
        action = final.get("triage_action", "INVALID")
        if action not in TRIAGE_ACTIONS:
            action = "INVALID"
        return {
            "issue_codes": predicted_issues,
            "triage_action": action,
            "tool_calls": tool_calls,
            "tool_outputs": tool_outputs,
        }
