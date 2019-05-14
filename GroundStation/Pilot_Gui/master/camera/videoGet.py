from threading import Thread
import socket
import struct
import time

class VideoGet():
    def __init__(self, ui):
        self.HOST = "169.254.196.68"
        self._PORT = 8485
        self.frame_data_send = ""
        self._ui = ui

    def connect(self):
        while True:
            if self._ui.camera_var == 0:
                self._ui.st_cameratype_lb_text = "Close"
                time.sleep(1)
                continue
            elif self._ui.camera_var == 1:
                self._ui.st_cameratype_lb_text = "Front is Waiting"
                self._PORT = 8480

            elif self._ui.camera_var == 2:
                self._ui.st_cameratype_lb_text = "Bottom is Waiting"
                self._PORT = 8485

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

                if self._ui.camera_var == 1:
                    self._ui.st_cameratype_lb_text = "Front is Open"
                elif self._ui.camera_var == 2:
                    self._ui.st_cameratype_lb_text = "Bottom is Open"
                break

            except socket.error as msg:
                print(msg, " in Video_Getter ")
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
                    if self.connected:
                        start = time.time()
                    self.connected = False
                    if not self.connected and time.time() > 1:
                        self.connect()
            self.frame_data = self.data[:msg_size]
            self.frame_data_send = self.frame_data
            self.data = self.data[msg_size:]
            if self._ui.camera_var == 0:
                self.conn.close()
                self.s.close()
                self.connect()
