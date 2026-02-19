import requests

def get_water_type_from_open_data(lat: float, lon: float, radius: int = 50) -> dict:
    """
    Определяет тип водоема по координатам с использованием Overpass API.
    """
    servers = [
        "http://overpass-api.de/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
        "https://z.overpass-api.de/api/interpreter"
    ]
    
    query = f"""
    [out:json];
    (
      way["natural"="water"](around:{radius},{lat},{lon});
      relation["natural"="water"](around:{radius},{lat},{lon});
      way["waterway"](around:{radius},{lat},{lon});
      relation["waterway"](around:{radius},{lat},{lon});
      way["natural"="wetland"](around:{radius},{lat},{lon});
      relation["natural"="wetland"](around:{radius},{lat},{lon});
    );
    out tags;
    """
    
    result = {
        "coordinates": {"lat": lat, "lon": lon},
        "source": "OpenStreetMap",
        "water_type": "Неизвестно",
        "water_name": "Неизвестно",
        "raw_tags": {}
    }

    headers = {
        'User-Agent': 'Water/1.0 (Project)'
    }
    
    current_url = servers[0] 
    response = requests.get(current_url, params={'data': query}, headers=headers, timeout=15)
    response.raise_for_status()
    
    data = response.json()
    if not data.get('elements'):
        return result
        
    tags = data['elements'][0].get('tags', {})
    result["raw_tags"] = tags
    
    return result

if __name__ == "__main__":
    test_lat, test_lon = 59.943287526496405, 30.31233184690002
    info = get_water_type_from_open_data(test_lat, test_lon, radius=50)
    print(info)
