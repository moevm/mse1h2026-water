from typing import Optional, Dict, Any

from utils.ee_helpers import build_region, build_collection, request_image
from utils.ee_auth import initialize_ee
from exceptions import GeoImageError, NoImageFoundError

import os
import ee
import uuid
import requests


initialize_ee()


class GeoImage:
    def __init__(self, ee_image: ee.Image, region: ee.Geometry, query_data: Dict[str, Any]):
        self._ee_image = ee_image.select(query_data.get("bands", ('B4', 'B3', 'B2', 'B8', 'B11')))
        self._region = region
        self._info: Optional[Dict[str, Any]] = None
        self._query_data = query_data
        self._tiff_file: Optional[str] = None
        self._src_img_url: str = None
        self._local_src_file = None


    @classmethod
    def from_data(
        cls,
        lon: float, lat: float,
        buffer_km: float = 6.0,
        start_date: str = '2025-06-01',
        end_date: str = '2025-08-31',
        image_collection: str = 'COPERNICUS/S2_SR_HARMONIZED',
        cloud_threshold: int = 20,
        bands: Optional[list] = ('B4', 'B3', 'B2', 'B8', 'B11')
    ) -> 'GeoImage':
        region = build_region(lon, lat, buffer_km)
        collection = build_collection(region, start_date, end_date, image_collection, cloud_threshold)

        try:
            ee_image = request_image(collection)
        except NoImageFoundError:
            raise NoImageFoundError(
                f"Не найдено изображений для координат: lon={lon}, lat={lat}, buffer={buffer_km} км, date_range=({start_date}, {end_date})"
            )

        query_data = {
            "coordinates_center": {"longitude": lon, "latitude": lat},
            "buffer_km": buffer_km,
            "date_range": {"start": start_date, "end": end_date},
            "image_collection": image_collection,
            "cloud_threshold": cloud_threshold,
            "bands": bands,
        }
        
        return cls(ee_image, region, query_data)


    def _load_info(self) -> Optional[Dict[str, Any]]:
        if self._info is None:
            try:
                self._info = self._ee_image.getInfo()
            except ee.EEException as e:
                raise GeoImageError(f"Ошибка при получении информации об изображении: {e}") from e
        return self._info


    @property
    def info(self) -> Optional[Dict[str, Any]]:
        return self._load_info()


    def _build_thumbnail(self, scale: int = 30):
        self._src_img_url = self._ee_image.getThumbURL({
            'region': self._region,
            'scale': scale,
            'format': 'png',
            'min': 0,
            'max': 3000,
            'crs': 'EPSG:3857'
        })
        return self._src_img_url
    
    
    def local_save_src(self, src_img_path = "files/img/source"): 
        
        # Вариант улучшения: Можно сделать запрос ссылки, только если старая неактивна
        resp = requests.get(self._build_thumbnail(), timeout=5)
        resp.raise_for_status()

        os.makedirs(src_img_path, exist_ok=True)
        
        self._local_src_file = f"{src_img_path}/{uuid.uuid4()}.png"
        while os.path.exists(self._local_src_file):
            self._local_src_file = f"{src_img_path}/{uuid.uuid4()}.png"
        
        with open(self._local_src_file, 'wb') as file:
            file.write(resp.content)
        
        return self._local_src_file


    def _download_tiff(self, filepath: str = "files/geotif", scale: int = 30) -> str:
        ee_tif_url = self._ee_image.getDownloadURL({
            "region": self._region,
            "scale": scale,
            "format": "GEO_TIFF",
            "crs": "EPSG:3857",
        })

        r = requests.get(ee_tif_url, timeout=5)
        tif_file = f"{filepath}/{uuid.uuid4()}.tif"
        with open(tif_file, "xb") as f:
            f.write(r.content)

        return tif_file


    @property
    def tiff_file(self, scale: int = 30) -> str:
        if self._tiff_file is None:
            try:
                self._tiff_file = self._download_tiff(scale)
            except Exception as e:
                raise GeoImageError(f"Ошибка при загрузке TIFF-файла: {e}") from e
        return self._tiff_file

    #TODO: Метадата

    #TODO: GeoJSON
