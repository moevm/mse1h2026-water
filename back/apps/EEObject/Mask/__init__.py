from apps.EEObject import AbstactEEObject
from apps.EEObject.GeoImage import GeoImage

from abc import abstractmethod


class AbstractGeoMask(AbstactEEObject):
    def __init__(self, geo_image: GeoImage):
        super().__init__(geo_image.query_data)
        self._geo_image = geo_image
    
    @property
    def _max_palette_value(self):
        return 1
    
    @abstractmethod
    def get_mask(self):
        pass
