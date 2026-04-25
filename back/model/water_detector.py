import requests
import time


SERVERS = [
    "http://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
]

HEADERS = {
    "User-Agent": "Water/1.0 (Project)",
}


def _build_query(lat: float, lon: float, radius: int) -> str:
    return f"""
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


def _init_result(lat: float, lon: float) -> dict:
    return {
        "coordinates": {"lat": lat, "lon": lon},
        "source": "OpenStreetMap",
        "water_type": "Неизвестно",
        "water_name": "Неизвестно",
        "raw_tags": {},
    }


def _get_tags(data: dict) -> dict:
    elements = data.get("elements")
    if not elements:
        return {}
    return elements[0].get("tags", {})


def _resolve_type(tags: dict) -> str:
    if tags.get("natural") == "wetland":
        return "болото"
    if "waterway" in tags or tags.get("water") in ["river", "stream", "canal"]:
        return "река"
    if tags.get("water") == "pond":
        return "пруд"
    if tags.get("water") == "lake" or tags.get("natural") == "water":
        return "озеро"
    return "Неизвестно"


def _resolve_name(tags: dict) -> str:
    return tags.get("name", tags.get("name:ru", "Без названия"))


def _fetch_data(url: str, query: str) -> dict:
    response = requests.get(
        url,
        params={"data": query},
        headers=HEADERS,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def _apply_tags(result: dict, tags: dict) -> None:
    result["raw_tags"] = tags
    result["water_type"] = _resolve_type(tags)
    result["water_name"] = _resolve_name(tags)


def _process_response(url: str, query: str, result: dict) -> None:
    data = _fetch_data(url, query)
    tags = _get_tags(data)
    if not tags:
        return
    _apply_tags(result, tags)


def get_water_type_from_open_data(lat: float, lon: float, radius: int = 50) -> dict:
    """
    Определяет тип водоема по координатам с использованием Overpass API.
    """
    query = _build_query(lat, lon, radius)
    result = _init_result(lat, lon)

    for attempt in range(3):
        current_url = SERVERS[attempt % len(SERVERS)]
        try:
            _process_response(current_url, query, result)
            return result

        except (requests.exceptions.RequestException, ValueError) as e:
            if attempt == 2:
                result["error"] = f"Ошибка после 3 попыток: {str(e)}"
            else:
                time.sleep(2)

    return result


if __name__ == "__main__":
    test_lat, test_lon = 59.965872971523886, 30.277092720124525  # Координаты в СПб (река Малая Невка)
    info = get_water_type_from_open_data(test_lat, test_lon, radius=50)

    if "error" in info:
        print(f"{info['error']}")

    print(f"Определенный тип водоема: {info['water_type']}")
    print(f"Название водоема: {info['water_name']}")
