from threading import Thread
import socket
import struct
import time

class VideoGet():
    def __init__(self, ui):
        self._HOST = '169.254.11.41'
        self._PORT = 8485
        self.frame_data_send = ""
        self._ui = ui

    def connect(self):
        while True:
            if self._ui.camera_var == 0:
                time.sleep(1)
                continue

            elif self._ui.camera_var == 1:
                self._PORT = 8480

            elif self._ui.camera_var == 2:
                self._PORT = 8485

            self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._s.settimeout(1)
            print('Socket created Video_Getter')

            try:
                self._s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self._s.bind((self._HOST, self._PORT))
                print('Socket bind complete Video_Getter')
                self._s.listen(10)
                print('Socket now listening Video_Getter')
                self.conn, self.addr = self._s.accept()
                print(self.addr)
                self._ui.warnings_list.append("Connection is Completed ip : {} in video getter thread".format(self.addr[0]))
                break


            except socket.error as msg:
                self.msg = "Try to Connect"
                time.sleep(1)

                continue

        self.connected = True
        print("after acception in video getter")
        img_counter = 0
        self.data = b""
        self.payload_size = struct.calcsize(">L")
        print("payload_size: {}".format(self.payload_size))


    def start(self):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        self.connect()

        i = 0
        start = time.time()
        while True:
            i += 1
            if time.time() - start > 1:
                start = time.time()
                print("i for Get Thread :", i)
                i = 0


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

            if self._ui.camera_var == 0:
                self._ui.warnings_list.append("Camera is closed")
                self.conn.close()
                self._s.close()
                self.connect()
