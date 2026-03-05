import requests
import time
import json
import os
import hashlib

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
CACHE_DIR = "scripts/utils/.overpass_cache"

# Ensure cache dir exists
os.makedirs(CACHE_DIR, exist_ok=True)

def _get_cache_path(query):
    hash_object = hashlib.md5(query.encode())
    return os.path.join(CACHE_DIR, f"{hash_object.hexdigest()}.json")

def query_overpass(query):
    """
    Queries the Overpass API with the given query.
    Includes caching and exponential backoff for rate limiting.
    """
    cache_path = _get_cache_path(query)

    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return json.load(f)

    max_retries = 5
    base_delay = 2

    for attempt in range(max_retries):
        try:
            response = requests.post(OVERPASS_URL, data={'data': query})

            if response.status_code == 429: # Too Many Requests
                delay = base_delay * (2 ** attempt)
                print(f"Overpass API rate limit hit. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue

            response.raise_for_status()
            data = response.json()

            # Cache the response
            with open(cache_path, 'w') as f:
                json.dump(data, f)

            time.sleep(1) # Base rate limiting
            return data

        except requests.exceptions.RequestException as e:
            print(f"Overpass query error (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
            else:
                return {"elements": []} # Return empty if fails after retries

    return {"elements": []}
