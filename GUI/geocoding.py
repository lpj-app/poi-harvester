import requests

def geocode_location(query):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 1
    }
    try:
        res = requests.get(url, params=params, headers={"User-Agent": "POIDataMiner"})
        data = res.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
    except Exception:
        return None
    return None