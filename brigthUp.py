import cv2 as cv
import numpy as np
image = cv.imread("stelazh.png")



cv.imwrite('brIMG.png', increase_brightness(image,50))