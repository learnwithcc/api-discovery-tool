import unittest
import datetime
from api_discovery_tool.scoring import calculate_confidence, calculate_completeness_score, calculate_reliability_score, calculate_recency_score, calculate_validation_score

class TestScoringSystem(unittest.TestCase):

    def test_calculate_completeness_score(self):
        self.assertEqual(calculate_completeness_score(10, 10), 1.0) # Full completeness
        self.assertEqual(calculate_completeness_score(5, 10), 0.5)  # Half completeness
        self.assertEqual(calculate_completeness_score(0, 10), 0.0)  # No completeness
        self.assertEqual(calculate_completeness_score(10, 0), 0.0) # Edge case: zero total fields
        self.assertEqual(calculate_completeness_score(0, 0), 0.0)   # Edge case: zero fields
        self.assertEqual(calculate_completeness_score(12, 10), 1.0) # More fields than expected (capped at 1.0)
        self.assertEqual(calculate_completeness_score(-5, 10), 0.0) # Negative fields present (capped at 0.0)

    def test_calculate_reliability_score(self):
        self.assertEqual(calculate_reliability_score('official_doc'), 0.9)
        self.assertEqual(calculate_reliability_score('known_api_db'), 0.8)
        self.assertEqual(calculate_reliability_score('blog'), 0.5)
        self.assertEqual(calculate_reliability_score('forum'), 0.3)
        self.assertEqual(calculate_reliability_score('unknown_source_type'), 0.2) # Default for unknown
        self.assertEqual(calculate_reliability_score('OFFICIAL_DOC'), 0.9) # Case-insensitivity

    def test_calculate_recency_score(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        self.assertAlmostEqual(calculate_recency_score(now), 1.0, places=7) # Very recent
        
        one_year_ago = now - datetime.timedelta(days=365)
        expected_one_year_ago_score = 1.0 - (0.1 * (365 / 365.25))
        self.assertAlmostEqual(calculate_recency_score(one_year_ago), expected_one_year_ago_score, places=7) # 1 year old (365 days)
        
        five_years_ago = now - datetime.timedelta(days=5*365)
        expected_five_years_ago_score = 1.0 - (0.1 * (5 * 365 / 365.25))
        self.assertAlmostEqual(calculate_recency_score(five_years_ago), expected_five_years_ago_score, places=7) # 5 years old (5*365 days)
        
        ten_years_ago = now - datetime.timedelta(days=10*365)
        expected_ten_years_ago_score = max(0.0, 1.0 - (0.1 * (10 * 365 / 365.25)))
        self.assertAlmostEqual(calculate_recency_score(ten_years_ago), expected_ten_years_ago_score, places=7) # 10 years old (10*365 days)
        
        eleven_years_ago = now - datetime.timedelta(days=11*365) # This should already be 0.0
        expected_eleven_years_ago_score = max(0.0, 1.0 - (0.1 * (11 * 365 / 365.25)))
        self.assertAlmostEqual(calculate_recency_score(eleven_years_ago), expected_eleven_years_ago_score, places=7) # Older than max decay
        
        future_date = now + datetime.timedelta(days=30)
        self.assertAlmostEqual(calculate_recency_score(future_date), 1.0, places=7) # Future date
        self.assertEqual(calculate_recency_score(None), 0.5) # None timestamp
        
        # Test with naive datetime (should be handled by assuming UTC)
        # For naive dates, the age calculation will be relative to local 'now' if not careful,
        # but calculate_recency_score converts naive to UTC.
        # The number of days difference will be the same (365), so the score should match expected_one_year_ago_score.
        naive_one_year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
        self.assertAlmostEqual(calculate_recency_score(naive_one_year_ago), expected_one_year_ago_score, places=7)

    def test_calculate_validation_score(self):
        self.assertEqual(calculate_validation_score(True), 1.0)
        self.assertEqual(calculate_validation_score(False), 0.0)
        self.assertEqual(calculate_validation_score(None), 0.5) # Neutral for unknown

    def test_calculate_confidence_high_confidence(self):
        data = {
            'metadata': {
                'source_type': 'official_doc',
                'fields_present': 10,
                'total_expected_fields': 10,
                'discovery_timestamp': datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30),
                'validated': True
            }
        }
        # Expected: (1.0 * 0.3) + (0.9 * 0.4) + (approx 0.99 * 0.15) + (1.0 * 0.15)
        # = 0.3 + 0.36 + 0.1485 + 0.15 = 0.9585
        self.assertAlmostEqual(calculate_confidence(data), 0.958, delta=0.001)

    def test_calculate_confidence_low_confidence(self):
        data = {
            'metadata': {
                'source_type': 'unknown',
                'fields_present': 2,
                'total_expected_fields': 10,
                'discovery_timestamp': datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3*365),
                'validated': False
            }
        }
        # Expected: (0.2 * 0.3) + (0.2 * 0.4) + (0.7 * 0.15) + (0.0 * 0.15)
        # = 0.06 + 0.08 + 0.105 + 0.0 = 0.245
        self.assertAlmostEqual(calculate_confidence(data), 0.245, delta=0.001)

    def test_calculate_confidence_medium_confidence_blog(self):
        data = {
            'metadata': {
                'source_type': 'blog',
                'fields_present': 7,
                'total_expected_fields': 10,
                'discovery_timestamp': datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=365),
                'validated': False
            }
        }
        # Expected: (0.7 * 0.3) + (0.5 * 0.4) + (0.9 * 0.15) + (0.0 * 0.15)
        # = 0.21 + 0.20 + 0.135 + 0.0 = 0.545
        self.assertAlmostEqual(calculate_confidence(data), 0.545, delta=0.001)

    def test_calculate_confidence_missing_metadata(self):
        data = {
            'metadata': {}
        }
        # Expected (defaults): (0/0->0.0 * 0.3) + (unknown->0.2 * 0.4) + (None->0.5 * 0.15) + (None->0.5 * 0.15)
        # = 0.0 + 0.08 + 0.075 + 0.075 = 0.23
        self.assertAlmostEqual(calculate_confidence(data), 0.23, delta=0.001)
    
    def test_calculate_confidence_no_metadata_key(self):
        data = {}
        # Should behave same as empty metadata dict
        self.assertAlmostEqual(calculate_confidence(data), 0.23, delta=0.001)

    def test_calculate_confidence_zero_expected_fields(self):
        data = {
            'metadata': {
                'source_type': 'official_doc',
                'fields_present': 5,
                'total_expected_fields': 0, # Completeness score will be 0
                'discovery_timestamp': datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30),
                'validated': True
            }
        }
        # Expected: (0.0 * 0.3) + (0.9 * 0.4) + (approx 0.99 * 0.15) + (1.0 * 0.15)
        # = 0.0 + 0.36 + 0.1485 + 0.15 = 0.6585
        self.assertAlmostEqual(calculate_confidence(data), 0.658, delta=0.001)

if __name__ == '__main__':
    unittest.main() 