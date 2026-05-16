from typing import Dict, Any, List, Optional

LEVEL_OK = "ok"
LEVEL_NOTICE = "notice"
LEVEL_WARNING = "warning"
LEVEL_CRITICAL = "critical"

LEVEL_LABELS = {
    LEVEL_OK: "норма",
    LEVEL_NOTICE: "внимание",
    LEVEL_WARNING: "тревога",
    LEVEL_CRITICAL: "критично",
}

LEVEL_COLORS = {
    LEVEL_OK: "#2e7d32",
    LEVEL_NOTICE: "#f9a825",
    LEVEL_WARNING: "#ef6c00",
    LEVEL_CRITICAL: "#c62828",
}

_NDCI_RULES: Dict[str, List[tuple]] = {
    "озеро": [
        (0.1, LEVEL_OK, "чистая вода, биомасса в норме"),
        (0.3, LEVEL_NOTICE, "повышенное содержание хлорофилла, начало роста биомассы"),
        (0.7, LEVEL_WARNING, "тревога: озеро может зацвести, вода стоячая"),
        (None, LEVEL_CRITICAL, "активное цветение, высокий риск замора рыбы"),
    ],
    "пруд": [
        (0.1, LEVEL_OK, "норма для пруда"),
        (0.3, LEVEL_NOTICE, "внимание: малый объем воды быстро накапливает органику"),
        (0.5, LEVEL_WARNING, "серьезный риск зарастания, требуется мониторинг"),
        (None, LEVEL_CRITICAL, "критично: пруд активно цветет, нужно вмешательство"),
    ],
    "река": [
        (0.2, LEVEL_OK, "вода чистая, течение справляется"),
        (0.4, LEVEL_NOTICE, "легкая загрязненность, для проточной воды допустимо"),
        (0.7, LEVEL_WARNING, "критично в затонах и старицах"),
        (None, LEVEL_CRITICAL, "сильное загрязнение даже с учетом течения"),
    ],
    "болото": [
        (0.1, LEVEL_OK, "необычно низкий уровень органики для болота"),
        (0.7, LEVEL_OK, "норма: для болота высокая органика естественна"),
        (0.85, LEVEL_NOTICE, "повышенный фон, но в пределах допустимого для болота"),
        (None, LEVEL_WARNING, "аномально высокий уровень даже для болота"),
    ],
}

_POLLUTED_RULES: Dict[str, List[tuple]] = {
    "озеро": [
        (10, "локальные очаги"),
        (40, "значительная часть акватории затронута"),
        (None, "большая часть акватории затронута"),
    ],
    "пруд": [
        (20, "точечные участки"),
        (60, "значительная часть пруда затронута"),
        (None, "почти весь пруд затронут"),
    ],
    "река": [
        (15, "отдельные участки русла"),
        (50, "загрязнение вдоль большой части русла"),
        (None, "загрязнено почти все русло"),
    ],
    "болото": [
        (50, "обычное распределение"),
        (None, "очень обширная зона повышенной органики"),
    ],
}

def _lookup(value: Optional[float], rules: List[tuple]) -> tuple:
    if value is None:
        return rules[-1]
    for upper, *rest in rules:
        if upper is None or value < upper:
            return (upper, *rest)
    return rules[-1]

def interpret_eutrophication(
    ndci_mean: Optional[float],
    polluted_percentage: Optional[float],
    water_type: str,
) -> Dict[str, Any]:
    water_type = (water_type or "").lower()
    rules = _NDCI_RULES.get(water_type)

    if rules is None:
        return {
            "water_type": water_type or "неизвестно",
            "level": LEVEL_NOTICE,
            "level_label": LEVEL_LABELS[LEVEL_NOTICE],
            "color": LEVEL_COLORS[LEVEL_NOTICE],
            "summary": "Тип водоема неизвестен - интерпретация ориентировочная.",
            "ndci_mean": ndci_mean,
            "polluted_percentage": polluted_percentage,
        }

    if ndci_mean is None:
        return {
            "water_type": water_type,
            "level": LEVEL_OK,
            "level_label": "нет данных",
            "color": "#9e9e9e",
            "summary": "Недостаточно данных для оценки.",
            "ndci_mean": None,
            "polluted_percentage": polluted_percentage,
        }

    _, level, description = _lookup(ndci_mean, rules)
    pct_note = ""
    if polluted_percentage is not None:
        pct_rules = _POLLUTED_RULES.get(water_type, [])
        if pct_rules:
            _, note = _lookup(polluted_percentage, pct_rules)
            pct_note = f"Площадь с превышением порога - {polluted_percentage:.1f}% ({note})."

    return {
        "water_type": water_type,
        "level": level,
        "level_label": LEVEL_LABELS[level],
        "color": LEVEL_COLORS[level],
        "summary": description + pct_note,
        "ndci_mean": ndci_mean,
        "polluted_percentage": polluted_percentage,
    }

def dominant_water_type(geojson_features: List[Dict[str, Any]]) -> Optional[str]:
    if not geojson_features:
        return None
    areas: Dict[str, float] = {}
    for f in geojson_features:
        props = f.get("properties", {})
        wtype = str(props.get("type", "")).lower()
        if not wtype:
            continue
        areas[wtype] = areas.get(wtype, 0.0) + float(props.get("area_pixels", 0) or 0)
    if not areas:
        return None
    return max(areas, key=areas.get)

def per_type_breakdown(
    geojson_features: List[Dict[str, Any]],
    ndci_mean: Optional[float],
    polluted_percentage: Optional[float],
) -> Dict[str, Dict[str, Any]]:
    types_present = {
        str(f.get("properties", {}).get("type", "")).lower()
        for f in geojson_features
    }
    types_present.discard("")
    return {
        t: interpret_eutrophication(ndci_mean, polluted_percentage, t)
        for t in sorted(types_present)
    }

def build_risk_interpretation(
    eutrophication_stats: Optional[Dict[str, Any]],
    geojson_features: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    if not eutrophication_stats:
        return None

    ndci_mean = eutrophication_stats.get("ndci_mean")
    polluted_pct = eutrophication_stats.get("polluted_percentage")

    dominant = dominant_water_type(geojson_features)
    primary = interpret_eutrophication(ndci_mean, polluted_pct, dominant) if dominant else None
    by_type = per_type_breakdown(geojson_features, ndci_mean, polluted_pct)

    return {
        "dominant_type": dominant,
        "primary": primary,
        "by_type": by_type,
    }