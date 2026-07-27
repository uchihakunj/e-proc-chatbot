import unittest

from actor_policy import DEPARTMENT_BUYER, actor_answer_violations


class ActorAnswerGuardTests(unittest.TestCase):
    def test_department_answer_rejects_vendor_registration_flow(self):
        answer = "Pehle vendor registration karein, valid DSC use karein aur technical bid submit karein."
        issues = actor_answer_violations(DEPARTMENT_BUYER, answer)
        self.assertIn("vendor registration", issues)
        self.assertIn("valid dsc", issues)

    def test_department_answer_allows_vendor_role_explanation(self):
        answer = "Department Tender publish karta hai; vendors apni bids submit karte hain."
        self.assertEqual(actor_answer_violations(DEPARTMENT_BUYER, answer), ())


if __name__ == "__main__":
    unittest.main()
