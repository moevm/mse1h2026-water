from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

import streamlit as st


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


@dataclass(frozen=True)
class Coords:
    lat: float
    lon: float


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


def try_precheck_running() -> None:
    st.session_state.submitted = True

    lat_error = validate_lat(st.session_state.lat_text)
    lon_error = validate_lon(st.session_state.lon_text)

    st.session_state.lat_error = lat_error
    st.session_state.lon_error = lon_error

    if lat_error or lon_error:
        st.session_state.result_text = ""
        return

    lat_val = parse_float(st.session_state.lat_text)
    lon_val = parse_float(st.session_state.lon_text)

    st.session_state.result_text = run_analysis(Coords(lat=lat_val, lon=lon_val))


def run_analysis(coords: Coords) -> str:
    return (
        f"✅ Тип водоёма: озеро\n\n"
        f"📊 ИЗВ: 0.20\n\n"
        f"📍 Координаты: {coords.lat:.6f}, {coords.lon:.6f}"
    )


if "lat_text" not in st.session_state:
    st.session_state.lat_text = ""
if "lon_text" not in st.session_state:
    st.session_state.lon_text = ""
if "result_text" not in st.session_state:
    st.session_state.result_text = ""
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "lat_error" not in st.session_state:
    st.session_state.lat_error = ""
if "lon_error" not in st.session_state:
    st.session_state.lon_error = ""


st.title("🧭 Анализ по координатам")
st.write("Введите широту и долготу и нажмите кнопку ниже.")

col1, col2 = st.columns(2)

with col1:
    st.text_input("Широта", key="lat_text", placeholder="например: 60.123456")
    if st.session_state.lat_error:
        st.error(st.session_state.lat_error)

with col2:
    st.text_input("Долгота", key="lon_text", placeholder="например: 30.123456")
    if st.session_state.lon_error:
        st.error(st.session_state.lon_error)

b1, b2 = st.columns([1, 1])

with b1:
    st.button(
        "🔎 Проанализировать",
        use_container_width=True,
        on_click=try_precheck_running,
    )

with b2:
    st.button(
        "↩️ Сбросить координаты",
        use_container_width=True,
        on_click=reset_coords,
    )

if st.session_state.result_text:
    st.success("Анализ выполнен!")
    st.markdown(st.session_state.result_text)