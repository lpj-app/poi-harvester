def get_bbox(lat, lon, radius_km):
    delta = radius_km / 111  # rough conversion from km to degrees
    return lat - delta, lon - delta, lat + delta, lon + delta
