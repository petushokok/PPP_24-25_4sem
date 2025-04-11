import numpy as np
from PIL import Image
import cv2

def bernsen_binarization(image: Image.Image, t: float = 0.5, window_size: int = 31, contrast_threshold: int = 15) -> Image.Image:
    """Применяет алгоритм Бернсена к изображению."""
    # Преобразуем изображение в массив
    img_array = np.array(image, dtype=np.uint8)
    pad = window_size // 2

    # Расширяем границы изображения (репликацией краёв)
    padded = np.pad(img_array, pad, mode='edge')

    result = np.zeros_like(img_array, dtype=np.uint8)

    for y in range(img_array.shape[0]):
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

    return Image.fromarray(result)

def singh_binarization(image: Image.Image, k: float = 0.25, window_size: int = 31) -> Image.Image:
    """Адаптивная бинаризация по методу Сингха."""
    img_array = np.array(image, dtype=np.uint8).astype(np.float32)
    mean = cv2.blur(img_array, (window_size, window_size))
    mean_sq = cv2.blur(img_array ** 2, (window_size, window_size))
    std = np.sqrt(mean_sq - mean ** 2)

    T = mean * (1 + k * ((std / 128) - 1))
    binary = np.where(img_array > T, 255, 0).astype(np.uint8)

    return Image.fromarray(binary)

def equbal_binarization(image: Image.Image, k: float = 0.2, window_size: int = 31) -> Image.Image:
    """Адаптивная бинаризация по методу Эйквила."""
    img_array = np.array(image, dtype=np.uint8).astype(np.float32)
    pad = window_size // 2
    padded = cv2.copyMakeBorder(img_array, pad, pad, pad, pad, cv2.BORDER_REPLICATE)

    result = np.zeros_like(img_array)

    for y in range(img_array.shape[0]):
        for x in range(img_array.shape[1]):
            window = padded[y:y + window_size, x:x + window_size]
            I_max = np.max(window)
            mean = np.mean(window)
            std = np.std(window)

            T = mean + k * (I_max - mean) * (std / 128)
            result[y, x] = 255 if img_array[y, x] > T else 0

    return Image.fromarray(result.astype(np.uint8))



def main():
    image = Image.open('bike_bw.png').convert('L')

    bernsen_result = bernsen_binarization(image)
    bernsen_result.save('output_bernsen.png')

    singh_result = singh_binarization(image)
    singh_result.save('output_singh.png')

    equbal_result = equbal_binarization(image)
    equbal_result.save('output_equbal.png')



if __name__ == "__main__":
    main()
