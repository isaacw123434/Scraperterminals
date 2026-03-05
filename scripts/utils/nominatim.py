import requests
import time
import urllib.parse

def geocode(query):
    """
    Geocodes a query string using Nominatim API.
    Adheres to 1 request per second rate limit.
    Returns (lat, lng) or (None, None) if not found.
    """
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&limit=1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    time.sleep(1)  # Rate limiting

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data and len(data) > 0:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as e:
        print(f"Geocoding error for {query}: {e}")

    return None, None
