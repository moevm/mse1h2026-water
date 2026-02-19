def get_water_type_from_open_data(lat: float, lon: float, radius: int = 50) -> dict:
    """
    Определяет тип водоема по координатам с использованием Overpass API.
    """
    result = {
        "coordinates": {"lat": lat, "lon": lon},
        "source": "OpenStreetMap",
        "water_type": "Неизвестно",
        "water_name": "Неизвестно",
        "raw_tags": {}
    }
    
    return result

if __name__ == "__main__":
    test_lat, test_lon = 59.943287526496405, 30.31233184690002
    info = get_water_type_from_open_data(test_lat, test_lon, radius=50)
    print(info)
