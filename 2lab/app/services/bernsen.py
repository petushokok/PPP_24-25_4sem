import cv2
import numpy as np

def binarize_bersen(image, window_size=15, k=0.15, t=0.5):
    """
    Бинаризация изображения методом Бернсена
    
    Параметры:
    - image: входное изображение (в градациях серого)
    - window_size: размер окрестности (должен быть нечетным)
    - k: параметр алгоритма (обычно 0.15-0.2)
    - t: параметр порога (0..1)
    
    Возвращает:
    - Бинаризованное изображение (0 - черный, 255 - белый)
    """
    if len(image.shape) > 2:
        raise ValueError("Изображение должно быть в градациях серого")
    
    if window_size % 2 == 0:
        window_size += 1  # делаем нечетным
    
    # Добавляем рамку для обработки границ
    border = window_size // 2
    padded = cv2.copyMakeBorder(image, border, border, border, border, cv2.BORDER_REFLECT)
    
    # Создаем пустое выходное изображение
    binary = np.zeros_like(image, dtype=np.uint8)
    
    # Проходим по каждому пикселю
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            # Получаем окрестность
            neighborhood = padded[i:i+window_size, j:j+window_size]
            
            # Находим минимальное и максимальное значение в окрестности
            min_val = np.min(neighborhood)
            max_val = np.max(neighborhood)
            
            # Вычисляем порог
            threshold = (min_val + max_val) / 2
            
            # Применяем порог с учетом параметра t
            if image[i, j] > threshold + (max_val - min_val) * k * (t - 0.5):
                binary[i, j] = 255
            else:
                binary[i, j] = 0
                
    return binary

if __name__ == "__main__":
    # Загрузка изображения
    input_path = "bike_bw.png"
    output_path = "output.png"
    
    # Чтение изображения (с автоматическим преобразованием в grayscale)
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        raise FileNotFoundError(f"Не удалось загрузить изображение {input_path}")
    
    # Применение бинаризации Бернсена
    binary_img = binarize_bersen(img, window_size=15, k=0.15, t=0.5)
    
    # Сохранение результата
    cv2.imwrite(output_path, binary_img)
    print(f"Бинаризация завершена. Результат сохранен в {output_path}")

