"""
TCP - IP Communication of vehicle
"""
import os
import socket
import time
from threading import Timer
import queue
from master.log.log import exceptionLog
from master.log.log import vehicleLog
from master.parse.parse import Parse

class GetFuncTypes:
    Temp = 32
    Pressure = 33
    x_speed = 34
    y_speed = 35
    ph = 36

def dec_to_bin(x):
    dec = "0"*(8 - len(bin(x)[2:])) + bin(x)[2:]
    return dec

def parse(packet):
    data1 = packet[2]
    data2 = packet[3]
    data1 = dec_to_bin(data1)
    data2 = dec_to_bin(data2)
    data = data1 + data2
    data = int(data,2)
    return data

#Timer utility for TCP to heartbeat in every 0,07352 sec
class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class Server():

    def __init__(self, ui):
        self.host = "169.254.134.171"
        self.port = 5566
        self.buffer_size = 1024
        self.axis_list = []
        self.ui = ui
        self.timer = time.time()
        self.i = 0

    def ping(self):
        state = os.system("ping -c 1 raspberrypi.local") == 0
        return state

    def bind_Server(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print("try to connect ___________ ServerClass")
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print("try to bind ___________ ServerClass")
            print("bind :    ", self.s.bind((self.host, self.port)))
            self.s.bind((self.host, self.port))
        except socket.error as msg:
            msg = "Bind Server error : " + str(msg)
            exceptionLog(msg)
        print("Socket bind comlete ____________ ServerClass.")

    def setupConnection(self):

        self.s.listen(1)
        print("before accept ______ ServerClass")
        self.ui.comm_text = "Waiting For Connection"
        self.ui.warnings_list.append("Waiting for client acception")
        self._connection = False
        self.conn, self.address = self.s.accept()
        self.conn.settimeout(0.001)
        time.sleep(0.5)
        self.ui.comm_text = "CONNECTED"
        self.ui.PressedKeys = []
        self.timer = time.time()
        print("Connected to: " + self.address[0] + ":" + str(self.address[1]))
        self.ui.vehicleip_text = self.address[0]
        self.ui.warnings_list.append("Connected to: " + str(self.address[0]) + ":" + str(self.address[1]))
        self._connection = True

    def dataTransfer(self, ui):
        if self.axis_list == [] or not self.ui.MotorMount_cb.isChecked():
             self.axis_list = [str.encode(chr(0))]

        for data in self.axis_list:
            try:
                self.conn.send(data)

            except BrokenPipeError as msg:
                ui.warnings_list.append("Broken PipeLine Error in Axis thread")
                print("thread pipe error")
                msg = "Data Transfer BrokenPipe Exception:" + str(msg)
                exceptionLog(msg)
                self.bind_Server()
                self.setupConnection()

            except Exception as msg:
                msg = "Data Transfer Exception: [FATAL]" + str(msg)
                exceptionLog(msg)

    def dataTransfer2(self, button_list):

        if button_list == []:
            return 0
        for data in button_list:
            try:
                print("Sending trying")
                self.conn.send(data)
                print("Sending Completed")

            except BrokenPipeError as msg:
                self.ui.warnings_list.append("Broken PipeLine Error ")
                print("broken pipe error ")
                msg = "Data Transfer2 BrokenPipe Exception:" + str(msg)
                exceptionLog(msg)
                self.bind_Server()
                self.setupConnection()

            except Exception as msg:
                print("data transfer exception : ", msg)
                msg = "Data Transfer2 Exception: [FATAL]" + str(msg)
                exceptionLog(msg)

    def getData(self):
        self._index = 0
        self._packet = []
        self._true_packet = 0
        self._wrongchecksum = 0
        self._wrongpacket = 0

        while True:
            try:
                data = self.conn.recv(self.buffer_size)
            except:
                continue

            for i in data:
                if self._index == 0 and i == 255:
                    self._packet.append(i)
                    self._index += 1

                elif self._index == 1 and i == GetFuncTypes.Pressure:
                    self._packet.append(i)
                    self._index += 1
                    self._pac_index = 0

                elif self._index == 1 and i == GetFuncTypes.Temp:
                    self._packet.append(i)
                    self._index += 1
                    self._pac_index = 1

                elif self._index == 1 and i == GetFuncTypes.x_speed:
                    self._packet.append(i)
                    self._index += 1
                    self._pac_index = 2

                elif self._index == 1 and i == GetFuncTypes.y_speed:
                    self._packet.append(i)
                    self._index += 1
                    self._pac_index = 3

                elif self._index == 1 and i == GetFuncTypes.ph:
                    self._packet.append(i)
                    self._index += 1
                    self._pac_index = 3

                elif self._index == 2:
                    self._packet.append(i)
                    self._index += 1

                elif self._index == 3:
                    self._packet.append(i)
                    self._index += 1

                elif self._index == 4:
                    self._packet.append(i)
                    self._index += 1

                elif self._index == 5:
                    packet_sum = sum(self._packet)
                    if i == 0:
                        self._true_packet += 1
                        self._packet.append(i)
                        data = parse(self._packet)
                        func = self._packet[1]

                        if func == GetFuncTypes.Pressure:
                            self.pressure = data
                            vehicleLog("PRESSURE "+str(data/16))
                            self.ui.pressure_text = str(float(data/16))

                        elif func == GetFuncTypes.Temp:
                            self.temp = data
                            self.ui.temperature_text = str(float(data/16))
                            vehicleLog("TEMPERATURE "+str(data/16))

                        elif func == GetFuncTypes.x_speed:
                            self.x_speed = data
                            #print("X speed : ",self.x_speed/16)
                            vehicleLog("X SPEED "+str(data/16))

                        elif func == GetFuncTypes.ph:
                            self.ph = data
                            #print("X speed : ",self.x_speed/16
                            self.ui.ph_text = str(float(data/16))
                            vehicleLog("ph "+str(data/16))

                        elif func == GetFuncTypes.y_speed:
                            self.y_speed = data
                            #print("Y speed : ",self.y_speed/16)
                            vehicleLog("Y SPEED "+str(data/16))

                        self._index = 0
                        self._packet = []

                    else:
                        self._packet = []
                        self._index = 0
                        self._pac_index = 0
                        self._wrongchecksum += 1

                else:
                    self._packet = []
                    self._wrongpacket += 1
                    self._index = 0
                    self._pac_index = 0
