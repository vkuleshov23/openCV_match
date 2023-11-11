# Программа Python для иллюстрации
# соответствия шаблона

import cv2
import sys
import numpy as np
import math
# from imutils.video import VideoStream
# import imutils
# from time import sleep

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
# Поправка на ширину рамки в таблице правая/левая
LINE_WIDTH = 10
# Поправка на ширину рамки в таблице верхняя/нижняя
LINE_HEIGH = 10
# Ядро свертки для размытия изображения (должно быть нечетным)
BLUR_CORE_CONVULTION = (3, 3)

# WAY = "/home/pi/"
WAY = "/home/pc1/myprojects/tyap-lyap/"
# Имя файла для результатов
FILE = WAY + "patterns_result.txt"
# Порог вхождения совпадений
TRESHOLD = 0.8

matrix_size = 6
matrix =   [[0,0,0,0,0,0], 
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0]]
# Смещение (начало и конец пикселей области ячеек таблицы на картинке)
shift_x = 256;
shift_end_x = 1140;
shift_y = 253;
shift_end_y = 1104;
# Размер ячеек
x_cell_size = int((shift_end_x - shift_x) / matrix_size)
y_cell_size = int((shift_end_y - shift_y) / matrix_size)
# Координаты и размер NS ячейки в таблице
NS_x = -1
NS_y = -1
NS_w = -1
NS_h = -1

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

def writeToFILE(matrix_):
    # Запись результатов в файл
    file = open(FILE, "w")
    result = ""
    x = 0
    # Запись матрицы
    while x < matrix_size:
        y = 0
        while y < matrix_size:
            result += str(matrix[x][y])
            y += 1
        x += 1

    file.write(result + "\n")
    file.close()

def fillMatrix(index):
    i = 0
    string = ""
    if NS_x > 0:
        global shift_end_x
        global shift_x
        global shift_end_y
        global shift_y
        global x_cell_size
        global y_cell_size 
        shift_end_x = NS_x + (NS_w)
        shift_y = NS_y + (NS_h)
        shift_x = shift_end_x - NS_w*matrix_size-1
        shift_end_y = shift_y + NS_h*matrix_size
        x_cell_size = int((shift_end_x - shift_x) / matrix_size)
        y_cell_size = int((shift_end_y - shift_y) / matrix_size)
        print("x1: " + str(shift_x) + " y1: " + str(shift_y) + " x2: " + str(shift_end_x) + " y2: " + str(shift_end_y) + " w: " + str(x_cell_size) + " h: " + str(y_cell_size))
    while i < len(average_sizes):
        # Получение координат пикселей центров объектов
        X = int(average_points[i][0] + average_sizes[i][0]/2)
        Y = int(average_points[i][1] + average_sizes[i][1]/2)
        # Сопоставление координат найденных объектов ячейкам таблицы
        x = math.floor((X-shift_x) / x_cell_size)
        y = math.floor((Y-shift_y) / y_cell_size)
        
        matrix[y][x] = index
        i += 1

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
            print(str(width) + "  " + str(height))
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


# # Создаём кадр из видеопотока
# img = cv2.VideoCapture(0) # Открываем камеру
# img.set(cv2.CAP_PROP_FPS, 30) # Частота кадров
# img.set(cv2.CAP_PROP_FRAME_WIDTH, 800) # Ширина кадров в видеопотоке.
# img.set(cv2.CAP_PROP_FRAME_HEIGHT, 600) # Высота кадров в видеопотоке.
# # Получаем кадр с камеры
# _, img_rgb = img.read()
# Добавление размытости
# img_rgb = cv2.GaussianBlur(img_rgb, BLUR_CORE_CONVULTION , 0)

#Читаем кадр из файла
img_rgb = cv2.imread(WAY + 'Table4.png')
# Преобразовать изображение в оттенки серого
img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
# Условие для отладки
i = 0
NS_template = cv2.imread(WAY + 'NS.png', 0)
findingWithResize(NS_template, MIN, MAX, MODULE)
if len(average_sizes) > 0:
    NS_w = average_sizes[0][0] + LINE_WIDTH
    NS_h = average_sizes[0][1] + LINE_HEIGH
    NS_x = average_points[0][0]
    NS_y = average_points[0][1]
    print("x: " + str(NS_x) + " y: " + str(NS_y) + " w: " + str(NS_w) + " h: " + str(NS_h))
    average_points.clear()
    average_sizes.clear()

while i < len(sys.argv)-1:
    # Считываем шаблон
    template__ = cv2.imread(sys.argv[i+1] , 0)
    findingWithResize(template__, MIN, MAX, MODULE)
    fillMatrix(i+1)
    average_points.clear()
    average_sizes.clear()
    i += 1
# Запись в файл
writeToFILE(matrix)
# # Освобождаем камеру
# img.release()
