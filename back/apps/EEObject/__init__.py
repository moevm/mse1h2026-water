from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

import ee


class AbstactEEObject(ABC):
    def __init__(self, query_data: Dict[str, Any]):
        self.ee_object = self._set_ee_object()
        self.region = self._set_ee_region()
        self.scale = query_data["scale"]
        self.query_data = query_data
        self._ee_obj_url = None
    
    
    @property
    @abstractmethod
    def _max_palette_value(self):
        pass


    @abstractmethod
    def _set_ee_object(self) -> ee.Image:
        pass
    
    
    @abstractmethod
    def _set_ee_region(self) -> ee.Geometry:
        pass
    
    
    def _build_thumbnail(self):
        # Вариант улучшения: Можно сделать запрос ссылки, только если старая неактивна
        self._ee_obj_url = self.ee_object.getThumbURL({
            'region': self.region,
            'scale': self.scale,
            'format': 'png',
            'min': 0,
            'max': self._max_palette_value,
            'crs': 'EPSG:3857'
        })
        return self._ee_obj_url
