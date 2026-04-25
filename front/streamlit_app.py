from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Optional, Dict, Any
import requests 
import plotly.graph_objects as go
import streamlit as st
import json


st.set_page_config(
    page_title="Анализ по координатам",
    page_icon="🧭",
    layout="centered",
)

st.markdown(
    """
<style>
[data-testid="stDeployButton"],
[data-testid="stAppDeployButton"],
button[aria-label="Deploy"],
button[title="Deploy"] {
    display: none !important;
}
</style>
""",
    unsafe_allow_html=True,
)

FLOAT_RE = re.compile(r"^\s*[-+]?\d+(?:\.\d+)?\s*$")
BACKEND_URL = os.getenv("BACKEND_URL", default="http://localhost:8000")
WATER_INFO_ENDPOINT = f"{BACKEND_URL}/water-info"

@dataclass(frozen=True)
class Coords:
    lat: float
    lon: float


MAP_STYLE_OPTIONS = {
    "Спутник": "satellite",
    "Спутник + улицы": "satellite-streets",
    "Схема": "streets",
}


def parse_float(text: str) -> Optional[float]:
    if text is None or not FLOAT_RE.match(text):
        return None
    try:
        return float(text.strip())
    except ValueError:
        return None


def validate_lat(text: str) -> str:
    value = parse_float(text)
    if value is None:
        return "Введите широту числом в формате 60.123456"
    if not (-90 <= value <= 90):
        return "Широта должна быть от -90 до 90"
    return ""


def validate_lon(text: str) -> str:
    value = parse_float(text)
    if value is None:
        return "Введите долготу числом в формате 30.123456"
    if not (-180 <= value <= 180):
        return "Долгота должна быть от -180 до 180"
    return ""


def reset_coords() -> None:
    st.session_state["lat_text"] = ""
    st.session_state["lon_text"] = ""
    st.session_state["result_text"] = ""
    st.session_state["submitted"] = False
    st.session_state["lat_error"] = ""
    st.session_state["lon_error"] = ""
    st.session_state["map_lat"] = 59.9343
    st.session_state["map_lon"] = 30.3351
    st.session_state["map_zoom"] = 10
    st.session_state["map_style_label"] = "Спутник"
    st.session_state["api_error"] = ""
    st.session_state["geojson_data"] = None
    st.session_state["geojson_coords"] = None 

def update_map_from_input() -> None:
    """Обновляет карту при изменении координат в полях ввода"""
    lat_error = validate_lat(st.session_state["lat_text"])
    lon_error = validate_lon(st.session_state["lon_text"])

    st.session_state["lat_error"] = lat_error
    st.session_state["lon_error"] = lon_error

    # Обновляем карту только если оба значения валидны
    if not lat_error and not lon_error:
        lat_val = parse_float(st.session_state["lat_text"])
        lon_val = parse_float(st.session_state["lon_text"])
        
        if lat_val is not None and lon_val is not None:
            st.session_state["map_lat"] = lat_val
            st.session_state["map_lon"] = lon_val

def try_precheck_running() -> None:
    st.session_state["submitted"] = True

    lat_error = validate_lat(st.session_state["lat_text"])
    lon_error = validate_lon(st.session_state["lon_text"])

    st.session_state["lat_error"] = lat_error
    st.session_state["lon_error"] = lon_error

    if lat_error or lon_error:
        st.session_state["result_text"] = ""
        return

    lat_val = parse_float(st.session_state["lat_text"])
    lon_val = parse_float(st.session_state["lon_text"])

    if lat_val is None or lon_val is None:
        st.session_state["result_text"] = ""
        return

    st.session_state["map_lat"] = lat_val
    st.session_state["map_lon"] = lon_val
    result = run_analysis(Coords(lat=lat_val, lon=lon_val))
    
    if result:
        st.session_state["result_text"] = result
        st.session_state["api_error"] = ""
    else:
        st.session_state["result_text"] = ""
        st.session_state["api_error"] = "Не удалось получить данные с сервера"

def get_water_info_from_backend(coords: Coords) -> Optional[Dict[str, Any]]:
    try:
        response = requests.get(
            WATER_INFO_ENDPOINT,
            params={
                "lat": coords.lat,
                "lon": coords.lon
            },
            timeout=60  
        )
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.ConnectionError:
        st.error(" Не удалось подключиться к серверу. Проверьте, запущен ли бэкенд.")
        return None
    except requests.exceptions.Timeout:
        st.error(" Превышено время ожидания ответа от сервера.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f" Ошибка сервера: {e}")
        return None
    except Exception as e:
        st.error(f" Неизвестная ошибка: {e}")
        return None
    
def format_result_from_backend(api_response: Dict[str, Any], coords: Coords) -> str:
    image_path = api_response.get("image_path")
    geojson_path = api_response.get("geojson_path")
    ecological_status = api_response.get("eutrophication_stats")
    
    return (
        f"Изображение: {image_path}\n\n"
        f"GeoJSON: {geojson_path}\n\n"
        f"Экологический статус:\n\n"
        f"```json\n{json.dumps(ecological_status, indent=4, ensure_ascii=False)}\n```\n\n"
        f"Координаты: {coords.lat:.6f}, {coords.lon:.6f}"
    )


def run_analysis(coords: Coords) -> str:
    with st.spinner("Получение данных с сервера..."):
        api_response = get_water_info_from_backend(coords)
    if api_response:
        geojson_data = api_response.get("geojson_path")
        geojson_response = requests.get(geojson_data)
        geojson = geojson_response.json() if geojson_response.status_code == 200 else None
        
        # Сохраняем geojson в session state для отображения на основной карте
        st.session_state["geojson_data"] = geojson
        st.session_state["geojson_coords"] = coords
        
        return format_result_from_backend(api_response, coords)
    else:
        return (
            f"Данные с сервера не получены\n\n" 
        )


def get_color_by_type(feature_type: str) -> str:
    """Возвращает цвет в зависимости от типа"""
    type_color_map = {
        "пруд": "#ffff00",
        "река": "#00ff00",
        "болото": "#ff0000",
        "озеро": "#0000ff",
    }
    return type_color_map.get(str(feature_type).lower(), "#0066cc")


def build_map_figure(lat, lon, zoom, map_style, geojson=None, polygon_alpha: float = 0.6, point_color: str = "#800080"):
    fig = go.Figure()

    if geojson:
        features = geojson["features"]
        
        # Группируем объекты по типам и добавляем отдельный trace для каждого типа
        types = {}
        for f in features:
            feature_type = f["properties"].get("type", "unknown")
            if feature_type not in types:
                types[feature_type] = []
            types[feature_type].append(f)
        
        for feature_type, type_features in types.items():
            color = get_color_by_type(feature_type)

            # Convert hex color to rgba string with requested alpha
            def hex_to_rgba(hex_color: str, alpha: float) -> str:
                hex_color = hex_color.lstrip("#")
                if len(hex_color) == 3:
                    hex_color = "".join([c*2 for c in hex_color])
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return f"rgba({r}, {g}, {b}, {alpha})"

            rgba = hex_to_rgba(color, max(0.0, min(1.0, polygon_alpha)))

            fig.add_trace(go.Choroplethmap(
                geojson={"type": "FeatureCollection", "features": type_features},
                locations=[f["properties"].get("id", i) for i, f in enumerate(type_features)],
                z=[1] * len(type_features),
                featureidkey="properties.id",
                name=feature_type,

                customdata=[
                    [
                        f["properties"].get("id"),
                        f["properties"].get("area_pixels"),
                        f["properties"].get("elongation"),
                        f["properties"].get("lon"),
                        f["properties"].get("lat"),
                    ]
                    for f in type_features
                ],

                hovertemplate=(
                    "ID: %{customdata[0]}<br>"
                    # "Тип: %{customdata[1]}<br>"
                    "Площадь (пиксели): %{customdata[1]}<br>"
                    "Элонгация: %{customdata[2]}<br>"
                    "Координаты: %{customdata[3]:.6f}, %{customdata[4]:.6f}<br>"
                ),

                colorscale=[[0, rgba], [1, rgba]],
                zmin=0,
                zmax=1,
                showscale=False,
            ))

    fig.add_trace(go.Scattermap(
        lat=[lat],
        lon=[lon],
        mode="markers",
        marker={"size": 16, "color": point_color},
        text=[f"Точка: {lat:.6f}, {lon:.6f}"],
        hoverinfo="text",
    ))


    fig.update_layout(
        map={
            "style": map_style,
            "center": {"lat": lat, "lon": lon},
            "zoom": zoom,
        },
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=500,
        showlegend=False,
    )

    return fig


if "lat_text" not in st.session_state:
    st.session_state["lat_text"] = ""
if "lon_text" not in st.session_state:
    st.session_state["lon_text"] = ""
if "result_text" not in st.session_state:
    st.session_state["result_text"] = ""
if "submitted" not in st.session_state:
    st.session_state["submitted"] = False
if "lat_error" not in st.session_state:
    st.session_state["lat_error"] = ""
if "lon_error" not in st.session_state:
    st.session_state["lon_error"] = ""
if "map_lat" not in st.session_state:
    st.session_state["map_lat"] = 59.9343
if "map_lon" not in st.session_state:
    st.session_state["map_lon"] = 30.3351
if "map_zoom" not in st.session_state:
    st.session_state["map_zoom"] = 10
if "map_style_label" not in st.session_state:
    st.session_state["map_style_label"] = "Спутник"
if "api_error" not in st.session_state:
    st.session_state["api_error"] = ""
if "geojson_data" not in st.session_state:
    st.session_state["geojson_data"] = None
if "geojson_coords" not in st.session_state:
    st.session_state["geojson_coords"] = None


st.title("🧭 Анализ по координатам")
st.write("Введите широту и долготу вручную. Карта ниже обновится по выбранной точке.")

@st.cache_data(ttl=60) 
def check_backend_health():
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False
if check_backend_health():
    st.sidebar.success("Бэкенд подключен")
else:
    st.sidebar.error("Бэкенд не отвечает")

col1, col2 = st.columns(2)

with col1:
    st.text_input(
        "Широта",
        key="lat_text",
        placeholder="например: 60.123456",
        on_change=update_map_from_input,
    )
    if st.session_state["lat_error"]:
        st.error(st.session_state["lat_error"])

with col2:
    st.text_input(
        "Долгота",
        key="lon_text",
        placeholder="например: 30.123456",
        on_change=update_map_from_input,
    )
    if st.session_state["lon_error"]:
        st.error(st.session_state["lon_error"])

b1, b2 = st.columns([1, 1])

with b1:
    st.button(
        "🔎 Проанализировать",
        width="stretch",
        on_click=try_precheck_running,
    )

with b2:
    st.button(
        "↩️ Сбросить координаты",
        width="stretch",
        on_click=reset_coords,
    )
if st.session_state.get("api_error"):
    st.warning(st.session_state["api_error"])

if st.session_state["result_text"]:
    st.success("Анализ выполнен!")

st.markdown("---")
st.subheader("🗺️ Карта")

st.selectbox(
    "Тип отображения карты",
    options=list(MAP_STYLE_OPTIONS.keys()),
    key="map_style_label",
)

selected_map_style = MAP_STYLE_OPTIONS[st.session_state["map_style_label"]]

# Используем сохраненный geojson или None если его нет
geojson_to_display = st.session_state.get("geojson_data")

fig = build_map_figure(
    lat=st.session_state["map_lat"],
    lon=st.session_state["map_lon"],
    zoom=st.session_state["map_zoom"],
    map_style=selected_map_style,
    geojson=geojson_to_display,
)

st.plotly_chart(
    fig,
    width="stretch",
    config={
        "scrollZoom": True,
        "displayModeBar": False,
    },
)

if st.session_state["result_text"]:
    st.markdown(st.session_state["result_text"])
