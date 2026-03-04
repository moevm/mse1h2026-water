import requests
import time

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
    is_in({lat},{lon})->.a;
    (
      area.a["natural"="water"];
      area.a["waterway"];
      area.a["natural"="wetland"];
      
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
    
    for attempt in range(3):
        current_url = servers[attempt % len(servers)] 
        
        try:
            response = requests.get(current_url, params={'data': query}, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('elements'):
                return result
                
            tags = data['elements'][0].get('tags', {})
            result["raw_tags"] = tags
            
            if tags.get('natural') == 'wetland':
                result["water_type"] = "болото"
            elif 'waterway' in tags or tags.get('water') in ['river', 'stream', 'canal']:
                result["water_type"] = "река"
            elif tags.get('water') == 'pond':
                result["water_type"] = "пруд"
            elif tags.get('water') == 'lake' or tags.get('natural') == 'water':
                result["water_type"] = "озеро"
                
            result["water_name"] = tags.get('name', tags.get('name:ru', 'Без названия'))
            
            return result
            
        except (requests.exceptions.RequestException, ValueError) as e:
            if attempt == 2:
                result["error"] = f"Ошибка после 3 попыток: {str(e)}"
            else:
                time.sleep(2)

    return result

if __name__ == "__main__":
    test_lat, test_lon = 59.965872971523886, 30.277092720124525 # Координаты в СПб (река Малая Невка)
    info = get_water_type_from_open_data(test_lat, test_lon, radius=50)
    
    if "error" in info:
        print(f"{info['error']}")

    print(f"Определенный тип водоема: {info['water_type']}")
    print(f"Название водоема: {info['water_name']}")
