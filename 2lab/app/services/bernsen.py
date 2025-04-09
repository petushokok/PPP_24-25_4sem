import numpy as np
from PIL import Image

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


def main():
    # Загружаем изображение
    image = Image.open('bike_bw.png').convert('L')

    # Применяем бинаризацию Бернсена
    result_image = bernsen_binarization(image)

    # Сохраняем результат
    result_image.save('output.png')


if __name__ == "__main__":
    main()
