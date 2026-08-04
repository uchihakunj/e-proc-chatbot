import unittest
from types import SimpleNamespace

from answer_evidence_guard import assess_final_context, render_evidence_gap_answer


def row(source, text):
    return {"point": SimpleNamespace(payload={"source": source, "text": text})}


class AnswerEvidenceGuardTests(unittest.TestCase):
    def test_excludes_project_brief_for_generic_budget_question(self):
        assessment = assess_final_context(
            "Budget approve ho gaya hai. Ab next step kya hai?", "approval_and_budget",
            [
                row("Précis e-Procurement Project.pdf", "Project 3.0 implementation DPR cost"),
                row("publicProManual.pdf", "Budget availability and procurement approval are recorded."),
            ],
        )
        self.assertTrue(assessment.evidence_present)
        self.assertEqual(len(assessment.usable_results), 1)
        self.assertIn("Précis e-Procurement Project.pdf", assessment.excluded_sources)

    def test_requires_payment_evidence_not_only_generic_security_text(self):
        assessment = assess_final_context(
            "Payment release se pehle kya verify karna hota hai?", "purchase_order",
            [row("Goods Manual.pdf", "Bank Guarantee verification with issuing bank")],
        )
        self.assertFalse(assessment.evidence_present)
        self.assertEqual(assessment.reason_code, "required_evidence_concept_missing")

    def test_accepts_payment_receipt_and_invoice_evidence(self):
        assessment = assess_final_context(
            "Payment release se pehle kya verify karna hota hai?", "purchase_order",
            [row("Goods Manual.pdf", "Verify delivery, acceptance certificate and supplier invoice before payment.")],
        )
        self.assertTrue(assessment.evidence_present)

    def test_keeps_only_chunk_with_payment_artifact(self):
        assessment = assess_final_context(
            "Payment release se pehle kya verify karna hota hai?", "purchase_order",
            [
                row("Goods Manual.pdf", "Bank Guarantee verification with issuing bank."),
                row("Goods Manual.pdf", "Verify delivery, acceptance certificate and supplier invoice before payment."),
            ],
        )
        self.assertTrue(assessment.evidence_present)
        self.assertEqual(len(assessment.usable_results), 1)
        self.assertIn("supplier invoice", assessment.usable_results[0]["point"].payload["text"])

    def test_gap_response_does_not_claim_unavailable_rule(self):
        answer = render_evidence_gap_answer("hinglish", "Office ke liye AC AMC karwana hai.")
        self.assertIn("direct guidance nahi milti", answer)
        self.assertNotIn("reliable section", answer.lower())


if __name__ == "__main__":
    unittest.main()
