import os
import unittest

from sarvam_streaming import configured_reasoning_effort, parse_sarvam_sse_line


class SarvamStreamingTests(unittest.TestCase):
    def test_extracts_hidden_reasoning_without_treating_it_as_answer(self):
        line = ('data: {"choices":[{"delta":{"content":null,'
                '"reasoning_content":"Planning the answer"}}]}')
        content, reasoning, done = parse_sarvam_sse_line(line)
        self.assertEqual(content, "")
        self.assertEqual(reasoning, "Planning the answer")
        self.assertFalse(done)

    def test_extracts_visible_answer_content(self):
        line = 'data: {"choices":[{"delta":{"content":"Answer text"}}]}'
        content, reasoning, done = parse_sarvam_sse_line(line)
        self.assertEqual(content, "Answer text")
        self.assertEqual(reasoning, "")
        self.assertFalse(done)

    def test_recognises_completion_marker(self):
        self.assertEqual(parse_sarvam_sse_line('data: [DONE]'), ("", "", True))

    def test_default_uses_low_reasoning_but_can_disable_it(self):
        old = os.environ.pop("SARVAM_REASONING_EFFORT", None)
        try:
            self.assertEqual(configured_reasoning_effort(), "low")
            os.environ["SARVAM_REASONING_EFFORT"] = "none"
            self.assertIsNone(configured_reasoning_effort())
        finally:
            if old is None:
                os.environ.pop("SARVAM_REASONING_EFFORT", None)
            else:
                os.environ["SARVAM_REASONING_EFFORT"] = old


if __name__ == "__main__":
    unittest.main()
