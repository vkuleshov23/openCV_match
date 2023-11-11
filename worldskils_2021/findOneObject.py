# Программа Python для иллюстрации
# соответствия шаблона

import cv2
import sys
import numpy as np
import math

# Список для усредненых точек найденных шаблонов на картинке(чтобы не было наслоения найденного одного и того же изображения)
# чтобы можно было проверять на уникальность
average_points = []
# Аналогично, только хранятся расстояния average_sizes[0] соответвует average_pionts[0] | [1] == [1] | ...
average_sizes = []
# Константа, хранящая допустимую разницу размера, при котором не будет записываться новое значение
# Пример: (точка 100, 100 не будет записываться, если имеются точки: (100-DIFFERENCE, 100), (100, 100-DIFFERENCE), (100-DIFFERENCE, 100-DIFFERENCE), (100+DIFFERENCE, 100), ...) 
DIFFERENCE = 50
# Минимальный процент от размера шаблона
MIN = 90
# Максимальный процент от размера шаблона (максимум - 100)
MAX = 100
# Модуль разницы размеров шаблона
MODULE = 5
# Ядро свертки для размытия изображения (должно быть нечетным)
BLUR_CORE_CONVULTION = (3, 3)
# Имя файла для результатов
FILE = "/home/pi/patterns_result.txt"
# Порог вхождения совпадений
TRESHOLD = 0.8

template__ = None
# Добавление точки в список найденных значений, если оно не в пределах другого изображения
def addAveragePoint(point, minDif, w, h):
    # Нахоим среднее из положений одного и того же изображения
    for pt in average_points:
        if point[0] <= pt[0] + minDif and point[0] >= pt[0] - minDif:
            if point[1] <= pt[1] + minDif and point[1] >= pt[1] - minDif:
                return
    # Если проверка прошла, то добавляем элемент (полагая, что это новый)
    average_points.append(point)
    average_sizes.append((w,h))

def writeToFILE(data):
    # Запись результатов в файл
    file = open(FILE, "w")
    file.write(data)
    file.close()

def getFoundPattern(index):
    filename = sys.argv[index]
    string = ""
    i = 0
    while i < len(average_sizes):
        # Получение координат пикселей центров объектов
        X = int(average_points[i][0] + average_sizes[i][0]/2)
        Y = int(average_points[i][1] + average_sizes[i][1]/2)
        string += filename[0:len(filename)-4] + "\n"
        i += 1
    return string

# Основная функция (вызывает другие), тут проходит уменьшение шаблона и поиск шаблона на изображении
def findingWithResize(template, MinPercent, maxPercent, module):
    if ((MinPercent < 0 or MinPercent > 150) or (maxPercent > 150 or maxPercent < 0) or (maxPercent < MinPercent)):
        print("Wrong MIN, MAX sizes")
        exit()
    size = maxPercent
    while size >= MinPercent:
        # Ищем только если шаблон увеличится на module процентов
        if size%module == 0:
            # Нахождение ширины и высоты
            width = int(template.shape[1] * size / 100)
            height = int(template.shape[0] * size / 100)
            dsize = (width, height)
            if getContourse(cv2.resize(template, dsize)) == True:
                 return True
        size -= 1
    return False

# Поиск шаблона
def getContourse(template):
  
    # Сохраняем ширину и высоту шаблона
    w, h = template.shape[::-1]
  
    # Выполняем операции сопоставления.
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
    # Сохраняем координаты совпадающей области в массиве
    # Координаты упорядочены по x, y (запись проходит вдоль икса)
    loc = np.where( res >= TRESHOLD) 
    # Флаг о том, что надо прекращать (для отладки)
    for pt in zip(*loc[::-1]):
        addAveragePoint(pt, DIFFERENCE, w, h)


# Создаём кадр из видеопотока
img = cv2.VideoCapture(0) # Открываем камеру
img.set(cv2.CAP_PROP_FPS, 30) # Частота кадров
img.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) # Ширина кадров в видеопотоке.
img.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) # Высота кадров в видеопотоке.
# Получаем кадр с камеры
_, img_rgb = img.read()
# Добавление размытости
# img_rgb = cv2.GaussianBlur(img_rgb, BLUR_CORE_CONVULTION , 0)

#Читаем кадр из файла
# img_rgb = cv2.imread('/home/pi/W_1.png')
# Преобразовать изображение в оттенки серого
img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
# Условие для отладки
i = 0
result = ""
while i < len(sys.argv)-1:
    # Считываем шаблон
    template__ = cv2.imread(sys.argv[i+1] , 0)
    findingWithResize(template__, MIN, MAX, MODULE)
    result += getFoundPattern(i+1)
    average_points.clear()
    average_sizes.clear()
    i += 1
# Запись в файл
if result == "":
    result = "No one object was detected\n"
writeToFILE(result)
# # Освобождаем камеру
img.release()