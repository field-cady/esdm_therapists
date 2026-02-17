#!/usr/bin/env python3
"""
Geocodes rows in data.tsv using Nominatim (OpenStreetMap) and outputs
data_w_latlon.tsv with added 'lat' and 'lon' columns.
"""

import csv
import time
import urllib.request
import urllib.parse
import json
import sys

INPUT_FILE = "data.tsv"
OUTPUT_FILE = "data_w_latlon.tsv"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "geo-enrichment-script/1.0"
RATE_LIMIT_SECONDS = 1.1  # Nominatim asks for max 1 req/sec; slight buffer


def nominatim_search(query_params: dict) -> tuple[float, float] | None:
    """
    Call Nominatim with the given params dict.
    Returns (lat, lon) floats or None if not found.
    """
    params = {**query_params, "format": "json", "limit": 1}
    url = f"{NOMINATIM_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            results = json.loads(resp.read().decode())
            if results:
                return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception as e:
        print(f"  [error] Request failed: {e}", file=sys.stderr)
    return None


def geocode_row(city: str, state: str, country: str) -> tuple[float, float] | None:
    """
    Try multiple query strategies from most to least specific,
    stopping as soon as we get a result.
    """
    city = city.strip()
    state = state.strip()
    country = country.strip()

    # Decide whether state is useful:
    # If state == country or state == city (case-insensitive), skip it.
    state_is_useful = (
        state
        and state.lower() != country.lower()
        and state.lower() != city.lower()
    )

    strategies = []

    # 1. Structured query: city + state + country (if state is useful)
    if state_is_useful:
        strategies.append({
            "city": city,
            "state": state,
            "country": country,
        })

    # 2. Structured query: city + country (no state)
    strategies.append({
        "city": city,
        "country": country,
    })

    # 3. Free-text query: "City, State, Country" (if state is useful)
    if state_is_useful:
        strategies.append({"q": f"{city}, {state}, {country}"})

    # 4. Free-text query: "City, Country"
    strategies.append({"q": f"{city}, {country}"})

    for params in strategies:
        time.sleep(RATE_LIMIT_SECONDS)
        result = nominatim_search(params)
        if result:
            return result

    return None


def main():
    # Read input
    try:
        with open(INPUT_FILE, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            fieldnames = reader.fieldnames
            if not fieldnames:
                print("ERROR: Could not read column names from input file.")
                sys.exit(1)
            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: '{INPUT_FILE}' not found in the current directory.")
        sys.exit(1)

    # Validate required columns
    for col in ("Country", "City", "State"):
        if col not in fieldnames:
            print(f"ERROR: Required column '{col}' not found in {INPUT_FILE}.")
            sys.exit(1)

    out_fieldnames = list(fieldnames) + ["lat", "lon"]
    total = len(rows)
    not_found = []

    print(f"Geocoding {total} rows...\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fieldnames, delimiter="\t")
        writer.writeheader()

        for i, row in enumerate(rows, start=1):
            city    = row.get("City", "")
            state   = row.get("State", "")
            country = row.get("Country", "")

            print(f"[{i}/{total}] {city}, {state}, {country} ... ", end="", flush=True)

            result = geocode_row(city, state, country)

            if result:
                lat, lon = result
                row["lat"] = lat
                row["lon"] = lon
                print(f"{lat}, {lon}")
            else:
                row["lat"] = ""
                row["lon"] = ""
                not_found.append(f"{city}, {state}, {country}")
                print("NOT FOUND")

            writer.writerow(row)

    print(f"\nDone! Output written to '{OUTPUT_FILE}'.")
    if not_found:
        print(f"\n{len(not_found)} row(s) could not be geocoded:")
        for entry in not_found:
            print(f"  - {entry}")


if __name__ == "__main__":
    main()