"""
Packet Classes and Functions
"""

import time
from master.joystick.joystick import Joy

def parse(datas):
    for data in datas:
        print("lenght of data : ", len(data))
        data = data.decode("utf-8")
        for i in data:
            print(ord(i), end=" ")
        print("")

def packing(ss,func,data1,data2,flag):
    send_packet = chr(ss) + chr(func) + chr(data1) + chr(data2) + chr(flag) + chr((ss+func+data1+data2+flag) % 256)
    send_packet = str.encode(send_packet)

    return send_packet

    # ASCII representations of functions
class Func_types():
    forward = 3   #  forward : 0 backward: 512
    throttle = 6  # 0 - 512
    up = 12       # 0 - 512
    yaw = 24      # 0 - 512
    gripper = 48    # on = 111 off = 222
    flagger = 96    # blue1 = 111 blue2 = 222 red1 = 333 red2 = 444 main = 0
    camera_1 = 192  # up = 111 down = 222
    void = 36      # void_fish= 111 void_rock = 222 void_main = 0
    led = 66       # on or off = 111
    microRov = 5   # go=111 come = 222 left = 444 right = 333
    AutoMode = 10  # on = 111 off = 222
    Cannon = 80    # open = 111
    ph = 40  # get_pH = 111

    # On JOYSTICK
class button_types():
    gripper_on = 6
    gripper_off = 7
    camera1_up = 8
    camera1_down = 9
    led = 0
    hat_up    = (0, 1)
    hat_down  = (0, -1)
    hat_left  = (-1, 0)
    hat_right = (1, 0)

    # On KEYBOARD
class key_types():
    Flagger_red1    = ord("G")
    Flagger_red2    = ord("H")
    Flagger_blue1   = ord("J")
    Flagger_blue2   = ord("K")
    Flagger_main    = ord("L")

    Send_MicroRov    = ord("O")
    Receive_MicroRov = ord("I")
    Right_MicroRov   = ord("P")
    Left_MicroRov    = ord("U")

    Auto_ModeOn   = ord("A")
    Auto_ModeOff  = ord("S")

    Void_fish     = ord("T")
    Void_rock     = ord("R")
    Void_main     = ord("E")

    Cannon_Open = ord("Q")

    pH = ord("Z")


class Packet():
    def __init__(self):
        self.start_time = time.time()*1000
        self.bytearr = bytearray()
        self.flag = 0
        self.start_seq = 255
        # individual init
        self.led_status = False

    def axis_packet(self, func_list, axis_list):
        self.flag += 1
        self.flag = self.flag % 4
        send_packet_list = []

        for i in range(len(axis_list)):
            if axis_list[i] > 255:
                data1 = 255
                data2 = axis_list[i] % 256

            else:
                data1 = axis_list[i]
                data2 = 0

            send_packet = packing(ss=self.start_seq, func=func_list[i], data1=data1, data2=data2, flag=self.flag)
            send_packet_list.append(send_packet)
        return send_packet_list

    def key_status(self,key):
        pressed = False
        data = 0
        func = 0

        if key == key_types.Send_MicroRov:
            pressed = True
            func = Func_types.microRov
            data = 111

        elif key == key_types.Receive_MicroRov:
            pressed = True
            func = Func_types.microRov
            data = 222

        elif key == key_types.Right_MicroRov:
            pressed = True
            func = Func_types.microRov
            data = 333

        elif key == key_types.Left_MicroRov:
            pressed = True
            func = Func_types.microRov
            data = 444

            ################

        elif key == key_types.Auto_ModeOn:
            pressed = True
            func = Func_types.AutoMode
            data = 111

        elif key == key_types.Auto_ModeOff:
            pressed = True
            func = Func_types.AutoMode
            data = 222

            ################

        elif key == key_types.Flagger_blue1:
            pressed =True
            func = Func_types.flagger
            data = 111

        elif key == key_types.Flagger_blue2:
            pressed =True
            func = Func_types.flagger
            data = 222

        elif key == key_types.Flagger_red1:
            pressed =True
            func = Func_types.flagger
            data = 333

        elif key == key_types.Flagger_red2:
            pressed =True
            func = Func_types.flagger
            data = 444

        elif key == key_types.Flagger_main:
            pressed = True
            func = Func_types.flagger
            data = 0

            ################

        elif key == key_types.Void_main:
            pressed = True
            func = Func_types.void
            data = 0

        elif key == key_types.Void_fish:
            pressed = True
            func = Func_types.void
            data = 111

        elif key == key_types.Void_rock:
            pressed = True
            func = Func_types.void
            data = 222

            ################

        elif key == key_types.pH:
            pressed = True
            func = Func_types.ph
            data = 111

        elif key == key_types.Cannon_Open:
            pressed = True
            func = Func_types.Cannon
            data = 111

        if pressed:
            if data > 255:
                data1 = 255
                data2 = data % 255
            else:
                data1 = data
                data2 = 0

            send_packet = packing(self.start_seq, func, data1, data2, self.flag)

            return [send_packet]
        else:
            return []

    def joy_status(self, list_button):
        func_list = []
        send_packet_list = []
        for button in list_button:
            if button == button_types.gripper_on:
                func_list.append((Func_types.gripper, 111))

            elif button == button_types.gripper_off and (not button_types.gripper_on in list_button):
                func_list.append((Func_types.gripper, 222))

            if button == button_types.camera1_up:
                func_list.append((Func_types.camera_1, 111))

            elif button == button_types.camera1_down and (not button_types.camera1_up in list_button):
                func_list.append((Func_types.camera_1, 222))

        if not self.led_status and (button_types.led in list_button):
            func_list.append((Func_types.led, 111))
            self.led_status = True

        elif self.led_status and not button_types.led in list_button:
            self.led_status = False

        if func_list != []:
            for func, data in func_list:
                send_packet = packing(self.start_seq, func, data, 0, self.flag)
                send_packet_list.append(send_packet)
            return send_packet_list
        else:
            return []
