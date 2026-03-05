# Hub Confirm
**UK Transport Hub Pin-Placement Tool**

A mobile-first, static web application allowing a single operator to manually confirm the exact GPS coordinates of UK transport hubs by placing a pin on a map.

## Setup Instructions

### Local Development
To run this project locally, simply clone the repository and start a static web server from the root directory:
```bash
python -m http.server 8000
```
Then visit `http://localhost:8000` in your web browser.

### GitHub Pages Setup
1. Go to your repository **Settings**.
2. Navigate to the **Pages** section.
3. Under **Source**, select the `main` branch.
4. Save the configuration. GitHub will provide a link to the live app.

### Running Data Scripts
The `.github/workflows/scrape.yml` file is configured to run the scraper and geocoder scripts monthly or on-demand to fetch new station data.

You can also run them locally:
```bash
python scripts/scrape_wikipedia.py
python scripts/geocode_nominatim.py
```

## Operator Notes
Here are the answers to some of the specific assumptions made during development:
1. **Map tiles:** The tool defaults to OpenStreetMap standard tiles and Esri Satellite/Aerial map tiles. No API key is required and there are no usage limits.
2. **P&R source:** The scraper uses `parkandride.net` as the primary source, but this logic can easily be customized in `scripts/scrape_wikipedia.py`.
3. **Station Size:** Category is left to the operator during pinning, though initial categories are loaded from the JSON data.
4. **Coach terminals:** Car park pins are an available entrance option, but "has car park" must be enabled for it to appear, allowing flexibility based on each terminal.
5. **"Unsure" on has_car_park:** Setting `has_car_park: null` blocks marking the station as "Complete". It must explicitly be "Yes" or "No" to allow final submission.
