# Программа Python для иллюстрации
# соответствия шаблона

import cv2
import sys
import numpy as np
import math
# from imutils.video import VideoStream
# import imutils
# from time import sleep

# Проверка, что аргумент (шаблон) был передан
if len(sys.argv) < 2:
    print("have no argument!    (png, jpg, ...)")
    exit()

# Читать основное изображение

# vs = VideoStream(src=0, usePiCamera=False, resolution=(1024, 720), framerate=32).start()
# sleep(2)
# img_rgb = None
# Список для усредненых точек найденных шаблонов на картинке(чтобы не было наслоения найденного одного и того же изображения)
# чтобы можно было проверять на уникальность
average_points = []
# Аналогично, только хранятся расстояния average_sizes[0] соответвует average_pionts[0] | [1] == [1] | ...
average_sizes = []
# Константа, хранящая допустимую разницу размера, при котором не будет записываться новое значение
# Пример: (точка 100, 100 не будет записываться, если имеются точки: (100-DIFFERENCE, 100), (100, 100-DIFFERENCE), (100-DIFFERENCE, 100-DIFFERENCE), (100+DIFFERENCE, 100), ...) 
DIFFERENCE = 20
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

matrix_size = 6
shift_x = 256;
shift_end_x = 1134;
shift_y = 253;
shift_end_y = 1098;
x_cell_size = int((shift_end_x - shift_x) / matrix_size);
y_cell_size = int((shift_end_y - shift_y) / matrix_size);

matrix =   [[0,0,0,0,0,0], 
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0]]
# Считываем шаблон
template__ = cv2.imread(sys.argv[1] , 0)

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

def writeToFILE(matrix_):
    # Запись результатов в файл
    file = open(FILE, "w")
    result = ""
    x = 0
    while x < matrix_size:
        y = 0
        while y < matrix_size:
            result += str(matrix[x][y])
            y += 1
        x += 1
    file.write(result + "\n")
    file.close()

def getDataForFILE(index):
    i = 0
    string = ""
    print(str(index))
    while i < len(average_sizes):
        Y = int(average_points[i][0] + average_sizes[i][0]/2)
        # print(str(Y))
        X = int(average_points[i][1] + average_sizes[i][1]/2)
        # print(str(X))
        y = math.floor((Y-shift_y) / y_cell_size)
        # print(str((Y-shift_y)) + " " + str(y))
        x = math.floor((X-shift_x) / x_cell_size)
        # print(str((X-shift_x)) + " " + str(x) + "\n")
        string += str(x) + " " + str(y) + " "
        matrix[x][y] = index
        i += 1
    result = "" + str(i) + " "
    result += string
    return result + "\n"


def getDataForFILE(index):
    i = 0
    string = ""
    while i < len(average_sizes):
        X = int(average_points[i][0] + average_sizes[i][0]/2)
        Y = int(average_points[i][1] + average_sizes[i][1]/2)
        x = int((X-shift_x) / x_cell_size)
        y = int((Y-shift_y) / y_cell_size)
        string += str(x) + " " + str(y) + " "
        i += 1
    result = "" + str(i) + " "
    result += string
    return result + "\n"

# Основная функция (вызывает другие), тут проходит уменьшение шаблона и поиск шаблона на изображении
def findingWithResize(MinPercent, maxPercent, module):
    if ((MinPercent < 0 or MinPercent > 150) or (maxPercent > 150 or maxPercent < 0) or (maxPercent < MinPercent)):
        print("Wrong MIN, MAX sizes")
        exit()
    size = maxPercent
    while size >= MinPercent:
        # Ищем только если шаблон увеличится на module процентов
        if size%module == 0:
            # Нахождение ширины и высоты
            width = int(template__.shape[1] * size / 100)
            height = int(template__.shape[0] * size / 100)
            dsize = (width, height)
            if getContourse(cv2.resize(template__, dsize)) == True:
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
img_rgb = cv2.imread('/home/pi/Table.png')
# Добавление размытости
# img_rgb = cv2.GaussianBlur(img_rgb, BLUR_CORE_CONVULTION , 0)
# Преобразовать изображение в оттенки серого
img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
# Условие для отладки
findingWithResize(MIN, MAX, MODULE)
# Запись в файл
getDataForFILE(1)
writeToFILE(matrix)
