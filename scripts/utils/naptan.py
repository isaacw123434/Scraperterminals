import requests
import csv
from io import StringIO

NAPTAN_URL = "https://naptan.api.dft.gov.uk/v1/access-nodes?dataFormat=csv"

def fetch_rail_stations():
    """
    Fetches the NaPTAN dataset and extracts railway stations (StopType == 'RLY').
    Returns a list of dicts with id, name, region, lat, lng.
    """
    print("Fetching NaPTAN dataset...")
    response = requests.get(NAPTAN_URL)
    response.raise_for_status()

    stations = []

    # Parse CSV
    reader = csv.DictReader(StringIO(response.text))
    for row in reader:
        if row.get('StopType') == 'RLY':
            try:
                # CommonName, LocalityName, ATCOCode
                station = {
                    "id": row.get('ATCOCode'),
                    "name": row.get('CommonName'),
                    "region": row.get('LocalityName'),
                    "source": "naptan",
                    "centre_lat": float(row.get('Latitude')),
                    "centre_lng": float(row.get('Longitude')),
                    "category": row.get('BusStopType') if row.get('BusStopType') else None, # Attempt category, though typically RLY doesn't have a good one here, handled in merge
                    "entrances": []
                }
                stations.append(station)
            except (ValueError, TypeError):
                continue

    print(f"Found {len(stations)} rail stations in NaPTAN.")
    return stations
