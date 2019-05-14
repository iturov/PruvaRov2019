import time
import pickle
import socket
import struct
import cv2
import numpy as np
import math
from threading import Thread

def nothing(x):
    print('Nothing')

cv2.namedWindow('Output')
cv2.createTrackbar('adaptation', 'Output', 127, 255, nothing)

class VideoGet():
    def __init__(self):
        self.HOST = "169.254.196.68" 
        self._PORT = 8480
        self.frame_data_send = ""

    def connect(self):
        while True:

            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.settimeout(1)
            print('Socket created Video_Getter')

            try:
                self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.s.bind((self.HOST, self._PORT))
                print("self.host", self._PORT)
                print('Socket bind complete Video_Getter')
                self.connected = True
                self.msg = "Connection is Completed Video_Getter"
                self.s.listen(10)
                print('Socket now listening Video_Getter')
                self.conn, self.addr = self.s.accept()
                self.connected = True
                break

            except socket.error as msg:
                print(msg, "in Video_Getter ")
                self.msg = "Try to Connect"
                time.sleep(1)
        self.data = b""
        self.payload_size = struct.calcsize(">L")

    def start(self):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        self.connect()

        start = time.time()
        while True:
            if time.time() - start > 1:
                start = time.time()

            while len(self.data) < self.payload_size:
                self.data += self.conn.recv(4096)
                if self.data == b'':
                    if self.connected == True:
                        start = time.time()
                    self.connected = False
                    if self.connected == False and time.time() > 1:
                        self.connect()

            packed_msg_size = self.data[:self.payload_size]
            self.data = self.data[self.payload_size:]
            msg_size = struct.unpack(">L", packed_msg_size)[0]
            while len(self.data) < msg_size:
                self.data += self.conn.recv(4096)
                if self.data == b'':
                    if self.connected == True:
                        start = time.time()
                    self.connected = False
                    if self.connected == False and time.time() > 1:
                        self.connect()
            self.frame_data = self.data[:msg_size]
            self.frame_data_send = self.frame_data
            self.data = self.data[msg_size:]


class Mouse():
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_PLAIN
        self.leftTop    = None
        self.rightTop   = None
        self.leftBottom = None
        self.rightBottom= None
        self.draw_counter = 0

    def mouse_drawing(self, event, x, y, flags, params):

        if event == cv2.EVENT_LBUTTONUP and self.draw_counter == 0:
            self.leftTop = (x, y)
            self.draw_counter += 1
            return 0
        if event == cv2.EVENT_LBUTTONUP and self.draw_counter == 1:
            self.rightTop = (x, y)
            self.draw_counter += 1
            return 0
        if event == cv2.EVENT_LBUTTONUP and self.draw_counter == 2:
            self.rightBottom = (x, y)
            self.draw_counter += 1
            return 0
        if event == cv2.EVENT_LBUTTONUP and self.draw_counter == 3:
            self.leftBottom = (x, y)
            self.draw_counter += 1
            return 0
        if event == cv2.EVENT_LBUTTONUP and self.draw_counter == 4:
            self.draw_counter = 0
            return 0

class ShapeDetection:
    def __init__(self):
        self.frame = None
        self.triangle_ctr = 0
        self.line_ctr = 0
        self.square_ctr = 0
        self.circle_ctr = 0
        self.LH = 127
        thresh1 = None
        self.gray = None
        self.triangle_countour = None
        self.triangle_countour_2 = None
        self.mid_points = []
        self.output = cv2.imread('shapes.png')
        self.triangle = cv2.imread('triangle.jpeg')
        self.template_triangle()

    def start(self, image, LH):
        self.frame = 255 - image.copy()
        self.detectShape()
        self.LH = LH


    def template_triangle(self):
        triangle_gray = cv2.cvtColor(self.triangle, cv2.COLOR_BGR2GRAY)
        ret, thresh1 = cv2.threshold(triangle_gray, 180, 255, 0)
        contours, _ = cv2.findContours(thresh1, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        self.triangle_contour = contours[0]

    def detectShape(self):
        resized =  cv2.resize(self.frame, None, fx=1, fy=1, interpolation=cv2.INTER_CUBIC)
        ratio = self.frame.shape[0] / float(resized.shape[0])
        self.gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        ret, thresh1 = cv2.threshold(self.gray, self.LH, 255, cv2.THRESH_BINARY)
        cv2.imshow('gray', self.gray)
        #thresh1 = cv2.adaptiveThreshold(self.gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C , cv2.THRESH_BINARY, 5, 6)
        circles = cv2.HoughCircles(thresh1, cv2.HOUGH_GRADIENT, 1, 50,
                                   param1=10, param2=25, minRadius=10, maxRadius=70)
        cv2.imshow('THRESH', thresh1)
        contours = cv2.findContours(thresh1.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        contours = contours[0]      
        threshold_area_low = 500  
        threshold_area_high = 15000 
        cXtmp = 0
        cYtmp = 0
        goNext = False
        j = 0

        for i, c in enumerate(contours):

            area = cv2.contourArea(c)
            print("area:", area)

            if area > threshold_area_low and area < threshold_area_high:
                M = cv2.moments(c)
                try:
                    cX = int((M['m10'] / M['m00']) * ratio)
                    cY = int((M['m01'] / M['m00']) * ratio)
                except (ZeroDivisionError):
                    cX = 0
                    cY = 0

                if (abs(cXtmp - cX) < 40 and abs(cYtmp - cY) < 40):
                    continue

                cXtmp = cX
                cYtmp = cY

                shape = self.detectType(c)
                c = c.astype("float")
                c *= ratio
                c = c.astype("int")

                if shape == "triangle":
                    cv2.drawContours(self.frame, [c], -1, (255, 255, 0), 2)
                    cv2.putText(self.frame, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

                if shape == "line":
                    cv2.drawContours(self.frame, [c], -1, (255, 255, 0), 2)
                    cv2.putText(self.frame, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)

                if shape == "square":
                    cv2.drawContours(self.frame, [c], -1, (255, 255, 0), 2)
                    cv2.putText(self.frame, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

                if shape == "circle":
                    cv2.drawContours(self.frame, [c], -1, (255, 255, 0), 2)
                    cv2.putText(self.frame, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                i = i.astype("float")
                i *= ratio
                i = i.astype("int")
                # draw the outer circle
                cv2.circle(self.frame, (i[0], i[1]), i[2], (255, 0, 0), 2)
                cv2.putText(self.frame, "Circle", (i[0], i[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            self.circle_ctr = len(circles[0, :])
        else:
            print("circles is None")

        self.frame = 255 - self.frame
        # merge 2 img
        x_offset = y_offset = 0
        self.frame[y_offset:y_offset + self.output.shape[0], x_offset:x_offset + self.output.shape[1]] = self.output

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(self.frame, str(self.triangle_ctr),(4, 105), font, 1, (0, 0, 255), 3, cv2.LINE_AA)
        cv2.putText(self.frame, str(int((self.square_ctr/2) +2)), (4, 260), font, 1, (0, 0, 255), 3, cv2.LINE_AA)
        cv2.putText(self.frame, str(int(self.line_ctr/2) +2), (4, 180), font, 1, (0, 0, 255), 3 , cv2.LINE_AA)
        cv2.putText(self.frame, str(self.circle_ctr), (4, 35), font, 1, (0, 0, 255), 3, cv2.LINE_AA)

        cv2.namedWindow("Output")
        cv2.setMouseCallback("Output", Mouse.mouse_drawing)
        cv2.imshow('Output', self.frame)
        cv2.waitKey(10)

        self.triangle_ctr = 0
        self.square_ctr = 0
        self.line_ctr = 0
        self.circle_ctr = 0

    def detectType(self, c):
        shape = "unidentified"
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        match1 = cv2.matchShapes(c, self.triangle_contour,   3, 0.0)
        match2 = cv2.matchShapes(c, self.triangle_contour_2, 3, 0.0)
        match3 = cv2.matchShapes(c, self.triangle_contour_3, 3, 0.0)

        if len(approx) == 4:
            leftmost = tuple(c[c[:, :, 0].argmin()][0])
            rightmost = tuple(c[c[:, :, 0].argmax()][0])
            topmost = tuple(c[c[:, :, 1].argmin()][0])
            bottommost = tuple(c[c[:, :, 1].argmax()][0])
            leftright = math.sqrt((rightmost[1] - leftmost[1]) ** 2 + (rightmost[0] - leftmost[0]) ** 2)
            topbottom = math.sqrt((topmost[1] - bottommost[1]) ** 2 + (topmost[0] - bottommost[0]) ** 2)

            if topbottom > 150 or leftright > 150:
                shape = "undefined"
                return shape

            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w / float(h)

            rightPointRow = int(y + (h / 2))
            rightPointCol = int(x + (w / 2)) + int((w / 4))

            leftPointRow = int(y + (h / 2))
            leftPointCol = int(x + (w / 2)) - int((w / 4))

            rightCheck = True
            leftCheck = True

            if (rightPointCol > self.gray.shape[1] ):
                rightCheck = False

            if (leftPointCol < 0 ):
                leftCheck = False

            if ar >= 0.5 and ar <= 1.5 :
                if rightCheck:
                    if self.gray[rightPointRow, rightPointCol] > self.LH+10:
                        self.square_ctr += 1
                        shape = "square"
                        return shape
                    else:
                        self.line_ctr += 1
                        shape = "line"
                elif leftCheck:
                    if self.gray[leftPointRow, leftPointCol] > self.LH+10:
                        self.square_ctr += 1
                        shape = "square"
                        return shape
                    else:
                        self.line_ctr += 1
                        shape = "line"
            else:
                self.line_ctr += 1
                shape = "line"
            return shape
        elif (match1 < 0.04 or match2 < 0.04 or match3 < 0.04) and len(approx) < 5:
            print(len(approx))
            self.triangle_ctr += 1
            shape = "triangle"
            return shape
        else:
            print(self.circle_ctr)
            self.circle_ctr += 1
            shape = "circle"
            return shape


video_getter = VideoGet()
video_getter.start()

mouse = Mouse()
shapeDetector = ShapeDetection()
frame_loop = False

while True:
    if video_getter.frame_data_send != "":
        frame_bytes = video_getter.frame_data_send
    else:
        continue
    frame = pickle.loads(frame_bytes, fix_imports=True, encoding="bytes")
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

    LH = cv2.getTrackbarPos('adaptation', 'Output')
    # Perspective Transformation on click
    if mouse.draw_counter == 4:
        src_pts = np.array([mouse.leftTop, mouse.rightTop, mouse.rightBottom, mouse.leftBottom], dtype=np.float32)
        dst_pts = np.array([[0, 0], [640, 0], [640, 480], [0, 480]], dtype=np.float32)
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        warp = cv2.warpPerspective(frame, M, (640, 480))
        shapeDetector.start(warp, LH)
    else:
        shapeDetector.start(frame, LH)
    # if the 'c' key is pressed, break from the loop
    key = cv2.waitKey(1)

    if key == 27:
        break
