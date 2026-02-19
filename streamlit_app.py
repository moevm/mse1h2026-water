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


# Validation regular expression
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
        return False, "Введите оба числа в формате 60.123456"
    if not (-90 <= lat <= 90):
        return False, "Широта должна быть от -90 до 90"
    if not (-180 <= lon <= 180):
        return False, "Долгота должна быть от -180 до 180"
    return True, ""


def reset_coords():
    st.session_state["lat_text"] = ""
    st.session_state["lon_text"] = ""
    st.session_state["result_text"] = ""
    st.session_state["submitted"] = False
    st.session_state["error_text"] = ""


def try_precheck_running():
    st.session_state.submitted = True
    lat_val = parse_float(st.session_state.lat_text)
    lon_val = parse_float(st.session_state.lon_text)
    ok, err = validate_coords(lat_val, lon_val)
    if ok:
        st.session_state.result_text = run_analysis(Coords(lat=lat_val, lon=lon_val))
        st.session_state.error_text = ""
    else:
        st.session_state.result_text = ""
        st.session_state.error_text = err

def run_analysis(coords: Coords) -> str:
    return (
        f"✅ Тип водоёма: озеро\n\n"
        f"📊 ИЗВ: 0.20\n\n"
        f"📍 Координаты: {coords.lat:.6f}, {coords.lon:.6f}"
    )

# --- session state defaults ---
if "lat_text" not in st.session_state:
    st.session_state.lat_text = ""
if "lon_text" not in st.session_state:
    st.session_state.lon_text = ""
if "result_text" not in st.session_state:
    st.session_state.result_text = ""
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "error_text" not in st.session_state:
    st.session_state.error_text = ""

# UI
st.title("🧭 Анализ по координатам")
st.write("Введите широту и долготу и нажмите кнопку ниже.")

col1, col2 = st.columns(2)

with col1:
    st.text_input("Широта", key="lat_text", placeholder="например: 60.123456")

with col2:
    st.text_input("Долгота", key="lon_text", placeholder="например: 30.123456")

# кнопки
b1, b2 = st.columns([1, 1])
with b1:
    analyze_clicked = st.button("🔎 Проанализировать", use_container_width=True, on_click=try_precheck_running)
with b2:
    reset_clicked = st.button("↩️ Сбросить координаты", use_container_width=True, on_click=reset_coords)

if st.session_state.error_text:
    st.warning(st.session_state.error_text)

if st.session_state.result_text:
    st.success("Анализ выполнен!")
    st.markdown(st.session_state.result_text)
