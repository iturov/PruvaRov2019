"""
axis list yapıldı
hats button_liste eklendi
05.02.2019
Abdullah Enes
"""

import pygame

def scale(joy_val, max):
    return int(round((joy_val+1)/2.0*max))

class Joy():
    def __init__(self, ui):
        try:
            self.pygame = pygame
            self.pygame.init()
            self.clock = pygame.time.Clock()
            self.pygame.joystick.init()
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.axes = self.joystick.get_numaxes()  # num of axes
            self.buttons = self.joystick.get_numbuttons()  # num of buttons
            self.hats = self.joystick.get_numhats()  # num of hats
            self.clock.tick(20)  # frame per second
            self.connected = True
            self.axis_list = []
            self.pressed_buttons = []
            self.ui = ui

        except:
            self.connected = False

    def joy_get(self):
        while True:
            try:
                self.clock = pygame.time.Clock()
                self.clock.tick(20)  # frame per second
                self.pygame.event.get()  # get joystick event
                self.pressed_buttons = self.which_button()
                self.axis_list = self.get_axes_list()
            except pygame.error:
                return False


    def which_button(self):
        self.pressed_buttons = []
        for i in range(self.buttons):
            if self.joystick.get_button(i) == 1:
                self.pressed_buttons.append(i)
        return self.pressed_buttons

    def get_axes_list(self):
        self.axis_list = []
        for i in range(self.axes - 1):
            axis = scale(self.joystick.get_axis(i), 511)
            self.axis_list.append(axis)

        if 3 in self.which_button():
            self.axis_list.append(125)

        elif 5 in self.which_button():
            if self.ui.Cannon_cb.isChecked():
                self.axis_list.append(511)
            else:
                self.axis_list.append(381)

        else:
            self.axis_list.append(256)
        return self.axis_list

    def get_hats(self):
        return self.joystick.get_hat(0)
