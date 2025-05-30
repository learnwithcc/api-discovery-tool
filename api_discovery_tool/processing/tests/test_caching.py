import unittest
import os
import shutil
import time
import datetime
import shelve
from api_discovery_tool.caching import ResultCache, DEFAULT_MAX_AGE_SECONDS

TEST_CACHE_DIR = os.path.join(os.getcwd(), ".cache_test_dir_unittest")
TEST_CACHE_NAME = "unittest_cache"

class TestResultCache(unittest.TestCase):

    def setUp(self):
        # Ensure a clean environment for each test
        if os.path.exists(TEST_CACHE_DIR):
            shutil.rmtree(TEST_CACHE_DIR)
        os.makedirs(TEST_CACHE_DIR, exist_ok=True)
        self.cache = ResultCache(cache_name=TEST_CACHE_NAME, cache_dir=TEST_CACHE_DIR, max_age_seconds=2) # Short expiry for tests

    def tearDown(self):
        if hasattr(self, 'cache') and self.cache._db is not None:
            self.cache.close() # Ensure shelve is closed
        if os.path.exists(TEST_CACHE_DIR):
            shutil.rmtree(TEST_CACHE_DIR)

    def test_cache_file_creation_default_location_preference(self):
        # This test is a bit tricky as it depends on home dir writability.
        # We'll test the fallback scenario if the primary test location fails for some reason.
        # For now, we trust the __init__ logic and test specific cache_dir usage.
        cache_custom_dir = os.path.join(TEST_CACHE_DIR, "custom_subdir")
        with ResultCache(cache_name="custom_name", cache_dir=cache_custom_dir) as custom_cache:
            # shelve creates files with extensions like .bak, .dat, .dir. We check for one common one.
            # The exact filenames can vary depending on the shelve backend used by the system.
            # A more reliable check is to see if the directory was created and if a subsequent put/get works.
            self.assertTrue(os.path.exists(cache_custom_dir))
            # Check one of the common shelve file patterns
            # Example: custom_name.db.dat or custom_name.db (for dbm.dumb)
            # This isn't foolproof due to backend variations
            found_db_file = False
            for ext in [".db", ".db.dat", ".db.bak", ".db.dir"]:
                if os.path.exists(os.path.join(cache_custom_dir, f"custom_name{ext}")):
                    found_db_file = True
                    break
            # A less direct but more reliable check might be to ensure the directory exists
            # and a simple operation works. For now, we check dir and one common pattern.
            # self.assertTrue(found_db_file, "Cache database file not found in custom directory.")
            # More robust: try a simple operation
            custom_cache.put({"probe": True}, "test")
            self.assertIsNotNone(custom_cache.get({"probe": True}), "Cache in custom dir failed basic operation.")


    def test_generate_key_stability(self):
        with self.cache: # Ensure DB is open for these calls if needed, though _generate_key is standalone
            params1 = {'query': 'users', 'version': 1, 'details': True}
            params2 = {'version': 1, 'details': True, 'query': 'users'} # Same params, different order
            key1 = self.cache._generate_key(params1)
            key2 = self.cache._generate_key(params2)
            self.assertEqual(key1, key2, "Generated keys for same params (different order) should be identical.")
            params3 = {'query': 'users', 'version': 2}
            key3 = self.cache._generate_key(params3)
            self.assertNotEqual(key1, key3, "Generated keys for different params should be different.")

    def test_put_and_get_item(self):
        with self.cache:
            params = {'test': 'put_get'}
            data = {'value': 'some data'}
            self.cache.put(params, data)
            retrieved_data = self.cache.get(params)
            self.assertEqual(retrieved_data, data, "Retrieved data does not match put data.")

    def test_get_non_existent_item(self):
        with self.cache:
            params = {'test': 'non_existent'}
            retrieved_data = self.cache.get(params)
            self.assertIsNone(retrieved_data, "get() should return None for non-existent items.")

    def test_item_expiry(self):
        with self.cache: # max_age_seconds is 2 for this test instance
            params = {'test': 'expiry'}
            data = {'value': 'expiring data'}
            self.cache.put(params, data)
            
            retrieved_immediately = self.cache.get(params)
            self.assertEqual(retrieved_immediately, data, "Data should be retrievable immediately after put.")
            
            time.sleep(3) # Wait for item to become stale (2s expiry + 1s buffer)
            
            retrieved_after_expiry = self.cache.get(params)
            self.assertIsNone(retrieved_after_expiry, "get() should return None for stale items.")
            
            # Verify the item was deleted from the shelve file
            key = self.cache._generate_key(params)
            # Re-open db explicitly if using context manager for main cache, or ensure it's open
            # self.cache._open_db() # If not using `with self.cache:` here specifically for db check
            self.assertNotIn(key, self.cache._db, "Stale item was not removed from the database by get().")

    def test_clear_stale(self):
        with self.cache: # max_age_seconds is 2
            params_fresh = {'item': 'fresh'}
            data_fresh = 'i am fresh'
            # Stored now, timestamped now
            self.cache.put(params_fresh, data_fresh)

            params_stale = {'item': 'stale'}
            data_stale = 'i will be stale'
            self.cache.put(params_stale, data_stale) 
            key_stale = self.cache._generate_key(params_stale)
            key_fresh = self.cache._generate_key(params_fresh)

            # Make params_stale data definitively stale by manipulating its stored timestamp in the shelve
            # This is a bit of a hack to precisely control staleness for testing clear_stale
            # without relying on long sleeps that make tests slow.
            if self.cache._db is not None and key_stale in self.cache._db:
                stale_item_content = self.cache._db[key_stale]
                # Create a timestamp that is definitely older than max_age_seconds
                very_old_timestamp = (datetime.datetime.now(datetime.timezone.utc) - 
                                      datetime.timedelta(seconds=self.cache.max_age_seconds + 60)).isoformat()
                stale_item_content['timestamp'] = very_old_timestamp
                self.cache._db[key_stale] = stale_item_content
            else:
                self.fail(f"Could not find key_stale '{key_stale}' in cache for direct manipulation.")
            
            # params_fresh should remain fresh as its timestamp is recent

            self.cache.clear_stale()
            
            self.assertIsNotNone(self.cache.get(params_fresh), "Fresh item was removed by clear_stale.")
            self.assertIn(key_fresh, self.cache._db, "Fresh item key not in DB after clear_stale")
            
            self.assertNotIn(key_stale, self.cache._db, "Stale item key still in DB after clear_stale.")
            self.assertIsNone(self.cache.get(params_stale), "Stale item was not removed by clear_stale (checked by get).")

    def test_clear_all(self):
        with self.cache:
            params1 = {'item': 'one'}
            params2 = {'item': 'two'}
            self.cache.put(params1, 'data1')
            self.cache.put(params2, 'data2')
            
            self.assertIsNotNone(self.cache.get(params1))
            self.assertIsNotNone(self.cache.get(params2))
            self.assertGreater(len(self.cache._db), 0, "Cache DB should have items before clear_all.")

            self.cache.clear_all()
            
            self.assertIsNone(self.cache.get(params1), "Item1 still found after clear_all.")
            self.assertIsNone(self.cache.get(params2), "Item2 still found after clear_all.")
            self.assertEqual(len(self.cache._db), 0, "Cache DB not empty after clear_all.")

    def test_persistence(self):
        params = {'test': 'persistence'}
        data = {'value': 'persistent data'}
        cache_file_path_to_check = os.path.join(TEST_CACHE_DIR, f"{TEST_CACHE_NAME}.db") # Base name

        with ResultCache(cache_name=TEST_CACHE_NAME, cache_dir=TEST_CACHE_DIR, max_age_seconds=60) as c1:
            c1.put(params, data)
            # Ensure shelve file(s) exist after put
            # self.assertTrue(any(f.startswith(cache_file_path_to_check) for f in os.listdir(TEST_CACHE_DIR)))
        # c1 is closed here by __exit__

        with ResultCache(cache_name=TEST_CACHE_NAME, cache_dir=TEST_CACHE_DIR, max_age_seconds=60) as c2:
            retrieved_data = c2.get(params)
        
        self.assertEqual(retrieved_data, data, "Data did not persist across cache instances.")

    def test_different_data_types_in_params_and_data(self):
        with self.cache:
            params = {
                'string': 'text',
                'integer': 123,
                'float': 45.67,
                'boolean': True,
                'list': [1, 'a', None],
                'dict': {'nested_key': 'nested_value'}
            }
            data = (
                "A string", 
                100, 
                3.14, 
                False, 
                ['x', 'y', 'z'], 
                {'complex': True, 'value': None}
            )
            self.cache.put(params, data)
            retrieved = self.cache.get(params)
            self.assertEqual(retrieved, data, "Failed to cache/retrieve complex data types correctly.")
    
    def test_context_manager_opens_and_closes_db(self):
        # Check db is None before entering context
        # Use a different cache name to ensure it's a fresh instance for this specific test
        ctx_cache_name = "ctx_mgr_test_cache"
        raw_cache = ResultCache(cache_name=ctx_cache_name, cache_dir=TEST_CACHE_DIR)
        self.assertIsNone(raw_cache._db, "DB should be None before context entry.")
        
        with raw_cache:
            self.assertIsNotNone(raw_cache._db, "DB should be opened within context.")
            raw_cache.put({"a":1},"data") # Perform an operation that requires open db
            self.assertIsNotNone(raw_cache.get({"a":1}))

        self.assertIsNone(raw_cache._db, "DB should be closed after exiting context.")

if __name__ == '__main__':
    unittest.main() 