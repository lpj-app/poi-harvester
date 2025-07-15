"""
Utility functions for POI-Harvester CLI
"""

from typing import Tuple, List, Dict

def get_bbox(lat: float, lon: float, radius_km: float) -> Tuple[float, float, float, float]:
    """
    Calculate bounding box from center point and radius

    Args:
        lat: Latitude of center point
        lon: Longitude of center point
        radius_km: Radius in kilometers

    Returns:
        Tuple of (south, west, north, east) coordinates
    """
    delta = radius_km / 111  # rough conversion from km to degrees
    return lat - delta, lon - delta, lat + delta, lon + delta


def generate_filename(location: str, radius: float, poi_types: List[str], format_ext: str) -> str:
    """
    Generate filename in format: poi-harvester_location_radius_poi-types.ext

    Args:
        location: Location string (postal code or city name)
        radius: Radius in km
        poi_types: List of selected POI types
        format_ext: File extension (sql, csv, json)

    Returns:
        Generated filename
    """
    # Clean location string - remove spaces and special characters
    clean_location = location.replace(" ", "").replace(",", "").replace("-", "")

    # Convert radius to integer if it's a whole number
    radius_str = str(int(radius)) if radius == int(radius) else str(radius)

    # Format POI types - join with dash and replace underscores
    poi_type_str = "-".join(poi_types).replace("_", "-")

    return f"poi-harvester_{clean_location}_{radius_str}_{poi_type_str}.{format_ext}"


def parse_column_mapping(mapping_str: str) -> Dict[str, str]:
    """
    Parse column mapping string like 'name=poi_name website=url'

    Args:
        mapping_str: Space-separated key=value pairs

    Returns:
        Dictionary mapping original keys to new column names
    """
    mapping = {}
    if mapping_str:
        for pair in mapping_str.split():
            if '=' in pair:
                key, value = pair.split('=', 1)
                mapping[key] = value
    return mapping


def clean_poi_data(data: List[Dict]) -> List[Dict]:
    """
    Clean POI data by removing id and type fields

    Args:
        data: List of POI dictionaries from Overpass API

    Returns:
        Cleaned data without id and type fields
    """
    cleaned_data = []

    for item in data:
        # Create a copy without id and type fields
        cleaned_item = {}

        # Keep lat/lon (either direct or from center)
        if 'lat' in item and 'lon' in item:
            cleaned_item['lat'] = item['lat']
            cleaned_item['lon'] = item['lon']
        elif 'center' in item:
            cleaned_item['lat'] = item['center'].get('lat')
            cleaned_item['lon'] = item['center'].get('lon')

        # Keep tags
        if 'tags' in item:
            cleaned_item['tags'] = item['tags']

        # Skip items without coordinates
        if cleaned_item.get('lat') is not None and cleaned_item.get('lon') is not None:
            cleaned_data.append(cleaned_item)

    return cleaned_data