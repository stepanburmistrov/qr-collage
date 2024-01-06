import cv2
import os
import numpy as np
import qrcode
import random

# 1) Считываем все фотографии из директории
dir_path = "images"
all_images = [os.path.join(dir_path, img) for img in os.listdir(dir_path) if img.endswith(('jpg', 'png'))]

# Создаем QR-код
data = "https://t.me/robot_x_school"
box_size = 27  # Это начальное значение, вы можете изменить его позже для настройки разрешения

qr = qrcode.QRCode(
    version=1, 
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=box_size,
    border=1
)
qr.add_data(data)
qr.make(fit=True)

# Вычисляем размер модуля в зависимости от размера итогового изображения
final_image_side = 13450
# Отношение сторон итогового изображения к количеству модулей в QR коде
scale_factor = final_image_side / (len(qr.modules) * box_size)

# Теперь создаем изображение с учетом масштабного коэффициента
img_qr = qr.make_image(fill_color="black", back_color="white").resize((int(scale_factor * len(qr.modules) * box_size), int(scale_factor * len(qr.modules) * box_size)))

# Если вы хотите сохранить QR-код в файл для проверки:
img_qr.save("high_res_qr.png")

# Открываем файл с QR-кодом
img_qr = cv2.imread('high_res_qr.png')

# Задаем параметры
box_size_pixels = 499
modules_count = 27  # так как 27x27 квадратов
final_img_collage = np.ones((final_image_side, final_image_side, 3), np.uint8) * 255

# Проходим по всем квадратам
for y in range(modules_count):
    for x in range(modules_count):
        # Вычисляем положение квадрата в пикселях
        y_pos = y * box_size_pixels
        x_pos = x * box_size_pixels
        # Устанавливаем начальное значение сдвига для каждой строки и колонки в ноль
        y_offset = 0
        x_offset = 0

        # Для каждой строки и колонки кроме первой, проверяем наличие смещения
        if y > 0:
            y_offset = -1 * y  # уменьшаем y_pos на 1 пиксель на каждую последующую строку
        if x > 0:
            x_offset = -1 * x  # уменьшаем x_pos на 1 пиксель на каждую последующую колонку

        # Корректируем положение квадрата с учетом сдвига
        y_pos += y_offset
        x_pos += x_offset

        # Извлекаем квадрат из изображения
        square = img_qr[y_pos:y_pos + box_size_pixels, x_pos:x_pos + box_size_pixels]
        # Вычисляем средний цвет квадрата
        module_color = np.mean(square)
        
        if module_color < 128:  # Если модуль черный
            # Выбираем случайное изображение
            random_img_path = random.choice(all_images)
            all_images.remove(random_img_path)
            img = cv2.imread(random_img_path)
            brightness_offset = 0  # Можете выбрать любое другое значение
            img = cv2.subtract(img, np.ones_like(img) * brightness_offset)
            # Ограничиваем значения пикселей, чтобы они оставались в диапазоне [0, 255]
            img = np.clip(img, 0, 255)
            h, w, _ = img.shape 
            min_edge = min(h, w)
            yoff = (h - min_edge) // 2
            xoff = (w - min_edge) // 2
            squared = img[yoff:yoff+min_edge, xoff:xoff+min_edge]
            squared_resized = cv2.resize(squared, (box_size_pixels, box_size_pixels))
            # Вставляем изображение вместо черного квадрата
            #img_qr[y_pos:y_pos + box_size_pixels, x_pos:x_pos + box_size_pixels] = squared_resized
            final_img_collage[y_pos:y_pos + box_size_pixels, x_pos:x_pos + box_size_pixels] = squared_resized

# Сохраняем результирующее изображение
cv2.imwrite('final_qr_collage.png', final_img_collage)

# Конвертировать изображение в градации серого
gray_qr = cv2.cvtColor(img_qr, cv2.COLOR_BGR2GRAY)


# Сохранить бинаризованное изображение
cv2.imwrite('final_qr_collage_bw.png', gray_qr)
