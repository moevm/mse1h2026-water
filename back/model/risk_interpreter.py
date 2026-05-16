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