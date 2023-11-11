# Программа Python для иллюстрации
# соответствия шаблона

import cv2
import sys
import numpy as np
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
# Считываем шаблон
template__ = cv2.imread(sys.argv[1] , 0)

# Поиск среднего значения из найденных точек изображений шаблона (при одинаковом размере шаблона), чтобы получить точно 1 значение
# def findAverage(array):
#     x = 0
#     x_sum = 0
#     y = 0
#     y_sum = 0
    
#     for p in array:
#         x_sum += p[0]
#         y_sum += p[1]

#     return ((int)(x_sum/len(array)), (int)(y_sum/len(array)))

# Проверка на то, что точка еще в пределах 1го найденного изображения (из многих)
# def checkPixel(minPoint, point):
    
#     if point[0] > (minPoint[0] + DIFFERENCE):
#         return False
#     if point[1] > (minPoint[1] + DIFFERENCE):
#         return False
#     return True

# Добавление точки в список найденных значений, если оно не в пределах другого изображения
def addAveragePoint(point, minDif, w, h):
    # Нахоим среднее из положений одного и того же изображения
    # point = findAverage(points)
    for pt in average_points:
        if point[0] <= pt[0] + minDif and point[0] >= pt[0] - minDif:
            if point[1] <= pt[1] + minDif and point[1] >= pt[1] - minDif:
                return
    # Если проверка прошла, то добавляем элемент (полагая, что это новый)
    average_points.append(point)
    average_sizes.append((w,h))

# Очистка списка (нужна, пока используется запись камеры, а не фото)
# def clearAverageLists():
#     average_sizes.clear()
#     average_points.clear()

def writeToFILE(data):
    # Запись результатов в файл
    file = open(FILE, "w")
    # print(getDataForFILE())
    file.write(data)
    file.close()

# Отрисовка рамки объекта и ее положения 
def print_result():
    i = 0
    while i < len(average_sizes):
        # print(average_points[i], " : ", average_sizes[i])
        # Отрисовка рамки
        cv2.rectangle(img_rgb, average_points[i], (average_points[i][0] + average_sizes[i][0], average_points[i][1] + average_sizes[i][1]), (0,255,0), 2, 8, 0)
        # Отрисовка координат
        cv2.putText(img_rgb, str(average_points[i][0]) + ", " + str(average_points[i][1]), (average_points[i][0],average_points[i][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
        #print(str(average_points[i]))
        i += 1

def getDataForFILE():
    i = 0
    string = ""
    while i < len(average_sizes):
        string += str(average_points[i]) + ", " + str(average_sizes[i][0]) + ", " + str(average_sizes[i][1]) + ";"
        i += 1
    result = "" + str(i) + "\n"
    result += string
    return result + "\n"

# def rotation(template):
#     for deg in range(0, 360):
#         if deg % 5 == 0:
#             (h, w) = template.shape[:2]
#             center = (int(w / 2), int(h / 2))
#             rotation_matrix = cv2.getRotationMatrix2D(center, deg, 1)
#             route_img = cv2.warpAffine(template, rotation_matrix, (w, h))
#             if getContourse(route_img) == True:
#                 return True
#     return False

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
            # if rotation(cv2.resize(template__, dsize)) == True:
            #     return True

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
    # cv2.imshow("result", res)

    # Сохраняем координаты совпадающей области в массиве
    # Координаты упорядочены по x, y (запись проходит вдоль икса)
    loc = np.where( res >= TRESHOLD) 
    # # Флаг о том, что надо прекращать (для отладки)
    flag = False

    # # Инициализация флага о входе в цикл
    # flag_about_in = False
    # Инициализация списка для одного изображения
    points = []
    # Инициализация минимума точки, при которой мы будем проверять, полагая, что это одно изображение
    minimum = (999999, 99999)

    for pt in zip(*loc[::-1]):
        addAveragePoint(pt, DIFFERENCE, w, h)
        
        # if minimum[0] > pt[0]:
        #     if minimum[1] > pt[1]:
        #         minimum = pt
        # Если точка является тем же изображением, то добавляем ее в список для дальнейшего поиска среднего значения
        # if checkPixel(minimum, pt) == True:
        # points.append(pt)
        # В ином случае, это другое изображение
        # else:
        #     # Добавляем старое в массив изображений
        #     addAveragePoint(points, DIFFERENCE, w, h)
        #     # Чистим список для дальнейшей записи точек нового изображения
        #     points.clear()
        #     # Устанавливаем точку как минимум для нового изобраения
        #     minimum = pt
        #     # Добавляем ее в список для дальнейшего поиска среднего значения
        #     points.append(pt)
        # flag_about_in = True
        
        # flag = True
    
    # if flag_about_in == True:    
    # addAveragePoint(pt, DIFFERENCE, w, h)
    return flag

stop_flag = False
i = 0
# while True:
while i != 1:
    i = 1
    # Создаём кадр из видеопотока
    img_rgb = cv2.imread('/home/pi/Table.png')
    # img_rgb = cv2.imread('Test_Tab_.png')
    # Добавление размытости
    # img_rgb = cv2.GaussianBlur(img_rgb, BLUR_CORE_CONVULTION , 0)
    # Преобразовать изображение в оттенки серого
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    # Условие для отладки
    if stop_flag == False:
        # Поиск всех совпадений для изображения
        stop_flag = findingWithResize(MIN, MAX, MODULE)
        # stop_flag = getContourse(template__)
        # Отрисовка рамок и координат
        print_result()
        # Запись в файл
        writeToFILE(getDataForFILE())
        # Очиска списка (для отладки)
        # clearAverageLists()
        # Выводим изображение в окно
        cv2.imshow('krasivoe',img_rgb)
    # ESC, чтобы закрыть окно
    # if cv2.waitKey(1) == 27:
    #     break
while True:
    cv2.imshow('krasivoe',img_rgb)
    if cv2.waitKey(1) == 27:
        break

# vs.stop()
cv2.destroyAllWindows()