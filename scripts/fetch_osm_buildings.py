"""Fetch the real OSM building footprints required by the Thrissur Phase 1 run."""
from __future__ import annotations

import json
from pathlib import Path

import requests


BBOX = "10.5100,76.2050,10.5300,76.2250"  # south, west, north, east
QUERY = f"""[out:json][timeout:60];
(way[\"building\"]({BBOX});relation[\"building\"]({BBOX}););
out tags geom;"""
ENDPOINTS = ("https://overpass.private.coffee/api/interpreter", "https://overpass-api.de/api/interpreter")


def main() -> None:
    payload = None
    last_error: Exception | None = None
    for endpoint in ENDPOINTS:
        try:
            response = requests.get(endpoint, params={"data": QUERY}, timeout=80, headers={"User-Agent": "AgniGeo/0.1 (research pipeline)"})
            response.raise_for_status()
            payload = response.json()
            print(f"Downloaded OSM data from {endpoint}")
            break
        except requests.RequestException as exc:
            last_error = exc
    if payload is None:
        raise RuntimeError("All Overpass endpoints failed") from last_error

    features = []
    for element in payload["elements"]:
        points = element.get("geometry", [])
        if len(points) < 4:
            continue
        ring = [[point["lon"], point["lat"]] for point in points]
        if ring[0] != ring[-1]:
            ring.append(ring[0])
        features.append({"type": "Feature", "properties": element.get("tags", {}), "geometry": {"type": "Polygon", "coordinates": [ring]}})
    output = Path("data/raw/osm/thrissur/buildings.geojson")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
    print(f"Wrote {len(features)} real OSM building footprints to {output}")


if __name__ == "__main__":
    main()
