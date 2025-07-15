#!/usr/bin/env python3
"""
POI-Harvester CLI Tool
Command-line interface for fetching POI data via Overpass API
"""

import argparse
import os
import sys
from typing import List, Optional

# Import modules
from .geocoding import geocode_location
from .utils import get_bbox, generate_filename, parse_column_mapping, clean_poi_data
from .poi_types import POI_DISPLAY_MAPPING, list_poi_types
from .overpass import fetch_poi_data, validate_poi_types
from .export import export_csv, export_sql, export_json, get_all_keys_from_data

def main():
    parser = argparse.ArgumentParser(
        description="POI-Harvester CLI Tool - Fetch POI data from OpenStreetMap",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --location "Berlin" --radius 1.5 --poi-types pharmacy --format csv
  %(prog)s --location "63571" --radius 2 --poi-types bakery --format sql --table-name bakeries
  %(prog)s --bbox 50.0 8.0 50.1 8.1 --poi-types restaurant cafe --format json
        """
    )

    # Location arguments
    location_group = parser.add_mutually_exclusive_group(required=True)
    location_group.add_argument(
        "--location",
        help="Location name or postal code (e.g., 'Berlin', '63571')"
    )
    location_group.add_argument(
        "--bbox",
        nargs=4,
        metavar=("S", "W", "N", "E"),
        type=float,
        help="Bounding box coordinates (south, west, north, east)"
    )

    parser.add_argument(
        "--radius",
        type=float,
        default=1.0,
        help="Search radius in km (default: 1.0, only used with --location)"
    )

    # POI selection
    parser.add_argument(
        "--keys",
        nargs="+",
        default=["name"],
        help="OSM keys to export (default: ['name'])"
    )

    parser.add_argument(
        "--poi-types",
        nargs="+",
        choices=list(POI_DISPLAY_MAPPING.keys()),
        default=["restaurant"],
        help="POI types to fetch (default: ['restaurant'])"
    )

    parser.add_argument(
        "--osm-types",
        nargs="+",
        choices=["node", "way", "relation"],
        default=["node", "way"],
        help="OSM object types to query (default: ['node', 'way'])"
    )

    # Export options
    parser.add_argument(
        "--format",
        choices=["csv", "sql", "json"],
        default="csv",
        help="Export format (default: csv)"
    )

    parser.add_argument(
        "--output",
        help="Output file path (auto-generated if not specified)"
    )

    parser.add_argument(
        "--table-name",
        default="poi_data",
        help="SQL table name (default: poi_data, only used with --format sql)"
    )

    parser.add_argument(
        "--column-map",
        default="",
        help="Column mapping for SQL export (e.g., 'name=poi_name website=url')"
    )

    # Additional options
    parser.add_argument(
        "--list-poi-types",
        action="store_true",
        help="List available POI types and exit"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress status messages"
    )

    parser.add_argument(
        "--all-keys",
        action="store_true",
        help="Export all available keys from the data"
    )

    args = parser.parse_args()

    # List POI types if requested
    if args.list_poi_types:
        list_poi_types()
        return 0

    # Redirect stderr to null if quiet mode
    if args.quiet:
        sys.stderr = open(os.devnull, 'w')

    # Validate POI types
    valid_poi_types = validate_poi_types(args.poi_types)
    if not valid_poi_types:
        print("Error: No valid POI types specified", file=sys.stderr)
        return 1

    # Determine bounding box
    if args.location:
        coords = geocode_location(args.location)
        if not coords:
            print(f"Error: Failed to geocode location '{args.location}'", file=sys.stderr)
            return 1

        lat, lon = coords
        bbox = get_bbox(lat, lon, args.radius)
        location_for_filename = args.location
    else:
        bbox = tuple(args.bbox)
        # Use coordinates for filename if no location specified
        location_for_filename = f"{args.bbox[0]}-{args.bbox[1]}-{args.bbox[2]}-{args.bbox[3]}"

    # Fetch data
    data = fetch_poi_data(bbox, valid_poi_types, args.osm_types)
    if not data:
        print("Error: No data retrieved", file=sys.stderr)
        return 1

    # Clean data (remove id and type fields)
    clean_data = clean_poi_data(data)

    # Determine keys to export
    if args.all_keys:
        export_keys = get_all_keys_from_data(clean_data)
        print(f"Exporting all {len(export_keys)} keys found in data", file=sys.stderr)
    else:
        export_keys = args.keys

    # Generate output filename if not specified
    if args.output:
        output_file = args.output
    else:
        output_file = generate_filename(
            location_for_filename,
            args.radius,
            valid_poi_types,
            args.format
        )

    # Export data based on format
    success = False
    if args.format == "csv":
        success = export_csv(clean_data, export_keys, output_file)
    elif args.format == "json":
        success = export_json(clean_data, export_keys, output_file)
    elif args.format == "sql":
        # Parse column mapping
        column_map = parse_column_mapping(args.column_map)
        success = export_sql(clean_data, export_keys, output_file, args.table_name, column_map)

    if not success:
        print("Error: Export failed", file=sys.stderr)
        return 1

    print(f"Successfully exported {len(clean_data)} POIs to {output_file}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())