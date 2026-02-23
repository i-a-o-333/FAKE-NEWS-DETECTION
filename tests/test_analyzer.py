import unittest

from src.news_intel.analyzer import analyze_text, determine_final_assessment


class AnalyzerTests(unittest.TestCase):
    def test_analyze_text_returns_result(self) -> None:
        result = analyze_text("According to a 2023 report, emissions fell by 23% in Germany.")
        self.assertTrue(result.topic)
        self.assertGreaterEqual(len(result.claims), 1)
        self.assertGreaterEqual(len(result.references), 1)

    def test_final_assessment_political(self) -> None:
        label = determine_final_assessment(
            {"objectivity": 70, "reliability": 60, "propaganda": 45},
            "Political influence",
        )
        self.assertEqual(label, "Likely propaganda")


if __name__ == "__main__":
    unittest.main()
