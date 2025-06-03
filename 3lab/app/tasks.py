from celery import Celery
import time
import redis
import json
from io import BytesIO
from PIL import Image
import numpy as np
import cv2
import base64
import io

celery = Celery(__name__, broker="redis://redis:6379/0")
r = redis.Redis(host="redis", port=6379)

@celery.task
def bernsen_binarization_task(task_id: str, image_data: str, t: float = 0.5, window_size: int = 31, contrast_threshold: int = 15):
    """Применяет алгоритм Бернсена к изображению."""
    try:
        img_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(img_bytes)).convert("L")
    except Exception as e:
        return {"error": f"Ошибка декодирования изображения: {e}"}

    # Преобразуем изображение в массив
    img_array = np.array(image, dtype=np.uint8)
    pad = window_size // 2

    # Расширяем границы изображения (репликацией краёв)
    padded = np.pad(img_array, pad, mode='edge')

    result = np.zeros_like(img_array, dtype=np.uint8)

    for y in range(img_array.shape[0]):
        progress = int(y / img_array.shape[0] * 100)
        r.publish(f"progress:{task_id}", json.dumps({"progress": progress}))
        for x in range(img_array.shape[1]):
            window = padded[y:y+window_size, x:x+window_size]
            I_max = np.max(window) * 1.0
            I_min = np.min(window) * 1.0
            contrast = I_max - I_min

            if contrast < contrast_threshold:
                result[y, x] = 255  # фон
            else:
                T = (I_max + I_min) * t
                result[y, x] = 255 if img_array[y, x] > T else 0

    result_image = Image.fromarray(result.astype(np.uint8))

    output = BytesIO()
    result_image.save(output, format="PNG")
    result_base64 = base64.b64encode(output.getvalue()).decode("utf-8")
    result_data_url = f"data:image/png;base64,{result_base64}"
    r.publish(f"progress:{task_id}", json.dumps({"result": result_data_url}))


@celery.task
def equbal_binarization_task(task_id: str, image_data: str, k: float = 0.2, window_size: int = 31):
    try:
        img_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(img_bytes)).convert("L")
    except Exception as e:
        return {"error": f"Ошибка декодирования изображения: {e}"}

    img_array = np.array(image, dtype=np.uint8).astype(np.float32)
    pad = window_size // 2
    padded = cv2.copyMakeBorder(img_array, pad, pad, pad, pad, cv2.BORDER_REPLICATE)

    result = np.zeros_like(img_array)

    for y in range(img_array.shape[0]):
        progress = int(y / img_array.shape[0] * 100)
        r.publish(f"progress:{task_id}", json.dumps({"progress": progress}))
        for x in range(img_array.shape[1]):
            window = padded[y:y + window_size, x:x + window_size]
            I_max = np.max(window)
            mean = np.mean(window)
            std = np.std(window)

            T = mean + k * (I_max - mean) * (std / 128)
            result[y, x] = 255 if img_array[y, x] > T else 0

    result_image = Image.fromarray(result.astype(np.uint8))

    output = BytesIO()
    result_image.save(output, format="PNG")
    result_base64 = base64.b64encode(output.getvalue()).decode("utf-8")
    result_data_url = f"data:image/png;base64,{result_base64}"
    r.publish(f"progress:{task_id}", json.dumps({"result": result_data_url}))


@celery.task
def singh_binarization_task(task_id: str, image_data:str, k: float = 0.25, window_size: int = 31):
    """Адаптивная бинаризация по методу Сингха."""
    try:
        img_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(img_bytes)).convert("L")
    except Exception as e:
        return {"error": f"Ошибка декодирования изображения: {e}"}
    img_array = np.array(image, dtype=np.uint8).astype(np.float32)
    mean = cv2.blur(img_array, (window_size, window_size))
    mean_sq = cv2.blur(img_array ** 2, (window_size, window_size))
    std = np.sqrt(mean_sq - mean ** 2)

    T = mean * (1 + k * ((std / 128) - 1))
    binary = np.where(img_array > T, 255, 0).astype(np.uint8)

    result_image = Image.fromarray(binary)

    output = BytesIO()
    result_image.save(output, format="PNG")
    result_base64 = base64.b64encode(output.getvalue()).decode("utf-8")
    result_data_url = f"data:image/png;base64,{result_base64}"
    r.publish(f"progress:{task_id}", json.dumps({"result": result_data_url}))

