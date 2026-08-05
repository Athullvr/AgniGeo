"""Fetch the real OSM building footprints required by the Thrissur Phase 1 run."""
from __future__ import annotations

import json
import argparse
from itertools import product
from pathlib import Path
from xml.etree import ElementTree

import requests
import yaml
import numpy as np


ENDPOINTS = ("https://overpass.private.coffee/api/interpreter", "https://overpass-api.de/api/interpreter")
OSM_MAP_ENDPOINT = "https://api.openstreetmap.org/api/0.6/map"


def osm_api_features(xml_bytes: bytes, seen_ids: set[int]) -> list[dict]:
    """Convert building ways from an official OSM API map response to GeoJSON."""
    root = ElementTree.fromstring(xml_bytes)
    nodes = {node.attrib["id"]: (float(node.attrib["lon"]), float(node.attrib["lat"])) for node in root.findall("node")}
    features = []
    for way in root.findall("way"):
        tags = {tag.attrib["k"]: tag.attrib["v"] for tag in way.findall("tag")}
        way_id = int(way.attrib["id"])
        if "building" not in tags or way_id in seen_ids:
            continue
        ring = [list(nodes[ref.attrib["ref"]]) for ref in way.findall("nd") if ref.attrib["ref"] in nodes]
        if len(ring) < 3:
            continue
        seen_ids.add(way_id)
        if ring[0] != ring[-1]:
            ring.append(ring[0])
        features.append({"type": "Feature", "properties": tags, "geometry": {"type": "Polygon", "coordinates": [ring]}})
    return features


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
    # Use start coordinates only: adding ``step`` to an inclusive endpoint can
    # create a floating-point, zero-width tile at the eastern/northern edge.
    lat_starts = np.arange(south, north - 1e-10, step).tolist()
    lon_starts = np.arange(west, east - 1e-10, step).tolist()
    features = []
    seen_ids: set[int] = set()
    for tile_south, tile_west in product(lat_starts, lon_starts):
        tile_north, tile_east = min(tile_south + step, north), min(tile_west + step, east)
        bbox = f"{tile_south},{tile_west},{tile_north},{tile_east}"
        # Prefer the official OSM API for small tiles. It is usually more
        # reliable than a shared Overpass server for this 0.03° research area.
        response = requests.get(
            OSM_MAP_ENDPOINT,
            params={"bbox": f"{tile_west},{tile_south},{tile_east},{tile_north}"},
            timeout=60,
            headers={"User-Agent": "AgniGeo/0.1 (research pipeline)"},
        )
        if response.ok:
            features.extend(osm_api_features(response.content, seen_ids))
            print(f"Downloaded OSM API tile {bbox} ({len(features)} unique buildings so far)", flush=True)
            continue
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
        print(f"Downloaded Overpass tile {bbox} ({len(features)} unique buildings so far)", flush=True)
    output = root / "data/raw/osm" / args.city / "buildings.geojson"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
    print(f"Wrote {len(features)} real OSM building footprints to {output}")


if __name__ == "__main__":
    main()
