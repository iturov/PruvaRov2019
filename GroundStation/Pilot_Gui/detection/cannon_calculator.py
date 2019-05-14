import math
import time
import cv2
import numpy
import argparse

img = cv2.imread("cannon.jpg")
smallrad = input("small rad:")
largerad = input("large rad:")
small_rad = float(smallrad)
large_rad = float(largerad)
imgcopy = img.copy()

font = cv2.FONT_HERSHEY_PLAIN

cv2.putText(img, 'Small Radius : ' + str(small_rad), (300, 75), font, 1.5, (150, 250, 150), 1, cv2.LINE_AA)
cv2.putText(img, 'Large Radius : ' + str(large_rad), (300, 55), font, 1.5, (150, 250, 150), 1, cv2.LINE_AA)
font = cv2.FONT_HERSHEY_PLAIN

class Mouse():
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_PLAIN
        self.point_small_up = ()
        self.point_small_down = ()
        self.point_small_left = ()
        self.point_small_right = ()
        
        self.point_large_up = ()
        self.point_large_down = ()
        self.point_large_left = ()
        self.point_large_right = ()
        self.liste = []
        self.draw_counter = 0
        cv2.putText(img, 'point_small_up', (10, 25), self.font, 1.5, (150, 250, 150), 1, cv2.LINE_AA)
        self.isfinished = False



    def mouse_drawing(self, event, x, y, flags, params):

        if event == cv2.EVENT_LBUTTONUP and self.draw_counter == 0:
            self.point_small_up = (x, y)
            self.draw_counter += 1
            img[0:30] = imgcopy[0:30]
            cv2.putText(img,'point_small_down', (10,25), self.font, 1.5, (250, 250, 150), 1, cv2.LINE_AA)
            return 0

        if event == cv2.EVENT_LBUTTONUP and self.draw_counter == 1:

            self.draw_counter += 1
            self.point_small_down = (x, y)
            cv2.line(img, self.point_small_down, self.point_small_up, [0+len(self.liste)*40, 255, 0], 2)
            img[0:30] = imgcopy[0:30]
            cv2.putText(img,'point_small_left', (10,25), self.font, 1.5, (250, 250, 150), 1, cv2.LINE_AA)
            return 0

        if event == cv2.EVENT_LBUTTONUP and self.draw_counter == 2:
            self.point_small_left = (x, y)
            self.draw_counter+=1
            img[0:30] = imgcopy[0:30]

            cv2.putText(img, 'point_small_right', (10,25), self.font, 1.5, (250, 150, 150), 1, cv2.LINE_AA)

            return 0

        if event == cv2.EVENT_LBUTTONUP and self.draw_counter == 3:
            self.point_small_right = (x, y)
            cv2.line(img, self.point_small_left, self.point_small_right, [255, 255 - self.draw_counter*25, 0], 2)
            self.draw_counter+=1
            img[0:30] = imgcopy[0:30]
            cv2.putText(img, 'point_large_up', (10,25), self.font, 1.5, (250, 250, 150), 1, cv2.LINE_AA)
            return 0

        if event == cv2.EVENT_LBUTTONUP and self.draw_counter== 4:
            self.point_large_up = (x, y)
            self.draw_counter+=1
            img[0:30] = imgcopy[0:30]
            cv2.putText(img, 'point_large_down', (10,25), self.font, 1.5, (150, 250, 250), 1, cv2.LINE_AA)
            return 0

        if event == cv2.EVENT_LBUTTONUP and self.draw_counter == 5:
            self.point_large_down = (x, y)
            self.draw_counter += 1
            cv2.line(img, self.point_large_up, self.point_large_down, [255, 255, self.draw_counter*50], 2)
            img[0:30] = imgcopy[0:30]
            cv2.putText(img, 'point_large_left', (10,25), self.font, 1.5, (250, 250, 150), 1, cv2.LINE_AA)
            return 0

        if event == cv2.EVENT_LBUTTONUP and self.draw_counter == 6:
            self.point_large_left = (x, y)
            self.draw_counter += 1
            img[0:30] = imgcopy[0:30]
            cv2.putText(img, 'point_large_right', (10,25), self.font, 1.5, (255, 250, 150), 1, cv2.LINE_AA)
            return 0

        if event == cv2.EVENT_LBUTTONUP and self.draw_counter == 7:
            self.point_large_right = (x, y)
            self.draw_counter += 1
            cv2.line(img, self.point_large_left, self.point_large_right, [self.draw_counter*40, 130, 50], 2)
            img[0:30] = imgcopy[0:30]
            cv2.putText(img, 'finished', (10,25), self.font, 1.5, (255, 250, 150), 1, cv2.LINE_AA)
            self.pix_small_rad = math.sqrt((self.point_small_up[0]-self.point_small_down[0])**2+(self.point_small_up[1]-self.point_small_down[1])**2)
            self.pix_large_rad = math.sqrt((self.point_large_up[0]-self.point_large_down[0])**2+(self.point_large_up[1]-self.point_large_down[1])**2)
            self.pix_small_len = math.sqrt((self.point_small_left[0]-self.point_small_right[0])**2+(self.point_small_left[1]-self.point_small_right[1])**2)
            self.pix_large_len = math.sqrt((self.point_large_left[0]-self.point_large_right[0])**2+(self.point_large_left[1]-self.point_large_right[1])**2)
            self.isfinished = True
            return 0


mouse = Mouse()
cv2.namedWindow("Frame")
cv2.setMouseCallback("Frame", mouse.mouse_drawing)
start = time.time()
while True:
    cv2.imshow("Frame", img)
    cv2.waitKey(10)
    if time.time() - start > 1:
        start = time.time()
        if mouse.isfinished:
            small_len = mouse.pix_small_len/mouse.pix_small_rad*small_rad
            large_len = mouse.pix_large_len/mouse.pix_large_rad*large_rad
            break
cv2.destroyAllWindows()
img[0:30] = imgcopy[0:30]
cv2.putText(img, "Small len : "+str(round(small_len, 4)), (10, 25), font, 1.5, (255, 250, 150), 1, cv2.LINE_AA)
cv2.putText(img, 'Large len : '+str(round(large_len, 4)), (10, 45), font, 1.5, (255, 250, 150), 1, cv2.LINE_AA)
cv2.imshow("Result ", img)
cv2.waitKey(0)



