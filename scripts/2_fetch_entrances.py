import json
import os
import math
from utils import overpass

DATA_DIR = "data"

def get_bounding_box(lat, lon, distance_m=500):
    """
    Calculates a bounding box (south, west, north, east) around a given point.
    """
    # Rough approximation: 1 degree latitude is ~111km
    lat_offset = distance_m / 111000.0
    lon_offset = distance_m / (111000.0 * math.cos(math.radians(lat)))

    return lat - lat_offset, lon - lon_offset, lat + lat_offset, lon + lon_offset

def classify_entrance(tags, element_type, name_query):
    """
    Classifies the entrance type and confidence based on OSM tags.
    Returns (entrance_type, confidence).
    """
    name = tags.get("name", "").lower()
    name_query_lower = name_query.lower()

    # Entrance type mapping
    if "railway" in tags and tags["railway"] == "station":
        entrance_type = "main"
    elif "amenity" in tags and tags["amenity"] == "parking":
        if tags.get("long_stay") == "yes" or "long stay" in name or "station" in name:
            entrance_type = "car_park"
        else:
            entrance_type = "car_park" # Lower confidence, handled later
    elif "park_ride" in tags:
        entrance_type = "park_and_ride"
    elif "amenity" in tags and tags["amenity"] == "bus_station":
        entrance_type = "bus_interchange"
    elif "amenity" in tags and tags["amenity"] == "bicycle_parking":
        entrance_type = "cycle_entrance"
    else:
        return None, None

    # Confidence scoring
    confidence = "low"
    if entrance_type == "main":
        if tags.get("railway") == "station" or name_query_lower in name:
            confidence = "high"
        else:
            confidence = "medium"
    elif entrance_type == "car_park":
        if "long stay" in name or "station" in name or "ncp" in name or "q-park" in name or name_query_lower in name:
            confidence = "high"
        else:
            confidence = "medium"
    elif entrance_type == "park_and_ride":
         confidence = "high" if name_query_lower in name else "medium"
    elif entrance_type == "bus_interchange":
         confidence = "high" if name_query_lower in name else "medium"
    elif entrance_type == "cycle_entrance":
         confidence = "medium" # Typically medium unless very specifically named

    return entrance_type, confidence

def process_hub(hub):
    """
    Fetches and classifies entrances for a single hub.
    """
    lat, lng = hub.get("centre_lat"), hub.get("centre_lng")
    if lat is None or lng is None:
        return hub

    print(f"Processing hub: {hub['name']} ({hub['id']})")

    s, w, n, e = get_bounding_box(lat, lng, 500)
    bbox_str = f"{s},{w},{n},{e}"

    query = f"""[out:json];
(
  way["railway"="station"]({bbox_str});
  node["railway"="station"]({bbox_str});

  way["amenity"="parking"]["parking"="surface"]({bbox_str});
  way["amenity"="parking"]["parking"="multi-storey"]({bbox_str});
  way["amenity"="parking"]["access"="yes"]({bbox_str});

  node["park_ride"]({bbox_str});
  way["park_ride"]({bbox_str});

  node["amenity"="bus_station"]({bbox_str});
  way["amenity"="bus_station"]({bbox_str});

  node["amenity"="bicycle_parking"]({bbox_str});
);
out center;
"""

    results = overpass.query_overpass(query)
    entrances = []

    for element in results.get("elements", []):
        tags = element.get("tags", {})
        el_type = element.get("type")
        osm_id = f"{el_type}/{element.get('id')}"

        # Get coordinates (center for ways)
        if el_type == "node":
            ent_lat, ent_lng = element.get("lat"), element.get("lon")
        else:
            center = element.get("center", {})
            ent_lat, ent_lng = center.get("lat"), center.get("lon")

        if ent_lat is None or ent_lng is None:
            continue

        # Classify
        entrance_type, confidence = classify_entrance(tags, el_type, hub["name"])

        if entrance_type:
            # Distance logic for lowering confidence could go here (e.g. if > 200m, downgrade to low)
            dist_approx = math.sqrt((lat - ent_lat)**2 + (lng - ent_lng)**2) * 111000
            if dist_approx > 200 and confidence != "low":
                 confidence = "medium" if confidence == "high" else "low"
            if dist_approx > 500:
                 confidence = "low"

            entrances.append({
                "entrance_id": f"{hub['id']}_{entrance_type}_{len(entrances)}",
                "entrance_type": entrance_type,
                "lat": ent_lat,
                "lng": ent_lng,
                "source": "overpass",
                "osm_id": osm_id,
                "osm_tags": tags,
                "confidence": confidence,
                "is_primary": True if len([e for e in entrances if e['entrance_type'] == entrance_type]) == 0 else False, # first of type is primary
                "confirmed": False,
                "confirmed_at": None,
                "notes": ""
            })

    hub["entrances"] = entrances
    return hub

def process_file(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found. Skipping.")
        return

    with open(filepath, 'r') as f:
        data = json.load(f)

    processed_data = []
    for hub in data:
        processed_data.append(process_hub(hub))

    out_filepath = os.path.join(DATA_DIR, filename.replace("_raw.json", "_with_entrances.json"))
    with open(out_filepath, 'w') as f:
        json.dump(processed_data, f, indent=2)

def main():
    print("Fetching entrances from Overpass API...")
    process_file("rail_stations_raw.json")
    process_file("coach_terminals_raw.json")
    process_file("park_and_ride_raw.json")

if __name__ == "__main__":
    main()
