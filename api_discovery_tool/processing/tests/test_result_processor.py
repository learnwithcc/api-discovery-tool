import unittest
from unittest.mock import patch, MagicMock, ANY
from api_discovery_tool.processing.result_processor import ResultProcessor
# We will also need to import or mock WebsiteAnalyzer, APIPatternRecognizer, ConfidenceScorer
# but for now, let's set up the basics.

class TestResultProcessor(unittest.TestCase):

    def setUp(self):
        # Instantiate the ResultProcessor.
        # Caching can be disabled for tests or a very short TTL can be used.
        self.processor = ResultProcessor(cache_ttl_seconds=0)

        # It's common to mock dependencies that are part of the same package but tested separately.
        # However, ResultProcessor instantiates these itself. So we'll patch where they are instantiated or called.
        # For ConfidenceScorer and APIPatternRecognizer, ResultProcessor instantiates them.
        # We will patch them at the module level where ResultProcessor looks them up.

        # Patching APIPatternRecognizer
        self.mock_pattern_recognizer_patch = patch('api_discovery_tool.processing.result_processor.APIPatternRecognizer')
        self.MockAPIPatternRecognizerClass = self.mock_pattern_recognizer_patch.start()
        self.mock_pattern_recognizer_instance = MagicMock()
        self.MockAPIPatternRecognizerClass.return_value = self.mock_pattern_recognizer_instance

        # Patching ConfidenceScorer
        self.mock_confidence_scorer_patch = patch('api_discovery_tool.processing.result_processor.ConfidenceScorer')
        self.MockConfidenceScorerClass = self.mock_confidence_scorer_patch.start()
        self.mock_confidence_scorer_instance = MagicMock()
        self.MockConfidenceScorerClass.return_value = self.mock_confidence_scorer_instance

        # Patching WebsiteAnalyzer (used specifically in the website_analysis method)
        # This patch will be applied per-method where WebsiteAnalyzer is used.

    def tearDown(self):
        self.mock_pattern_recognizer_patch.stop()
        self.mock_confidence_scorer_patch.stop()

    def test_initialization(self):
        """Test ResultProcessor initializes."""
        self.assertIsNotNone(self.processor)
        self.assertIsNotNone(self.processor.cache)

    @patch('api_discovery_tool.processing.result_processor.WebsiteAnalyzer')
    def test_process_results_website_analysis_success(self, MockWebsiteAnalyzerClass):
        """Test process_results for website_analysis method successfully."""

        # Configure mock WebsiteAnalyzer
        mock_website_analyzer_instance = MagicMock()
        mock_analyze_return_value = {
            "urls": ["http://example.com/api/v1/users", "http://example.com/about"],
            "text_content": ["Sample API text content", "About us page text"]
        }
        mock_website_analyzer_instance.analyze.return_value = mock_analyze_return_value
        MockWebsiteAnalyzerClass.return_value = mock_website_analyzer_instance

        # Configure mock APIPatternRecognizer
        mock_website_patterns = {
            "versioning_schemes": ["v1"],
            "common_paths": ["api"],
            "keyword_matches_in_urls": [{"url": "http://example.com/api/v1/users", "keyword": "users"}],
            "keyword_matches_in_text": []
        }
        self.mock_pattern_recognizer_instance.recognize_from_website_data.return_value = mock_website_patterns

        # Configure mock ConfidenceScorer
        mock_score = 75.0
        self.mock_confidence_scorer_instance.score.return_value = mock_score

        test_url = "http://example.com"
        data_input = {"url": test_url}
        discovery_method = "website_analysis"

        result = self.processor.process_results(
            discovery_method=discovery_method,
            data=data_input
        )

        # Assertions
        MockWebsiteAnalyzerClass.assert_called_once_with(test_url)
        mock_website_analyzer_instance.analyze.assert_called_once_with(crawl_depth=1)

        self.mock_pattern_recognizer_instance.recognize_from_website_data.assert_called_once_with(
            urls=mock_analyze_return_value["urls"],
            text_content=mock_analyze_return_value["text_content"]
        )

        self.mock_confidence_scorer_instance.score.assert_called_once_with(
            mock_website_patterns, data_source_type='website'
        )

        self.assertEqual(result["discovery_method"], discovery_method)
        # raw_data_summary in ResultProcessor for website_analysis stores the extracted_data directly
        self.assertEqual(result["raw_data_summary"], mock_analyze_return_value)
        self.assertEqual(result["analysis_summary"]["api_conventions"], mock_website_patterns)
        self.assertEqual(result["analysis_summary"]["confidence_score"], mock_score)
        self.assertIn("url_analyzed", result["analysis_summary"]["confidence_details"])
        self.assertEqual(result["analysis_summary"]["confidence_details"]["url_analyzed"], test_url)

    def test_process_results_website_analysis_no_url(self):
        """Test process_results for website_analysis when URL is not provided."""
        data_input = {"some_other_key": "value"} # No "url" key
        discovery_method = "website_analysis"

        result = self.processor.process_results(
            discovery_method=discovery_method,
            data=data_input
        )

        self.assertIn("error", result)
        self.assertEqual(result["error"], "URL not provided for website analysis")
        self.assertIn("status_code", result) # My ResultProcessor returns this
        self.assertEqual(result["status_code"], 400)

        # Ensure mocks that shouldn't be called are not called
        self.MockAPIPatternRecognizerClass.assert_not_called() # Recognizer itself is not called if error before that
        self.mock_pattern_recognizer_instance.recognize_from_website_data.assert_not_called()
        self.mock_confidence_scorer_instance.score.assert_not_called()


    # TODO: Add tests for other discovery_methods like 'openapi_spec' and 'mitmproxy'
    # to ensure their calls to pattern_recognizer and confidence_scorer are correct,
    # especially with the new score(patterns, data_source_type) signature.

if __name__ == '__main__':
    unittest.main()
