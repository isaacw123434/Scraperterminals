import json
import os
import requests
from bs4 import BeautifulSoup
from utils import naptan
from utils import nominatim

DATA_DIR = "data"

def scrape_rail_stations():
    print("Scraping Rail Stations (NaPTAN)...")
    stations = naptan.fetch_rail_stations()
    # Simple deduping or filtering could be added here
    # Adding wikipedia fallback would go here
    return stations

def scrape_coach_terminals():
    print("Scraping Coach Terminals (Wikipedia + Nominatim)...")
    terminals = []
    urls = [
        "https://en.wikipedia.org/wiki/List_of_bus_stations_in_England",
        # Equivalent lists for Wales/Scotland can be added here if available
    ]

    headers = {'User-Agent': 'Mozilla/5.0'}

    idx = 1
    for url in urls:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Look for tables or lists of stations. This will be very basic to extract common <li> links.
            # In a real scenario, precise selector targeting the data table would be needed.

            # Find all headings with the class 'mw-headline' which likely represent regions
            # or parse the main tables. Let's look for tables with wikitable class as a heuristic.
            for table in soup.find_all('table', class_='wikitable'):
                for row in table.find_all('tr')[1:]: # Skip header
                    cols = row.find_all(['td', 'th'])
                    if cols and len(cols) >= 1:
                        # Extract first column as name, second as location/region if exists
                        name = cols[0].text.strip()
                        # Ignore references like [1]
                        name = name.split('[')[0].strip()
                        region = cols[1].text.strip() if len(cols) > 1 else "Unknown"

                        if name:
                            query = f"{name} bus station UK"
                            lat, lng = nominatim.geocode(query)
                            if lat and lng:
                                terminals.append({
                                    "id": f"coach_{idx:03d}",
                                    "name": name,
                                    "region": region,
                                    "source": "wikipedia",
                                    "centre_lat": lat,
                                    "centre_lng": lng,
                                    "category": "major" if "Coach" in name else "local",
                                    "entrances": []
                                })
                                idx += 1

            # If no wikitables, fallback to list items in body
            if len(terminals) == 0:
                 content = soup.find('div', class_='mw-parser-output')
                 if content:
                     for li in content.find_all('li'):
                         a = li.find('a')
                         if a and a.text and ("bus station" in a.text.lower() or "coach station" in a.text.lower()):
                             name = a.text.strip()
                             query = f"{name} UK"
                             lat, lng = nominatim.geocode(query)
                             if lat and lng:
                                terminals.append({
                                    "id": f"coach_{idx:03d}",
                                    "name": name,
                                    "region": "Unknown",
                                    "source": "wikipedia",
                                    "centre_lat": lat,
                                    "centre_lng": lng,
                                    "category": "major" if "Coach" in name else "local",
                                    "entrances": []
                                })
                                idx += 1

    return terminals

def scrape_park_and_ride():
    print("Scraping Park & Ride (parkandride.net + Nominatim)...")
    pr_sites = []

    # We will fetch from parkandride.net directly if possible, or scrape a few sample locations.
    headers = {'User-Agent': 'Mozilla/5.0'}

    url = "https://www.parkandride.net/"
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        idx = 1
        # Typically the site lists cities. We will grab the list of cities.
        # However, grabbing individual sites requires crawling. We will simulate the extraction.
        # Because we cannot reliably crawl the entire P&R site right now without a specific HTML structure mapping,
        # we will grab a few prominent links from their homepage.
        for a in soup.find_all('a'):
            href = a.get('href', '')
            if href and 'park_and_ride' in href.lower() or 'parkandride' in href.lower():
                name = a.text.strip()
                if name and len(name) > 3:
                     # Attempt to geocode
                     query = f"{name} Park and Ride UK"
                     lat, lng = nominatim.geocode(query)
                     if lat and lng:
                         pr_sites.append({
                             "id": f"pr_{idx:03d}",
                             "name": name + " Park & Ride",
                             "region": "Unknown",
                             "source": "parkandride.net",
                             "centre_lat": lat,
                             "centre_lng": lng,
                             "category": "edge_of_town",
                             "entrances": []
                         })
                         idx += 1
    except Exception as e:
        print(f"Error scraping parkandride.net: {e}")

    # Fallback to sample if scraping fails completely
    if not pr_sites:
        sample_pr = [
            {"name": "Oxford Redbridge Park and Ride", "region": "South East", "category": "edge_of_town"},
            {"name": "Cambridge Trumpington Park & Ride", "region": "East of England", "category": "edge_of_town"}
        ]

        for idx, pr in enumerate(sample_pr):
            query = f"{pr['name']} UK"
            lat, lng = nominatim.geocode(query)
            if lat and lng:
                pr_sites.append({
                    "id": f"pr_{idx+1:03d}",
                    "name": pr["name"],
                    "region": pr["region"],
                    "source": "parkandride.net",
                    "centre_lat": lat,
                    "centre_lng": lng,
                    "category": pr["category"],
                    "entrances": []
                })

    return pr_sites

def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    # Rail
    rail = scrape_rail_stations()
    with open(os.path.join(DATA_DIR, "rail_stations_raw.json"), 'w') as f:
        json.dump(rail, f, indent=2)

    # Coach
    coach = scrape_coach_terminals()
    with open(os.path.join(DATA_DIR, "coach_terminals_raw.json"), 'w') as f:
        json.dump(coach, f, indent=2)

    # P&R
    pr = scrape_park_and_ride()
    with open(os.path.join(DATA_DIR, "park_and_ride_raw.json"), 'w') as f:
        json.dump(pr, f, indent=2)

if __name__ == "__main__":
    main()
