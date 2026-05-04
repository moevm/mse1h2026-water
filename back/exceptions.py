class GeoImageError(Exception):
    """Базовое исключение для GeoImage."""
    pass

class NoImageFoundError(GeoImageError):
    """Нет подходящего снимка."""
    pass

class InvalidParametersError(GeoImageError):
    """Некорректные параметры запроса."""
    pass
