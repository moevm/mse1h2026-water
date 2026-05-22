from apps.EEObject.Mask import AbstractGeoMask

import requests
import numpy as np
import cv2


class WaterMask(AbstractGeoMask):
    def _set_ee_object(self):
        ndwi = self.ee_object.normalizedDifference(['B3', 'B8'])
        swir1 = self.ee_object.select('B11')
        ee_mask = ndwi.gt(-0.006).And(swir1.lt(1600))
        return ee_mask
    
    
    def get_mask(self):
        mask_url = self._build_thumbnail()
        
        resp = requests.get(mask_url, timeout=5)
        arr = np.frombuffer(resp.content, np.uint8)
        mask = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)

        if mask is None:
            raise ValueError("Не удалось загрузить водную маску")

        mask = (mask > 127).astype(np.uint8) * 255
        kernel = np.ones((2, 2), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        return mask
