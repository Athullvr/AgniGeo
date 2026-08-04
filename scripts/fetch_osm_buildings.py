"""Fetch the real OSM building footprints required by the Thrissur Phase 1 run."""
from __future__ import annotations

import json
import argparse
from itertools import product
from pathlib import Path

import requests
import yaml
import numpy as np


ENDPOINTS = ("https://overpass.private.coffee/api/interpreter", "https://overpass-api.de/api/interpreter")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch real OSM building footprints for an AgniGeo city.")
    parser.add_argument("--city", default="thrissur")
    args = parser.parse_args()
    root = Path(__file__).parents[1]
    config = yaml.safe_load((root / "configs/config.yaml").read_text(encoding="utf-8"))
    west, south, east, north = config["cities"][args.city]["bbox"]
    # Kochi is denser than the Thrissur pilot. Query 0.01-degree tiles so one
    # overloaded public Overpass request cannot block the whole acquisition.
    step = 0.01
    lat_edges = np.arange(south, north + step, step).tolist()
    lon_edges = np.arange(west, east + step, step).tolist()
    features = []
    seen_ids: set[int] = set()
    for tile_south, tile_west in product(lat_edges[:-1], lon_edges[:-1]):
        tile_north, tile_east = min(tile_south + step, north), min(tile_west + step, east)
        bbox = f"{tile_south},{tile_west},{tile_north},{tile_east}"
        query = f"""[out:json][timeout:60];way[\"building\"]({bbox});out tags geom;"""
        payload = None
        last_error: Exception | None = None
        for endpoint in ENDPOINTS:
            try:
                response = requests.get(endpoint, params={"data": query}, timeout=80, headers={"User-Agent": "AgniGeo/0.1 (research pipeline)"})
                response.raise_for_status()
                payload = response.json()
                break
            except requests.RequestException as exc:
                last_error = exc
        if payload is None:
            raise RuntimeError(f"All Overpass endpoints failed for tile {bbox}") from last_error
        for element in payload["elements"]:
            if element["id"] in seen_ids:
                continue
            seen_ids.add(element["id"])
            points = element.get("geometry", [])
            if len(points) < 4:
                continue
            ring = [[point["lon"], point["lat"]] for point in points]
            if ring[0] != ring[-1]:
                ring.append(ring[0])
            features.append({"type": "Feature", "properties": element.get("tags", {}), "geometry": {"type": "Polygon", "coordinates": [ring]}})
        print(f"Downloaded OSM tile {bbox} ({len(features)} unique buildings so far)")
    output = root / "data/raw/osm" / args.city / "buildings.geojson"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
    print(f"Wrote {len(features)} real OSM building footprints to {output}")


if __name__ == "__main__":
    main()
