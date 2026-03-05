import json
import os

DATA_DIR = "data"

def process_hub(hub):
    """
    Applies final scoring and status logic to a hub.
    """
    entrances = hub.get("entrances", [])

    # 1. Determine has_car_park
    if any(e.get("entrance_type") == "car_park" for e in entrances):
        hub["has_car_park"] = True
    else:
        hub["has_car_park"] = False

    # 2. Determine status
    if not entrances:
        hub["status"] = "unreviewed"
        # If no entrances found, create a fallback pin at the center
        lat, lng = hub.get("centre_lat"), hub.get("centre_lng")
        if lat and lng:
            entrances.append({
                 "entrance_id": f"{hub['id']}_main_fallback",
                 "entrance_type": "main",
                 "lat": lat,
                 "lng": lng,
                 "source": "fallback",
                 "osm_id": None,
                 "confidence": "none",
                 "is_primary": True,
                 "confirmed": False,
                 "confirmed_at": None,
                 "notes": "Fallback pin at hub centre."
            })
    else:
        all_low_confidence = all(e.get("confidence") == "low" for e in entrances)
        if all_low_confidence:
             hub["status"] = "needs_review"
        else:
             hub["status"] = "unreviewed"

    # Ensure category is present
    if "category" not in hub:
        hub["category"] = None

    # Ensure flagged and skipped exist
    hub.setdefault("flagged", False)
    hub.setdefault("skipped", False)
    hub.setdefault("last_edited", None)

    return hub

def merge_and_score(input_filename, output_filename):
    filepath = os.path.join(DATA_DIR, input_filename)
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found. Skipping merge.")
        return

    with open(filepath, 'r') as f:
        data = json.load(f)

    final_data = []
    for hub in data:
        final_data.append(process_hub(hub))

    out_filepath = os.path.join(DATA_DIR, output_filename)
    with open(out_filepath, 'w') as f:
        json.dump(final_data, f, indent=2)

    print(f"Generated {output_filename} with {len(final_data)} hubs.")

def main():
    print("Merging data and assigning final scores...")
    merge_and_score("rail_stations_with_entrances.json", "rail_stations.json")
    merge_and_score("coach_terminals_with_entrances.json", "coach_terminals.json")
    merge_and_score("park_and_ride_with_entrances.json", "park_and_ride.json")
    print("Pipeline complete.")

if __name__ == "__main__":
    main()
