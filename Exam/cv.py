
import cv2
import sys
import numpy as np

if len(sys.argv) < 3:
    print("have no argument!    (png, jpg, ...)")
    exit()


WIDTH = 800
HEIGHT = 600
site = [0, WIDTH]

img_rgb = None
average_points = []
average_sizes = []

DIFFERENCE = 20
MIN = 50
MAX = 120
MODULE = 5

rotat = 0
degree_module = 1
degree = [-50, 50]

BLUR_CORE_CONVULTION = (3, 3)
FILE = "result.txt"
TRESHOLD = 0.8
template__ = cv2.imread(sys.argv[2] , 0)


def setSite(site_):
    global site
    if site_ == "L":
        site = [0, int(WIDTH/2)]
    elif site_ == "R":
        site = [int(WIDTH/2), WIDTH]

def setDegree(deg):
    if len(sys.argv) > 3:
        global degree
        degree = [-int((int(deg)/2)+1), int((int(deg)/2)+1)]

def findAverage(array):
    x = 0
    x_sum = 0
    y = 0
    y_sum = 0
    
    for p in array:
        x_sum += p[0]
        y_sum += p[1]

    return ((int)(x_sum/len(array)), (int)(y_sum/len(array)))

def checkPixel(minPoint, point):
    
    if point[0] > (minPoint[0] + DIFFERENCE):
        return False
    if point[1] > (minPoint[1] + DIFFERENCE):
        return False
    return True

def addAveragePoint(points, minDif, w, h):
    point = findAverage(points)
    for pt in average_points:
        if point[0] <= pt[0] + minDif and point[0] >= pt[0]:
            return
        if point[0] >= pt[0] - minDif and point[0] <= pt[0]:
            return
        if point[1] <= pt[1] + minDif and point[1] >= pt[1]:
            return
        if point[1] >= pt[1] - minDif and point[1] <= pt[1]:
            return
    average_points.append(point)
    average_sizes.append((w,h))

def clearAverageLists():
    del average_sizes[:]
    del average_points[:]

def writeToFILE(data):
    file = open(FILE, "w")
    file.write(data)
    file.close()

def print_result():
    global rotat
    i = 0
    while i < len(average_sizes):
        cv2.rectangle(img_rgb, average_points[i], (average_points[i][0] + average_sizes[i][0], average_points[i][1] + average_sizes[i][1]), (0,0,255), 1, 8, 0)
        cv2.putText(img_rgb, str(average_points[i][0]) + ", " + str(average_points[i][1]) + ", " + str(rotat), (average_points[i][0],average_points[i][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
        i += 1

def getDataForFILE():
    i = 0
    string = ""
    while i < len(average_sizes):
        string += str((average_points[i][0] + average_sizes[i][0])) + ", " + str((average_points[i][1] + average_sizes[i][1])) + ", " + str(rotat) + "\n"
        i += 1
    if string == "" :
        # string += "Template not found :(\n"
        string += "---------------------\n"
    return string

def rotation(template):
    global rotat
    rotat = 0
    for deg in range(degree[0], degree[1]):
        if deg % degree_module == 0:
            (h, w) = template.shape[:2]
            center = (int(w / 2), int(h / 2))
            rotation_matrix = cv2.getRotationMatrix2D(center, deg, 1)
            route_img = cv2.warpAffine(template, rotation_matrix, (w, h))
            if getContourse(route_img) == True:
                rotat = int(deg)
                return True
    return False

def findingWithResize(MinPercent, maxPercent, module):
    if ((MinPercent < 0 or MinPercent > 150) or (maxPercent > 150 or maxPercent < 0) or (maxPercent < MinPercent)):
        print("Wrong MIN, MAX sizes")
        exit()
    for size in range(MinPercent, maxPercent):
        if size%module == 0:
            width = int(template__.shape[1] * size / 100)
            height = int(template__.shape[0] * size / 100)
            dsize = (width, height)
            if rotation(cv2.resize(template__, dsize)) == True:
                # return True
                return False
    return False

def getContourse(template):
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
    loc = np.where( res >= TRESHOLD) 
    flag = False
    flag_about_in = False
    points = []
    minimum = (999999, 999999)
    for pt in zip(*loc[::-1]):
        if minimum[0] > pt[0]:
            if minimum[1] > pt[1]:
                minimum = pt
        if checkPixel(minimum, pt) == True:
            points.append(pt)
        else:
            addAveragePoint(points, DIFFERENCE, w, h)
            del points[:]
            minimum = pt
            points.append(pt)
        flag_about_in = True
        flag = True
    if flag_about_in == True:    
        addAveragePoint(points, DIFFERENCE, w, h)
    return flag


setSite(sys.argv[1])
setDegree(sys.argv[3])

img = cv2.VideoCapture(0)
img.set(cv2.CAP_PROP_FPS, 30)
img.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
img.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

stop_flag = False
# while True:
i = 0
while i != 1:
    i += 1
    _, img_rgb = img.read()
    img_rgb = img_rgb[:, site[0]:site[1]]
    img_rgb = cv2.GaussianBlur(img_rgb, BLUR_CORE_CONVULTION , 0)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    if stop_flag == False:
        stop_flag = findingWithResize(MIN, MAX, MODULE)
        # print_result()
       	print(getDataForFILE())
        #writeToFILE(getDataForFILE())
        clearAverageLists()
        # cv2.imshow('result',img_rgb)
    # if cv2.waitKey(1) == 27:
    #     break
img.release()