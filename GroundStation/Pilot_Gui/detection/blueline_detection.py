import time
import pickle
import socket
import struct
import cv2
import numpy as np
from threading import Thread

class VideoGet():
    def __init__(self):
        self.HOST = '169.254.11.41'
        self._PORT = 8480
        self.frame_data_send = ""

    def connect(self):
        while True:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #
            self.s.settimeout(1)
            try:
                self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.s.bind((self.HOST, self._PORT))
                self.connected = True
                self.msg = "Connection is Completed Video_Getter"
                self.s.listen(10)
                self.conn, self.addr = self.s.accept()
                self.connected = True
                break

            except socket.error as msg:
                self.msg = "Try to Connect" + str(msg)
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
                    if self.connected:
                        start = time.time()
                    self.connected = False
                    if not self.connected and time.time() > 1:
                        self.connect()

            packed_msg_size = self.data[:self.payload_size]
            self.data = self.data[self.payload_size:]
            msg_size = struct.unpack(">L", packed_msg_size)[0]
            while len(self.data) < msg_size:
                self.data += self.conn.recv(4096)
                if self.data == b'':
                    if self.connected:
                        start = time.time()
                    self.connected = False
                    if not self.connected and time.time() > 1:
                        self.connect()
            self.frame_data = self.data[:msg_size]
            self.frame_data_send = self.frame_data
            self.data = self.data[msg_size:]


class LineDetect():
    def __init__(self):
        self.lower_blue = np.array([90, 40, 40])
        self.upper_blue = np.array([150, 255, 255])
        self.length_in_cm = 0
        self.len_final = 0
        self.crack_type = ""
        self.init = True
        self.slopeArr = []

    def regression_hor(self, mean, len_hor):
        add = 4.9362 * mean + 0.0202577
        len_hor += len_hor * add
        return len_hor

    def regression_ver(self, mean, len_ver):
        add = 0.30194 - 0.00444151 * mean
        len_ver += len_ver * add
        return len_ver

    def start(self, cap):
        self.slopeArr = []
        blur = cv2.GaussianBlur(cap, (5, 5), cv2.BORDER_DEFAULT)
        hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

        # Threshold the HSV image to get only red colors
        mask = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
        edges = cv2.Canny(mask, 100, 200)

        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 30, maxLineGap=20)
        slope = 0
        show_cm = False

        try:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if x1 != x2:
                    slope = (y2 - y1) / (x2 - x1)
                    slope = round(slope, 3)
                    slope = abs(slope)
                if self.crack_type == "hor" and slope < 0.15:
                    self.slopeArr.append(slope)
                elif self.crack_type == "ver" and slope > 10:
                    self.slopeArr.append(slope)
                if self.crack_type == "ver" and slope > 30:
                    show_cm = True
                elif self.crack_type == "hor" and slope > 1/30:
                    show_cm = True
            slope_mean = np.mean(self.slopeArr)
        except:
            return 0

        contours = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        contours = contours[0]

        threshold_area_low = 1500
        threshold_area_high = 20000

        max_area = 0
        c_max = None
        for c in contours:
            area = cv2.contourArea(c)
            if area > threshold_area_low and area < threshold_area_high:
                if area > max_area:
                    max_area = area
                    c_max = c
                    cv2.drawContours(frame, [c], -1, (0, 255, 255), 2)

        if c_max is not None:
            leftmost = tuple(c_max[c_max[:, :, 0].argmin()][0])
            rightmost = tuple(c_max[c_max[:, :, 0].argmax()][0])
            topmost = tuple(c_max[c_max[:, :, 1].argmin()][0])
            bottommost = tuple(c_max[c_max[:, :, 1].argmax()][0])
            len_hor = bottommost[1] - topmost[1]
            len_ver = rightmost[0] - leftmost[0]

            if self.crack_type == "ver":
                self.length_in_cm = len_hor / len_ver * 1.8
                self.len_final = self.regression_ver(slope_mean, self.length_in_cm)
            elif self.crack_type == "hor":
                self.length_in_cm = len_ver / len_hor * 1.8
                self.len_final = self.regression_hor(slope_mean, self.length_in_cm)

            if len_hor > len_ver:
                self.crack_type = "ver"
            else:
                self.crack_type = "hor"

        try:
            if show_cm:
                cv2.circle(frame, leftmost,     3, [100, 111, 123], -1)
                cv2.circle(frame, rightmost, 3, [100, 111, 123], -1)
                cv2.circle(frame, topmost, 3, [243, 111, 123], -1)
                cv2.circle(frame, bottommost, 3, [243, 111, 123], -1)
        except Exception as msg:
            print("None" + msg)
        cv2.putText(frame, str(round(self.len_final, 5)) + "cm", (40, 25), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2,
                    cv2.LINE_AA)
        cv2.namedWindow("Length of the crack", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Length of the crack", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Length of the crack", frame)
        cv2.waitKey(1)


lineDetect = LineDetect()
video_getter = VideoGet()
video_getter.start()

while True:
    if video_getter.frame_data_send != "":
        frame_bytes = video_getter.frame_data_send
    else:
        continue
    frame = pickle.loads(frame_bytes, fix_imports=True, encoding="bytes")
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    lineDetect.start(frame)
    key = cv2.waitKey(1)

    if key == 27:
        break
