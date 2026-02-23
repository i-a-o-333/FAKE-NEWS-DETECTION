import unittest

from src.news_intel.text_processing import extract_claim_candidates, extract_topic, normalize_text


class TextProcessingTests(unittest.TestCase):
    def test_normalize_text(self) -> None:
        self.assertEqual(normalize_text("Hello\n\nworld   !"), "Hello world !")

    def test_extract_topic_question(self) -> None:
        topic = extract_topic("Do aliens exist?")
        self.assertIn("aliens", topic)

    def test_extract_claim_candidates(self) -> None:
        text = "Officials confirmed the launch in 2024 according to records. Why now?"
        claims = extract_claim_candidates(text)
        self.assertGreaterEqual(len(claims), 1)


if __name__ == "__main__":
    unittest.main()
