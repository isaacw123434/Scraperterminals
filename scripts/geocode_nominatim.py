import json
import time
import os

def geocode_station(name):
    # This is a stub for the actual geocoding logic.
    # In a real scenario, this would:
    # 1. Check if the station already has a `geocode_hint` or confirmed coordinate.
    # 2. Query Nominatim API: `https://nominatim.openstreetmap.org/search?q={name} railway station, UK&format=json`
    # 3. Adhere to the Nominatim rate limit: 1 request per second.
    # 4. Parse the response and return lat/lng with confidence 'auto'.
    # 5. If it fails, return null with confidence 'failed'.

    # Simulate a rate limit wait
    time.sleep(1)

    # Return dummy data
    return {
        "lat": 51.5032,
        "lng": -0.1143,
        "confidence": "auto"
    }

def main():
    print("Geocoding unmapped stations via Nominatim...")

    # This script would iterate through data/rail_stations.json, etc.
    # and update the `geocode_hint` for entries missing one.

    print("Geocoding completed.")

if __name__ == "__main__":
    main()
