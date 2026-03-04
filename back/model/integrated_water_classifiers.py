from back.model.API import get_satellite_image
import numpy as np
import cv2
import requests
import os


def cv_integrated_water_classifier(image_data=None, region=None, image_source=None, file_to_save="cv_water_objects.png"):
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
        # thumbnail для OpenCV
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
        if img is None:
            raise ValueError("Не удалось загрузить изображение из model")

    else:
        raise ValueError("Не указаны ни image_source, ни image_data + region")

    annotated = img.copy()

    # =========================
    # Настоящие каналы для NDWI (B3 - B8)
    # =========================
    if image_data is not None:
        ndwi_img = image_data.normalizedDifference(['B3', 'B8'])
        thumb_url = ndwi_img.getThumbURL({
            'region': region,
            'dimensions': 1024,
            'format': 'png',
            'min': -1,
            'max': 1
        })
        resp = requests.get(thumb_url)
        arr = np.frombuffer(resp.content, np.uint8)
        water_mask = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
        water_mask = (water_mask > 127).astype(np.uint8) * 255  # бинаризация
    else:
        # для обычного RGB (thumbnail / local file)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        R = img_rgb[:, :, 0].astype(float)
        G = img_rgb[:, :, 1].astype(float)
        ndwi = (G - R) / (G + R + 1e-6)
        water_mask = (ndwi > 0.2).astype(np.uint8) * 255

    # =========================
    # Морфология 2x2
    # =========================
    kernel = np.ones((2, 2), np.uint8)
    water_mask = cv2.morphologyEx(water_mask, cv2.MORPH_CLOSE, kernel, iterations=1)

    # =========================
    # Контуры и классификация
    # =========================
    contours, _ = cv2.findContours(water_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    results = []
    obj_id = 1
    h_img, w_img = annotated.shape[:2]

    color_dict = {
        "озеро": (255, 0, 0), # синий
        "река": (0, 255, 0), # зеленый
        "болото": (0, 0, 255), # красный
        "пруд": (0, 255, 255) # желтый
    }

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 10:
            continue

        # минимальный повёрнутый прямоугольник
        rect = cv2.minAreaRect(cnt)  # ((cx, cy), (w, h), angle)
        (cx_r, cy_r), (w, h), angle = rect
        elongation = max(w, h) / (min(w, h) + 1e-6)

        # классификация
        if area < 100:
            water_type = "пруд"
        elif elongation > 2:
            water_type = "река"
        elif area > 2000:
            water_type = "озеро"
        else:
            water_type = "болото"

        # центр контура через моменты
        M = cv2.moments(cnt)
        cx = int(M["m10"] / M["m00"]) if M["m00"] != 0 else int(cx_r)
        cy = int(M["m01"] / M["m00"]) if M["m00"] != 0 else int(cy_r)

        cv2.drawContours(annotated, [cnt], -1, color_dict[water_type], 2)
        cv2.putText(annotated, str(obj_id), (cx, cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_dict[water_type], 2)

        result = {
            "id": obj_id,
            "area_pixels": area,
            "elongation": float(elongation),
            "type": water_type,
            "center_x": cx,
            "center_y": cy
        }

        if region is not None:
            min_lon, min_lat = region.bounds().getInfo()['coordinates'][0][0]
            max_lon, max_lat = region.bounds().getInfo()['coordinates'][0][2]
            lon = min_lon + (cx / w_img) * (max_lon - min_lon)
            lat = max_lat - (cy / h_img) * (max_lat - min_lat)
            result["lon"] = lon
            result["lat"] = lat

        results.append(result)
        obj_id += 1

    cv2.imwrite(file_to_save, annotated)
    return results

if __name__ == "__main__":

    lon, lat = 30.3141, 59.9386  # Санкт-Петербург

    image, region, url = get_satellite_image(lon, lat, buffer_km=10)

    cv_results = cv_integrated_water_classifier(image, region, url)
    print(cv_results)
