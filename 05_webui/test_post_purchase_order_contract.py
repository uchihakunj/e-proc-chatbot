import unittest

from fine_intent_policy import (
    build_fine_intent_fallback,
    render_fine_intent_fallback,
    requires_deterministic_policy_answer,
)


class PostPurchaseOrderContractTests(unittest.TestCase):
    QUESTION = "Purchase Order issue hone ke baad next process kya hota hai?"

    def test_post_order_question_uses_grounded_contract(self):
        self.assertTrue(requires_deterministic_policy_answer(
            self.QUESTION, "inspection_and_acceptance"))
        state = build_fine_intent_fallback(
            self.QUESTION, "department_buyer", "inspection_and_acceptance", "hinglish",
            "unspecified", "Chhattisgarh", "grounded_deterministic",
            ("publicProManual-1755343081262-715558279.pdf",),
        )
        answer = render_fine_intent_fallback(state).casefold()
        for term in ("inspection", "acceptance", "invoice", "stock/asset register"):
            self.assertIn(term, answer)
        self.assertNotIn("reliable section available nahi", answer)


if __name__ == "__main__":
    unittest.main()
