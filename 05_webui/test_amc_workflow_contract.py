import unittest

from fine_intent_policy import build_fine_intent_fallback, render_fine_intent_fallback


class AmcWorkflowContractTests(unittest.TestCase):
    def test_generic_ac_amc_question_gets_service_workflow(self):
        state = build_fine_intent_fallback(
            "Department ko AC ka AMC karana hai. Process kya hai?",
            "department_buyer", "procurement_planning", "hinglish",
            "amc_services", "Chhattisgarh", "grounded_deterministic",
            ("publicProManual-1755343081262-715558279.pdf",),
        )
        answer = render_fine_intent_fallback(state).casefold()
        self.assertIn("service scope", answer)
        self.assertIn("sla", answer)
        self.assertIn("approval", answer)
        self.assertNotIn("reliable section available nahi", answer)


if __name__ == "__main__":
    unittest.main()
