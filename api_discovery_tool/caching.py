import shelve
import hashlib
import json
import os
import datetime
import time

DEFAULT_MAX_AGE_SECONDS = 7 * 24 * 60 * 60  # 7 days

class ResultCache:
    """A simple caching mechanism using shelve for persistence."""

    def __init__(self, cache_name="results_cache", cache_dir=None, max_age_seconds=DEFAULT_MAX_AGE_SECONDS):
        """
        Initializes the ResultCache.

        Args:
            cache_name (str): The name of the cache file (without extension).
            cache_dir (str, optional): Directory to store the cache. 
                                       Defaults to ~/.cache/api_discovery_tool/ or .cache/api_discovery_tool/ if home is not writable.
            max_age_seconds (int): Maximum age of cache items in seconds.
        """
        if cache_dir is None:
            try:
                user_cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "api_discovery_tool")
                os.makedirs(user_cache_dir, exist_ok=True)
                # Test writability
                test_file = os.path.join(user_cache_dir, ".__test_writable__")
                with open(test_file, "w") as f:
                    f.write("test")
                os.remove(test_file)
                self.cache_dir = user_cache_dir
            except (OSError, PermissionError):
                # Fallback to local directory
                local_cache_dir = os.path.join(os.getcwd(), ".cache", "api_discovery_tool")
                os.makedirs(local_cache_dir, exist_ok=True)
                self.cache_dir = local_cache_dir
        else:
            self.cache_dir = cache_dir
            os.makedirs(self.cache_dir, exist_ok=True)

        self.cache_file_path = os.path.join(self.cache_dir, f"{cache_name}.db")
        self.max_age_seconds = max_age_seconds
        self._db = None # Shelve object will be opened on demand

    def _open_db(self):
        if self._db is None:
            self._db = shelve.open(self.cache_file_path)

    def _close_db(self):
        if self._db is not None:
            self._db.close()
            self._db = None

    def __enter__(self):
        self._open_db()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close_db()

    def _generate_key(self, params: dict) -> str:
        """Generates a stable SHA256 hash key from a dictionary of parameters."""
        # Sort the dictionary by keys to ensure consistent string representation
        canonical_params = json.dumps(params, sort_keys=True)
        return hashlib.sha256(canonical_params.encode('utf-8')).hexdigest()

    def get(self, params: dict):
        """
        Retrieves data from the cache if available and not stale.

        Args:
            params (dict): Parameters used to generate the original data.

        Returns:
            The cached data if found and not stale, otherwise None.
        """
        self._open_db()
        key = self._generate_key(params)
        cached_item = self._db.get(key)

        if cached_item:
            timestamp_str = cached_item.get('timestamp')
            data = cached_item.get('data')
            
            if timestamp_str:
                try:
                    # Attempt to parse with timezone info first
                    timestamp = datetime.datetime.fromisoformat(timestamp_str)
                except ValueError:
                    # Fallback for older ISO formats or if no tzinfo (should not happen if we always store with UTC)
                    # This part might need adjustment if timestamps are stored differently or need migration.
                    # For now, let's assume if it's not full isoformat, it might be a naive UTC timestamp string.
                    try:
                        timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%f")
                        timestamp = timestamp.replace(tzinfo=datetime.timezone.utc) # Assume UTC if naive
                    except ValueError:
                         # Final fallback if strptime also fails
                        print(f"Warning: Could not parse timestamp string '{timestamp_str}' for cache key '{key}'. Considering item stale.")
                        return None

                # Ensure timestamp is offset-aware for comparison
                if timestamp.tzinfo is None or timestamp.tzinfo.utcoffset(timestamp) is None:
                    timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)

                age_seconds = (datetime.datetime.now(datetime.timezone.utc) - timestamp).total_seconds()
                if age_seconds <= self.max_age_seconds:
                    return data
                else:
                    # Item is stale, remove it
                    del self._db[key]
        return None

    def put(self, params: dict, data: any):
        """
        Stores data in the cache.

        Args:
            params (dict): Parameters used to generate the data.
            data (any): The data to cache.
        """
        self._open_db()
        key = self._generate_key(params)
        # Store timestamp in ISO format with UTC timezone
        timestamp_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self._db[key] = {'timestamp': timestamp_str, 'data': data}

    def clear_stale(self):
        """Removes all stale items from the cache."""
        self._open_db()
        keys_to_delete = []
        for key in list(self._db.keys()): # list() to avoid issues with concurrent modification
            cached_item = self._db.get(key)
            if cached_item:
                timestamp_str = cached_item.get('timestamp')
                if timestamp_str:
                    try:
                        timestamp = datetime.datetime.fromisoformat(timestamp_str)
                    except ValueError:
                        try:
                            timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%f")
                            timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)
                        except ValueError:
                            keys_to_delete.append(key) # Unparsable timestamp, treat as stale
                            continue
                    
                    if timestamp.tzinfo is None or timestamp.tzinfo.utcoffset(timestamp) is None:
                         timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)

                    age_seconds = (datetime.datetime.now(datetime.timezone.utc) - timestamp).total_seconds()
                    if age_seconds > self.max_age_seconds:
                        keys_to_delete.append(key)
                else:
                    keys_to_delete.append(key) # No timestamp, treat as stale
            else:
                # This case should ideally not happen if key is from self._db.keys()
                # but good to be defensive. If it's None, it's effectively gone.
                pass 

        for key in keys_to_delete:
            if key in self._db:
                 del self._db[key]
        if keys_to_delete:
            print(f"Cleared {len(keys_to_delete)} stale item(s) from cache.")

    def clear_all(self):
        """Clears all items from the cache."""
        self._open_db()
        # Shelve doesn't have a clear() method directly that works on all backends.
        # Iterating and deleting is the most reliable way.
        keys_to_delete = list(self._db.keys())
        for key in keys_to_delete:
            del self._db[key]
        print(f"Cleared all {len(keys_to_delete)} item(s) from the cache.")

    def close(self):
        """Closes the shelve database explicitly."""
        self._close_db()
        print("Cache closed.")

# Example usage (for basic manual testing)
if __name__ == '__main__':
    print("Testing ResultCache...")
    # Using a specific test cache directory to avoid cluttering default locations
    test_cache_dir = os.path.join(os.getcwd(), ".cache_test", "api_discovery_tool")
    
    # Ensure the test directory is clean before starting
    if os.path.exists(test_cache_dir):
        import shutil
        shutil.rmtree(test_cache_dir)
    os.makedirs(test_cache_dir, exist_ok=True)

    cache = ResultCache(cache_name="my_test_cache", cache_dir=test_cache_dir, max_age_seconds=5) # Short expiry for testing

    with cache: # Using context manager
        params1 = {'query': 'users', 'version': 1}
        data1 = {'result': 'data for users v1'}
        
        print(f"Putting data for params1: {params1}")
        cache.put(params1, data1)
        
        retrieved_data1 = cache.get(params1)
        print(f"Retrieved data for params1: {retrieved_data1}")
        assert retrieved_data1 == data1, "Data mismatch after immediate get!"

        print("Waiting for cache to expire (6 seconds)...")
        time.sleep(6)

        retrieved_stale_data1 = cache.get(params1)
        print(f"Retrieved data for params1 after expiry: {retrieved_stale_data1}")
        assert retrieved_stale_data1 is None, "Stale data was not None!"

        # Test clear_stale (item should have been removed by get() already if stale)
        params2 = {'query': 'products', 'version': 2}
        data2 = {'result': 'data for products v2'}
        cache.put(params2, data2) # This one is fresh
        print("Putting fresh data for params2 and sleeping for 2s...")
        time.sleep(2) # params2 is 2s old
        cache.clear_stale()
        retrieved_data2 = cache.get(params2)
        print(f"Retrieved data for params2 after clear_stale: {retrieved_data2}")
        assert retrieved_data2 == data2, "Fresh data was removed by clear_stale!"

        # Test clear_all
        cache.put(params1, {'result': 're-cached users v1'}) # Re-cache params1
        print(f"Cache items before clear_all: {list(cache._db.keys())}")
        cache.clear_all()
        print(f"Cache items after clear_all: {list(cache._db.keys())}")
        assert not list(cache._db.keys()), "Cache not empty after clear_all!"
        assert cache.get(params1) is None, "Data found after clear_all!"
        assert cache.get(params2) is None, "Data found after clear_all!"

    print("Cache test completed successfully.")

    # Clean up the test cache directory
    if os.path.exists(test_cache_dir):
        import shutil
        shutil.rmtree(test_cache_dir)
        print(f"Cleaned up test cache directory: {test_cache_dir}") 