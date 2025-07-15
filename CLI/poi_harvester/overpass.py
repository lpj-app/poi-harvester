"""
Overpass API module for POI-Harvester CLI
"""

import requests
import sys
from typing import List, Dict, Tuple
from .poi_types import POI_DISPLAY_MAPPING


def build_overpass_query(bbox: Tuple[float, float, float, float],
                         poi_types: List[str],
                         osm_types: List[str]) -> str:
    """
    Build Overpass API query string

    Args:
        bbox: Bounding box (south, west, north, east)
        poi_types: List of POI types to query
        osm_types: List of OSM object types (node, way, relation)

    Returns:
        Overpass query string
    """
    s, w, n, e = bbox

    query_parts = []
    for poi_type in poi_types:
        if poi_type in POI_DISPLAY_MAPPING:
            for key, value in POI_DISPLAY_MAPPING[poi_type]:
                for osm_type in osm_types:
                    query_parts.append(f'{osm_type}["{key}"="{value}"]({s},{w},{n},{e});')

    if not query_parts:
        return ""

    query_body = "\n  ".join(query_parts)
    query = f"""
[out:json][timeout:25];
(
  {query_body}
);
out center;
"""

    return query


def fetch_poi_data(bbox: Tuple[float, float, float, float],
                   poi_types: List[str],
                   osm_types: List[str]) -> List[Dict]:
    """
    Fetch POI data from Overpass API

    Args:
        bbox: Bounding box (south, west, north, east)
        poi_types: List of POI types to query
        osm_types: List of OSM object types (node, way, relation)

    Returns:
        List of POI dictionaries
    """
    query = build_overpass_query(bbox, poi_types, osm_types)

    if not query:
        print("No valid POI types selected.", file=sys.stderr)
        return []

    try:
        print("Fetching data from Overpass API...", file=sys.stderr)
        response = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query},
            headers={"User-Agent": "POI-Harvester-CLI"},
            timeout=30
        )
        response.raise_for_status()

        data = response.json().get("elements", [])
        print(f"Found {len(data)} POIs", file=sys.stderr)
        return data

    except requests.exceptions.Timeout:
        print("Request to Overpass API timed out", file=sys.stderr)
    except requests.exceptions.RequestException as e:
        print(f"Network error during Overpass query: {e}", file=sys.stderr)
    except ValueError as e:
        print(f"Error parsing Overpass response: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Unexpected error during Overpass query: {e}", file=sys.stderr)

    return []


def validate_poi_types(poi_types: List[str]) -> List[str]:
    """
    Validate and filter POI types

    Args:
        poi_types: List of POI type strings

    Returns:
        List of valid POI types
    """
    valid_types = []
    invalid_types = []

    for poi_type in poi_types:
        if poi_type in POI_DISPLAY_MAPPING:
            valid_types.append(poi_type)
        else:
            invalid_types.append(poi_type)

    if invalid_types:
        print(f"Warning: Invalid POI types ignored: {', '.join(invalid_types)}", file=sys.stderr)

    return valid_types