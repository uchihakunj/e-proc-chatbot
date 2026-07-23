import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from nlp_features import correct_typos
from streaming_utils import (
    is_explicitly_out_of_scope,
    new_stream_state,
    record_stream_content,
    sanitize_model_answer,
    should_retry_with_fallback,
)


class StreamingStateTests(unittest.TestCase):
    def test_new_state_preserves_provider_fallback_reason(self):
        state = new_stream_state()

        self.assertEqual(state["fallback_reason"], "")

    def test_provider_tokens_are_reconstructed_for_done_event_and_cache(self):
        state = new_stream_state()

        record_stream_content(state, "\n")
        self.assertFalse(state["content_streamed"])

        record_stream_content(state, "Answer")
        record_stream_content(state, " text")

        self.assertTrue(state["content_streamed"])
        self.assertEqual("".join(state["answer_buf"]), "\nAnswer text")

    def test_fallback_state_without_buffer_is_repaired(self):
        state = {"content_streamed": False, "failed_before_output": False}

        record_stream_content(state, "fallback answer")

        self.assertEqual(state["answer_buf"], ["fallback answer"])
        self.assertTrue(state["content_streamed"])

    def test_sarvam_timeout_state_can_retry_on_fallback_model(self):
        state = {
            "content_streamed": False,
            "failed_before_output": True,
            "sarvam_timeout": True,
        }

        self.assertTrue(
            should_retry_with_fallback(state, True, "gemma3:4b")
        )

    def test_fallback_is_skipped_when_disabled(self):
        state = {
            "content_streamed": False,
            "failed_before_output": True,
        }

        self.assertFalse(
            should_retry_with_fallback(state, False, "gemma3:4b")
        )

    def test_fallback_requires_a_configured_model(self):
        state = {
            "content_streamed": False,
            "failed_before_output": True,
        }

        self.assertFalse(
            should_retry_with_fallback(state, True, "")
        )

    def test_cumulative_provider_snapshots_are_not_duplicated(self):
        state = new_stream_state()

        emitted = [
            record_stream_content(state, "Answer"),
            record_stream_content(state, "Answer text"),
            record_stream_content(state, "Answer text"),
            record_stream_content(state, "Answer text complete."),
        ]

        self.assertEqual(emitted, ["Answer", " text", "", " complete."])
        self.assertEqual("".join(state["answer_buf"]), "Answer text complete.")

    def test_older_cumulative_snapshot_is_ignored(self):
        state = new_stream_state()

        record_stream_content(state, "Complete response")
        emitted = record_stream_content(state, "Complete")

        self.assertEqual(emitted, "")
        self.assertEqual("".join(state["answer_buf"]), "Complete response")

    def test_valid_participating_word_is_not_fuzzy_rewritten(self):
        query = "For a newly participating supplier, explain EMD."

        corrected, corrections = correct_typos(query)

        self.assertEqual(corrected, query)
        self.assertEqual(corrections, [])

    def test_known_typo_is_still_corrected(self):
        corrected, corrections = correct_typos("How do I paticipate in a tendor?")

        self.assertEqual(corrected, "How do I participate in a tender?")
        self.assertEqual(corrections, [("paticipate", "participate"), ("tendor", "tender")])

    def test_model_artifacts_are_removed_from_valid_answer(self):
        refusal = "The answer to this question was not found in the available documents."
        raw = (
            "💡 Answer\nEMD safeguards a bid.\n\n"
            "📋 Process\n(Omitted as this is not a process)\n\n"
            "📘 Source: Procurement Manual\n\n" + refusal
        )

        cleaned = sanitize_model_answer(raw, [refusal])

        self.assertEqual(
            cleaned,
            "💡 Answer\nEMD safeguards a bid.\n\n📘 Source: Procurement Manual",
        )

    def test_genuine_refusal_is_preserved(self):
        refusal = "The answer to this question was not found in the available documents."

        self.assertEqual(sanitize_model_answer(refusal, [refusal]), refusal)

    def test_explicit_general_topic_is_out_of_scope(self):
        self.assertTrue(is_explicitly_out_of_scope("What is the weather on Mars today?"))
        self.assertTrue(is_explicitly_out_of_scope("Tell me a joke"))

    def test_procurement_question_with_weather_word_remains_in_scope(self):
        query = "What procurement rules apply to emergency purchases after severe weather?"

        self.assertFalse(is_explicitly_out_of_scope(query))


if __name__ == "__main__":
    unittest.main()
