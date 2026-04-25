from model.download_images import get_satellite_image
from model.water_utils import get_water_mask_gee

import asyncio
import numpy as np
import cv2
import requests
import os
import uuid
import json
import rasterio


def load_image(image_source=None, image_data=None, region=None):
    if image_source:
        if image_source.startswith("http"):
            resp = requests.get(image_source)
            arr = np.frombuffer(resp.content, np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        else:
            if not os.path.exists(image_source):
                raise ValueError("Файл не найден")
            img = cv2.imread(image_source)
    else:
        thumb_url = image_data.getThumbURL({
            'region': region,
            'dimensions': 512,
            'format': 'png',
            'min': 0,
            'max': 3000
        })
        resp = requests.get(thumb_url)
        arr = np.frombuffer(resp.content, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Не удалось загрузить изображение")

    return img

def get_water_mask(image_data, region, get_water_mask_gee):
    mask_gee = get_water_mask_gee(image_data)

    mask_url = mask_gee.getThumbURL({
        'region': region,
        'dimensions': 512,
        'format': 'png',
        'min': 0,
        'max': 1
    })

    resp = requests.get(mask_url)
    arr = np.frombuffer(resp.content, np.uint8)
    mask = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)

    if mask is None:
        raise ValueError("Не удалось загрузить водную маску")

    mask = (mask > 127).astype(np.uint8) * 255
    kernel = np.ones((2, 2), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask

def classify_water_object(area, elongation, water_ratio):
    if area < 100:
        return "пруд"
    elif elongation > 2 or water_ratio < 0.4:
        return "река"
    elif area > 2000:
        return "озеро"
    else:
        return "болото"

def pixel_to_geo(x, y, transform):
    
    lon, lat = rasterio.transform.xy(transform, y, x)

    return lon, lat

def analyze_water_objects(mask, annotated, tif_file):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    results = []
    h_img, w_img = annotated.shape[:2]

    colors = {
        "пруд": (0, 255, 255),
        "река": (0, 255, 0),
        "болото": (0, 0, 255),
        "озеро": (255, 0, 0)
    }

    obj_id = 1

    with rasterio.open(tif_file) as src:
        transform = src.transform

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 10:
            continue

        rect = cv2.minAreaRect(cnt)
        (_, _), (w, h), _ = rect
        elongation = max(w, h) / (min(w, h) + 1e-6)

        x, y, w_box, h_box = cv2.boundingRect(cnt)
        roi = mask[y:y+h_box, x:x+w_box]
        water_ratio = np.sum(roi > 0) / (w_box * h_box + 1e-6)

        water_type = classify_water_object(area, elongation, water_ratio)

        M = cv2.moments(cnt)
        cx = int(M["m10"] / M["m00"]) if M["m00"] else x
        cy = int(M["m01"] / M["m00"]) if M["m00"] else y
    
        lon, lat = pixel_to_geo(cx, cy, transform)

        cv2.drawContours(annotated, [cnt], -1, colors[water_type], 2)

        results.append({
            "id": obj_id,
            "type": water_type,
            "area_pixels": area,
            "elongation": float(elongation),
            "center_x": cx,
            "center_y": cy,
            "lon": lon,
            "lat": lat,
            "contour": cnt.reshape(-1, 2).tolist()
        })

        obj_id += 1

    return results

def create_geojson(results, bounds, w_img, h_img, metadata):
    features = []
    
    tif_file = metadata["tif_file"]
    with rasterio.open(tif_file) as src:
        transform = src.transform
    
    for obj in results:
        cnt = obj["contour"]
        coords = []

        for point in cnt:
            x, y = point
            lon, lat = pixel_to_geo(x, y, transform)
            coords.append([lon, lat])

        if coords[0] != coords[-1]:
            coords.append(coords[0])

        features.append({
            "type": "Feature",
            "properties": {
                "id": obj["id"],
                "type": obj["type"],
                "area_pixels": obj["area_pixels"],
                "elongation": obj["elongation"],
                "center_x": obj["center_x"],
                "center_y": obj["center_y"],
                "lon": obj["lon"],
                "lat": obj["lat"],
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords]
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": metadata,
        "bounds": bounds,
        "image_dimensions": [w_img, h_img]
    }


async def cv_integrated_water_classifier(image_data, region, image_source, metadata, save_image=True, save_geojson=True, do_show_content=False):

    """
    Классификация водоемов через OpenCV по данным с ИК-каналами (GEE).
    Для классификации требуется image_data и region.
    image_source используется только для получения визуального изображения для разметки.
    """

    img = load_image(image_source, image_data, region)
    annotated = img.copy()

    mask = get_water_mask(image_data, region, get_water_mask_gee)

    bounds = region.bounds().getInfo()['coordinates'][0]

    results = analyze_water_objects(mask, annotated, tif_file=metadata["tif_file"])

    answer = dict()

    if save_image:
        os.makedirs("img", exist_ok=True)
        filename = f"img/{uuid.uuid4()}.png"
        cv2.imwrite(filename, annotated)
        answer["image_path"] = filename

    if save_geojson:
        os.makedirs("geojson", exist_ok=True)
        geojson = create_geojson(results, bounds, *annotated.shape[:2][::-1], metadata)

        filename = f"geojson/{uuid.uuid4()}.geojson"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(geojson, f, indent=2, ensure_ascii=False)

        answer["geojson_path"] = filename

    if do_show_content:
        answer["results"] = results
        answer["metadata"] = metadata
    
    return answer
