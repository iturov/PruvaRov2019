import os
import cv2
import io
import socket
import struct
import time
import pickle
import zlib
import time

class CamServer():
    def __init__(self):
        self._host = '169.254.11.41'
        self._port = 8485

    def connect(self):
        while True:

            try:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.settimeout(1)
                self._socket.connect((self._host, self._port))
                print ("Connection is build")
                self._connected = True
                break

            except Exception as msg:
                print("try to connect")
                print("Exception is : ", msg)

            time.sleep(1)

    def send_frame(self, size, data):
        try:
            self._socket.sendall(struct.pack(">L", size) + data)
            self._connected = True
        except socket.error as msg:
            self._connected = False
            print("connection problem")
            print("socket error : ", msg)

    @property
    def connection(self):
        return self._connected



camserver = CamServer()
camserver.connect()
video_source = 0
fps = 25
cam = cv2.VideoCapture(video_source)
#cam.set(3,800)
#cam.set(4,600)
#time.sleep(2)
#cam.set(15, -8.0)

cam.set(cv2.CAP_PROP_FPS, fps) 
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 60]


start = time.time()
img_counter = 0

while True:

    if not camserver.connection:
        cam.release()
        camserver.connect()
        cam = cv2.VideoCapture(video_source)
        cam.set(cv2.CAP_PROP_FPS, fps)


    ret, frame = cam.read()

    if time.time() - start > 1:
        print("fps : ", img_counter)
        start = time.time()
        img_counter = 0

    result, frame = cv2.imencode('.jpg', frame, encode_param)

    data = pickle.dumps(frame, 0)
    size = len(data)

    camserver.send_frame(size=size, data=data)

    img_counter += 1

cam.release()
