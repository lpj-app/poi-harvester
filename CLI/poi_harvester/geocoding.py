"""
Geocoding module for POI-Harvester CLI
"""

import requests
import sys
from typing import Optional, Tuple


def geocode_location(query: str) -> Optional[Tuple[float, float]]:
    """
    Geocode a location string to lat/lon coordinates using Nominatim API

    Args:
        query: Location string (e.g., "Berlin", "10115", "New York")

    Returns:
        Tuple of (lat, lon) or None if geocoding failed
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 1
    }

    try:
        res = requests.get(url, params=params, headers={"User-Agent": "POI-Harvester-CLI"})
        res.raise_for_status()
        data = res.json()

        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon

    except requests.RequestException as e:
        print(f"Network error during geocoding: {e}", file=sys.stderr)
    except (ValueError, KeyError, IndexError) as e:
        print(f"Error parsing geocoding response: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Unexpected error during geocoding: {e}", file=sys.stderr)

    return None