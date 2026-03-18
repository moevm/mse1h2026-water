from model.download_images import get_satellite_image

import asyncio
import numpy as np
import cv2
import requests
import os
import base64
import uuid


async def cv_integrated_water_classifier(image_data=None, region=None, image_source=None, file_to_save=None, is_create_file_with_url=True):
    """
    Классификация водоемов через OpenCV
    Работает:
      - с image_data + region (model Image)
      - с image_source (локальный файл или URL)
    """

    # =========================
    # Получение изображения
    # =========================
    if image_source:
        if image_source.startswith("http://") or image_source.startswith("https://"):
            resp = requests.get(image_source)
            arr = np.frombuffer(resp.content, np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        else:
            if not os.path.exists(image_source):
                raise ValueError("Файл не найден")
            img = cv2.imread(image_source)

        if img is None:
            raise ValueError("Не удалось загрузить изображение")

    elif image_data is not None and region is not None:
        thumb_url = image_data.getThumbURL({
            'region': region,
            'dimensions': 1024,
            'format': 'png',
            'min': 0,
            'max': 3000
        })
        resp = requests.get(thumb_url)
        arr = np.frombuffer(resp.content, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    else:
        raise ValueError("Не указаны ни image_source, ни image_data + region")

    annotated = img.copy()

    if image_data is not None:
        swir1 = image_data.select('B11')
        ndwi  = image_data.normalizedDifference(['B3', 'B8']) 

        water_mask_gee = (
            ndwi.gt(-0.006)         
            .And(swir1.lt(1600))  
        )

        mask_thumb_url = water_mask_gee.getThumbURL({
            'region': region,
            'dimensions': 1024,
            'format': 'png',
            'min': 0,
            'max': 1
        })

        resp = requests.get(mask_thumb_url)
        arr = np.frombuffer(resp.content, np.uint8)
        water_mask = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)

        if water_mask is None:
            raise ValueError("Не удалось загрузить водную маску")

        water_mask = (water_mask > 127).astype(np.uint8) * 255

    else:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        R = img_rgb[:, :, 0].astype(float)
        G = img_rgb[:, :, 1].astype(float)
        ndwi = (G - R) / (G + R + 1e-6)
        water_mask = (ndwi > 0.2).astype(np.uint8) * 255

    kernel = np.ones((2, 2), np.uint8)
    water_mask = cv2.morphologyEx(water_mask, cv2.MORPH_CLOSE, kernel, iterations=1)

    contours, _ = cv2.findContours(water_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    results = []
    obj_id = 1
    h_img, w_img = annotated.shape[:2]

    color_dict = {
        "пруд": (0, 255, 255),   
        "река": (0, 255, 0),      
        "болото": (0, 0, 255),   
        "озеро": (255, 0, 0)    
    }

    if region is not None:
        bounds = region.bounds().getInfo()['coordinates'][0]
        min_lon, min_lat = bounds[0]
        max_lon, max_lat = bounds[2]

    if region is not None:
        bounds = region.bounds().getInfo()['coordinates'][0]
        min_lon, min_lat = bounds[0]
        max_lon, max_lat = bounds[2]

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 10:
            continue

        rect = cv2.minAreaRect(cnt)
        (cx_r, cy_r), (w, h), angle = rect
        elongation = max(w, h) / (min(w, h) + 1e-6)

        x, y, w_box, h_box = cv2.boundingRect(cnt)
        roi = water_mask[y:y+h_box, x:x+w_box]
        water_ratio = np.sum(roi > 0) / (w_box * h_box + 1e-6)

        if area < 100:
            water_type = "пруд"
        elif elongation > 2 or water_ratio < 0.4: 
            water_type = "река"
        elif area > 2000:
            water_type = "озеро"
        else:
            water_type = "болото"

        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            cx = int(cx_r)
            cy = int(cy_r)

        cv2.drawContours(annotated, [cnt], -1, color_dict[water_type], 2)

        result = {
            "id": obj_id,
            "area_pixels": area,
            "elongation": float(elongation),
            "type": water_type,
            "center_x": cx,
            "center_y": cy,
        }

        if region is not None:
            lon = min_lon + (cx / w_img) * (max_lon - min_lon)
            lat = max_lat - (cy / h_img) * (max_lat - min_lat)
            result["lon"] = lon
            result["lat"] = lat

        results.append(result)
        obj_id += 1

    if file_to_save:
        cv2.imwrite(file_to_save, annotated)
        
    if is_create_file_with_url:
        unique_filename = f"{uuid.uuid4()}.png"
        save_path = os.path.join("img/classified", unique_filename)
        cv2.imwrite(save_path, annotated)
        annotated_url = f"img/classified/{unique_filename}"
    
    return {
        'annotated_url': annotated_url,
        'results': results,
    }


if __name__ == "__main__":

    lon, lat = 30.3141, 59.9386  

    image, region, url, metadata = get_satellite_image(lon, lat, buffer_km=6)

    cv_results = cv_integrated_water_classifier(image, region, url, file_to_save="cv_water_objects.png")
    print(cv_results)