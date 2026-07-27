import unittest

from run_retrieval_regression import evaluate_sources


CASE = {
    "id": "RR-test",
    "query": "computer kharidne ka process batao",
    "required_sources": ["store purchase rule cg", "publicpromanual-1755343081262-715558279"],
    "forbidden_source_terms": ["medical", "forensic"],
}


class RetrievalRegressionTests(unittest.TestCase):
    def test_accepts_the_required_planning_sources(self):
        result = evaluate_sources(CASE, [
            "store purchase rule cg.pdf",
            "publicProManual-1755343081262-715558279.pdf",
        ])
        self.assertTrue(result["passed"])

    def test_rejects_a_forbidden_source_even_when_required_sources_exist(self):
        result = evaluate_sources(CASE, [
            "store purchase rule cg.pdf",
            "publicProManual-1755343081262-715558279.pdf",
            "Medical_Device_Procurement_Manual.pdf",
        ])
        self.assertFalse(result["passed"])
        self.assertEqual(result["forbidden_sources"], ["medical_device_procurement_manual"])

    def test_rejects_missing_required_source(self):
        result = evaluate_sources(CASE, ["store purchase rule cg.pdf"])
        self.assertFalse(result["passed"])
        self.assertEqual(result["missing_required_sources"], ["publicpromanual-1755343081262-715558279"])

    def test_rejects_vendor_workflow_terms_in_buyer_answer(self):
        case = {**CASE, "forbidden_answer_terms": ["vendor registration", "valid dsc"]}
        result = evaluate_sources(
            case,
            ["store purchase rule cg.pdf", "publicProManual-1755343081262-715558279.pdf"],
            "Pehle vendor registration karein aur valid DSC use karein.",
        )
        self.assertFalse(result["passed"])
        self.assertEqual(result["forbidden_answer_terms"], ["vendor registration", "valid dsc"])


if __name__ == "__main__":
    unittest.main()
