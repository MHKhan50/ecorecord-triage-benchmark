import json
import unittest
from unittest.mock import patch

from ecorecord_triage.agents import OllamaAgent, RuleAgent
from ecorecord_triage.constants import ISSUE_CODES, TOOL_NAMES, TRIAGE_ACTIONS
from ecorecord_triage.dataset import build_dataset
from ecorecord_triage.metrics import evaluate
from ecorecord_triage.policy import choose_triage_action


class AgentMetricTests(unittest.TestCase):
    def test_rule_agent_matches_all_controlled_labels(self):
        cases = build_dataset()
        predictions = []
        agent = RuleAgent()
        for case in cases:
            result = agent.run(case["record"])
            self.assertEqual(set(result["issue_codes"]), set(case["expected_issue_codes"]))
            self.assertEqual(result["triage_action"], case["expected_triage_action"])
            predictions.append({"case_id": case["case_id"], **result})
        metrics = evaluate(cases, predictions)
        self.assertEqual(metrics["issue_micro_f1"], 1.0)
        self.assertEqual(metrics["triage_action_accuracy"], 1.0)
        self.assertEqual(metrics["tool_precision"], 1.0)
        self.assertEqual(metrics["tool_recall"], 1.0)

    def test_rule_agent_skips_observation_only_tools_for_specimens(self):
        specimen = next(c["record"] for c in build_dataset() if c["scenario_family"] == "specimen_no_media_no_ids_control")
        result = RuleAgent().run(specimen)
        self.assertNotIn("check_verifiability", result["tool_calls"])
        self.assertNotIn("check_identification", result["tool_calls"])

    def test_policy_precedence(self):
        self.assertEqual(choose_triage_action(["TAXON_CONFLICT", "MEDIA_MISSING"]), "EXPERT_REVIEW")
        self.assertEqual(choose_triage_action(["MEDIA_MISSING", "LOW_IDENTIFICATION_CONSENSUS"]), "REQUEST_CORRECTION")
        self.assertEqual(choose_triage_action(["LOW_IDENTIFICATION_CONSENSUS"]), "COMMUNITY_IDENTIFICATION")

    def test_ollama_parser_filters_unknown_values(self):
        agent = OllamaAgent()
        calls = [
            {"tool_calls": ["check_dates", "made_up_tool"]},
            {"issue_codes": ["RECORDED_DATE_INVALID", "MADE_UP"], "triage_action": "REQUEST_CORRECTION"},
        ]
        def fake_generate(prompt, schema):
            return calls.pop(0)
        record = build_dataset()[36]["record"]
        with patch.object(agent, "_generate", side_effect=fake_generate):
            result = agent.run(record)
        self.assertEqual(result["tool_calls"], ["check_dates"])
        self.assertEqual(result["issue_codes"], ["RECORDED_DATE_INVALID"])
        self.assertEqual(result["triage_action"], "REQUEST_CORRECTION")

    def test_schema_vocabularies_are_consistent(self):
        self.assertEqual(len(TOOL_NAMES), len(set(TOOL_NAMES)))
        self.assertTrue(ISSUE_CODES)
        self.assertTrue(TRIAGE_ACTIONS)


if __name__ == "__main__":
    unittest.main()
