"""Bounded checks against real weights and a separate set of synthetic requests."""
import json
import socket
import unittest
from pathlib import Path
from unittest.mock import patch
from engine import LocalEncoder, InputError, analyze, parse_scope

ROOT = Path(__file__).resolve().parent

class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.encoder = LocalEncoder()
        cls.example = json.loads((ROOT / "examples.json").read_text())

    def check_match(self, request, expected_id):
        result = analyze(self.encoder, self.example["brief"], request)
        self.assertEqual(result["findings"][0]["matches"][0]["id"], expected_id)

    def test_paraphrased_contact_form(self):
        self.check_match("The enquiry form should deliver messages to our email.", "B02")

    def test_translation_exclusion(self):
        self.check_match("We also need the pages translated into Spanish.", "B05")

    def test_payment_exclusion(self):
        self.check_match("Please add online checkout so customers can pay on the site.", "B04")

    def test_each_quote_is_an_exact_input_line(self):
        result = analyze(self.encoder, self.example["brief"], self.example["requests"])
        source_lines = set(self.example["brief"].splitlines())
        for finding in result["findings"]:
            for match in finding["matches"]:
                self.assertIn(match["source"], source_lines)

    def test_unknown_request_is_never_auto_approved(self):
        result = analyze(self.encoder, self.example["brief"], "Can you book flights for our holiday?")
        self.assertEqual(result["findings"][0]["status"], "review")

    def test_negation_does_not_produce_a_contract_verdict(self):
        result = analyze(self.encoder, self.example["brief"], "Do not add any online payments.")
        self.assertNotIn(result["findings"][0]["status"], ["in_scope", "out_of_scope", "approved"])
        self.assertIn("not confidence", result["limitations"])

    def test_offline_analysis_does_not_open_network_sockets(self):
        with patch.object(socket.socket, "connect", side_effect=AssertionError("Network forbidden")):
            result = analyze(self.encoder, self.example["brief"], "Add an online checkout.")
        self.assertEqual(result["network_requests_during_analysis"], 0)

    def test_oversized_token_input_is_rejected_not_truncated(self):
        with self.assertRaises(InputError):
            analyze(self.encoder, "[IN] " + "photos "*260, "Photos please")

    def test_empty_and_invalid_inputs(self):
        for value in ["", "   ", None, 123]:
            with self.assertRaises(InputError):
                parse_scope(value)

    def test_unlabelled_clause_is_unspecified(self):
        self.assertEqual(parse_scope("No payment integration included")[0]["kind"], "unspecified")

if __name__ == "__main__":
    unittest.main()
