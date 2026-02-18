from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Tuple

import streamlit as st


st.set_page_config(
    page_title="Анализ по координатам",
    page_icon="🧭",
    layout="centered",
)


# Validation
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


def validate_coords(lat: Optional[float], lon: Optional[float]) -> Tuple[bool, str]:
    if lat is None or lon is None:
        return False, "Введите числа в формате 60.123456"
    if not (-90 <= lat <= 90):
        return False, "Широта должна быть от -90 до 90"
    if not (-180 <= lon <= 180):
        return False, "Долгота должна быть от -180 до 180"
    return True, ""


def run_analysis(coords: Coords) -> str:
    return (
        f"✅ Тип водоёма: озеро\n"
        f"📊 ИЗВ: 0.20\n\n"
        f"📍 Координаты: {coords.lat:.6f}, {coords.lon:.6f}"
    )


# UI
st.title("🧭 Анализ по координатам")
st.write("Введите широту и долготу и нажмите кнопку ниже.")

col1, col2 = st.columns(2)

with col1:
    lat_text = st.text_input("Широта", placeholder="например: 60.123456")

with col2:
    lon_text = st.text_input("Долгота", placeholder="например: 30.123456")

lat_val = parse_float(lat_text)
lon_val = parse_float(lon_text)

ok, err = validate_coords(lat_val, lon_val)

if not ok and (lat_text or lon_text):
    st.warning(err)

if st.button("🔎 Проанализировать", disabled=not ok):
    coords = Coords(lat=lat_val, lon=lon_val)
    result = run_analysis(coords)

    st.success("Анализ выполнен!")
    st.markdown(result)
