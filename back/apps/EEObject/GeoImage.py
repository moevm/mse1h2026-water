from typing import Optional, Dict, Any

from apps.EEObject import AbstactEEObject
from utils.ee_collections import build_collection, request_image
from utils.ee_auth import initialize_ee
from exceptions import GeoImageError, InvalidParametersError

import os
import ee
import uuid
import requests


initialize_ee()


class GeoImage(AbstactEEObject):
    def __init__(self, query_data: Dict[str, Any]):
        super().__init__(query_data)
        self._info: Optional[Dict[str, Any]] = None
        self._tiff_file: Optional[str] = None
        self._local_src_file = None

    
    @property
    def _max_palette_value(self):
        return 3000
    
    
    def _set_ee_object(self):
        region, start_date, end_date, image_collection, cloud_threshold = (
            self.query_data["region"],
            self.query_data["start_date"],
            self.query_data["end_date"],
            self.query_data["image_collection"],
            self.query_data["cloud_threshold"],
        )
        
        collection = build_collection(
            region, start_date, end_date, image_collection, cloud_threshold
        )
        
        ee_image = request_image(collection)
            
        return ee_image.select(self.query_data.get("bands"))
    

    def _set_ee_region(self) -> ee.Geometry:
        lon, lat, buffer_km = (
            self.query_data["lon"],
            self.query_data["lat"],
            self.query_data["buffer_km"],
        )
        
        try:
            point = ee.Geometry.Point([lon, lat])
            return point.buffer(buffer_km * 1000).bounds()
        except ee.EEException as e:
            raise InvalidParametersError(
                f"Не удалось построить регион: lon={lon}, lat={lat}, buffer={buffer_km} км"
            ) from e


    @classmethod
    def from_data(
        cls,
        lon: float, lat: float,
        buffer_km: float = 6.0,
        start_date: str = '2025-06-01',
        end_date: str = '2025-08-31',
        image_collection: str = 'COPERNICUS/S2_SR_HARMONIZED',
        cloud_threshold: int = 20,
        scale: int = 30,
        bands: Optional[tuple] = ('B4', 'B3', 'B2', 'B8', 'B11')
    ) -> 'GeoImage':

        query_data = {
            "coordinates_center": {"longitude": lon, "latitude": lat},
            "buffer_km": buffer_km,
            "date_range": {"start": start_date, "end": end_date},
            "image_collection": image_collection,
            "cloud_threshold": cloud_threshold,
            "scale": scale,
            "bands": bands,
        }
        
        return cls(query_data)


    def _load_info(self) -> Optional[Dict[str, Any]]:
        if self._info is None:
            try:
                self._info = self.ee_object.getInfo()
            except ee.EEException as e:
                raise GeoImageError(f"Ошибка при получении информации об изображении: {e}") from e
        return self._info


    @property
    def info(self) -> Optional[Dict[str, Any]]:
        return self._load_info()
    
    
    def local_save_src(self, src_img_path = "files/img/source"):
        
        resp = requests.get(self._build_thumbnail(), timeout=5)
        resp.raise_for_status()

        os.makedirs(src_img_path, exist_ok=True)
        
        self._local_src_file = f"{src_img_path}/{uuid.uuid4()}.png"
        while os.path.exists(self._local_src_file):
            self._local_src_file = f"{src_img_path}/{uuid.uuid4()}.png"
        
        with open(self._local_src_file, 'wb') as file:
            file.write(resp.content)
        
        return self._local_src_file


    def _download_tiff(self, filepath: str = "files/geotif") -> str:
        ee_tif_url = self.ee_object.getDownloadURL({
            "region": self.region,
            "scale": self.scale,
            "format": "GEO_TIFF",
            "crs": "EPSG:3857",
        })

        r = requests.get(ee_tif_url, timeout=5)
        tif_file = f"{filepath}/{uuid.uuid4()}.tif"
        with open(tif_file, "xb") as f:
            f.write(r.content)

        return tif_file


    @property
    def tiff_file(self) -> str:
        if self._tiff_file is None:
            try:
                self._tiff_file = self._download_tiff(self.scale)
            except Exception as e:
                raise GeoImageError(f"Ошибка при загрузке TIFF-файла: {e}") from e
        return self._tiff_file

    #TODO: Метадата

    #TODO: GeoJSON
