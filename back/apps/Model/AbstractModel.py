from Image.GeoImage import GeoImage

import numpy as np
import requests
import cv2
import os


class OpenCVimg:
    def __init__(self, img):
        self._cv_image = img
    
    
    @classmethod
    def from_local_img(cls, path):
        if not os.path.exists(path):
            raise ValueError("Файл не найден")
        img = cv2.imread(path)
        return cls(img)
    
    
    @classmethod
    def from_url_img(cls, url):
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        arr = np.frombuffer(resp.content, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return cls(img)
