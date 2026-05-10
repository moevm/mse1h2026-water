from exceptions import GeoImageError, InvalidParametersError, NoImageFoundError

import ee


def build_region(lon: float, lat: float, buffer_km: float) -> ee.Geometry:
    try:
        point = ee.Geometry.Point([lon, lat])
        return point.buffer(buffer_km * 1000).bounds()
    except ee.EEException as e:
        raise InvalidParametersError(
            f"Не удалось построить регион: lon={lon}, lat={lat}, buffer={buffer_km} км"
        ) from e


def build_collection(
    region: ee.Geometry, 
    start_date: str, 
    end_date: str, 
    image_collection: str = 'COPERNICUS/S2_SR_HARMONIZED', 
    cloud_threshold: int = 20
) -> ee.ImageCollection:
    try:
        return (
            ee.ImageCollection(image_collection)
            .filterDate(start_date, end_date)
            .filterBounds(region)
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_threshold))
            .sort('CLOUDY_PIXEL_PERCENTAGE')
        )
    except ee.EEException as e:
        raise InvalidParametersError(
            f"Не удалось построить коллекцию: start={start_date}, end={end_date}"
        ) from e


def request_image(collection: ee.ImageCollection) -> ee.Image:
    try:
        ee_image = collection.first()
        if ee_image is None:
            raise NoImageFoundError
        return ee_image
    except ee.EEException as e:
        raise GeoImageError(f"Ошибка Earth Engine при получении снимка: {e}") from e
