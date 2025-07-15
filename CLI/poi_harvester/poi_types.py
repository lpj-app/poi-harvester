"""
POI type definitions for POI-Harvester CLI
"""

# POI type mappings - each POI type maps to list of (key, value) tuples
POI_DISPLAY_MAPPING = {
    # AMENITY – Public facilities and services useful for daily life
    "drinking-water": [("amenity", "drinking_water")],
    "hospital": [("amenity", "hospital")],
    "school": [("amenity", "school")],
    "library": [("amenity", "library")],
    "pharmacy": [("amenity", "pharmacy")],
    "restaurant": [("amenity", "restaurant")],
    "cafe": [("amenity", "cafe")],
    "toilets": [("amenity", "toilets")],
    "bench": [("amenity", "bench")],
    "graveyard": [("amenity", "grave_yard")],
    "bank": [("amenity", "bank")],
    "atm": [("amenity", "atm")],
    "post-office": [("amenity", "post_office")],
    "fuel": [("amenity", "fuel")],
    "parking": [("amenity", "parking")],
    "police": [("amenity", "police")],
    "fire-station": [("amenity", "fire_station")],
    "town-hall": [("amenity", "townhall")],
    "university": [("amenity", "university")],
    "college": [("amenity", "college")],
    "kindergarten": [("amenity", "kindergarten")],
    "clinic": [("amenity", "clinic")],
    "dentist": [("amenity", "dentist")],
    "veterinary": [("amenity", "veterinary")],
    "place-of-worship": [("amenity", "place_of_worship")],

    # LEISURE – Recreational and entertainment facilities
    "fitness-centre": [("leisure", "fitness_centre")],
    "park": [("leisure", "park")],
    "playground": [("leisure", "playground")],
    "swimming-pool": [("leisure", "swimming_pool")],
    "dog-park": [("leisure", "dog_park")],
    "stadium": [("leisure", "stadium")],
    "sports-centre": [("leisure", "sports_centre")],
    "golf-course": [("leisure", "golf_course")],
    "marina": [("leisure", "marina")],
    "garden": [("leisure", "garden")],
    "nature-reserve": [("leisure", "nature_reserve")],
    "beach": [("leisure", "beach_resort")],
    "picnic-table": [("leisure", "picnic_table")],

    # SHOP – Retail stores and commercial outlets
    "supermarket": [("shop", "supermarket")],
    "bakery": [("shop", "bakery")],
    "hairdresser": [("shop", "hairdresser")],
    "clothes": [("shop", "clothes")],
    "electronics": [("shop", "electronics")],
    "books": [("shop", "books")],
    "convenience": [("shop", "convenience")],
    "butcher": [("shop", "butcher")],
    "greengrocer": [("shop", "greengrocer")],
    "florist": [("shop", "florist")],
    "hardware": [("shop", "hardware")],
    "bicycle": [("shop", "bicycle")],
    "car": [("shop", "car")],
    "car-repair": [("shop", "car_repair")],
    "optician": [("shop", "optician")],
    "jewelry": [("shop", "jewelry")],
    "gift": [("shop", "gift")],
    "toys": [("shop", "toys")],
    "sports": [("shop", "sports")],
    "shoes": [("shop", "shoes")],
    "furniture": [("shop", "furniture")],
    "department-store": [("shop", "department_store")],
    "mall": [("shop", "mall")],

    # TOURISM – Tourist attractions and services
    "attraction": [("tourism", "attraction")],
    "hotel": [("tourism", "hotel")],
    "hostel": [("tourism", "hostel")],
    "guest-house": [("tourism", "guest_house")],
    "museum": [("tourism", "museum")],
    "gallery": [("tourism", "gallery")],
    "viewpoint": [("tourism", "viewpoint")],
    "information": [("tourism", "information")],
    "artwork": [("tourism", "artwork")],
    "zoo": [("tourism", "zoo")],
    "theme-park": [("tourism", "theme_park")],

    # TRANSPORT – Transportation facilities
    "bus-stop": [("highway", "bus_stop")],
    "railway-station": [("railway", "station")],
    "subway-entrance": [("railway", "subway_entrance")],
    "taxi": [("amenity", "taxi")],
    "bicycle-rental": [("amenity", "bicycle_rental")],
    "car-rental": [("amenity", "car_rental")],
    "ferry-terminal": [("amenity", "ferry_terminal")],
}


def get_poi_categories() -> dict:
    """
    Get POI types organized by categories

    Returns:
        Dictionary with categories as keys and POI types as values
    """
    categories = {
        "Amenities": [],
        "Leisure": [],
        "Shops": [],
        "Tourism": [],
        "Transport": []
    }

    for poi_type, tags in POI_DISPLAY_MAPPING.items():
        if not tags:
            continue

        key = tags[0][0]  # First tag key
        if key == "amenity":
            categories["Amenities"].append(poi_type)
        elif key == "leisure":
            categories["Leisure"].append(poi_type)
        elif key == "shop":
            categories["Shops"].append(poi_type)
        elif key == "tourism":
            categories["Tourism"].append(poi_type)
        elif key in ["highway", "railway"]:
            categories["Transport"].append(poi_type)
        else:
            categories["Amenities"].append(poi_type)  # Default category

    return categories


def list_poi_types() -> None:
    """Print all available POI types organized by category"""
    categories = get_poi_categories()

    print("Available POI types by category:")
    print("=" * 40)

    for category, poi_types in categories.items():
        if poi_types:
            print(f"\n{category}:")
            for poi_type in sorted(poi_types):
                tags = POI_DISPLAY_MAPPING[poi_type]
                tag_str = ", ".join([f"{key}={value}" for key, value in tags])
                print(f"  {poi_type:<20} ({tag_str})")