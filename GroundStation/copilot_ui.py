"""
ITU ROV CO-PILOT GUI
"""


import os
from PyQt5 import QtCore, QtGui, QtWidgets
from master.packet.packet import key_types
from functools import partial
from master.camera.videoGet import VideoGet
import cv2
from threading import Thread
import pickle
import time
import math
from threading import Thread
from master.packet.packet import Packet
from master.packet.packet import Func_types
from master.parse.parse import Parse
from master.joystick.joystick import Joy
from master.tcp.tcp import Server
from master.tcp.tcp import RepeatTimer
from master.camera.videoGet import VideoGet
from master.log.log import exceptionLog
from master.log.log import vehicleLog
import time
import pickle


class MainThread(QtCore.QThread):

    def run(self):

        # Joystick
        joy = Joy(ui)
        if joy.connected:
            ui.joystick_text = "CONNECTED"

        else:
            ui.joystick_text = "NOT CONNECTED"
            joy = Joy()
            pass

        # TCP
        s = Server(ui)

        while True:
            if s.ping():
                break
            else:
                print("Ethernet is Unplugged")
                ui.comm_text = "Ethernet is Unplugged"
                ui.warnings_list.append("Ethernet is Unplugged")

        s.bind_Server()
        s.setupConnection()
        ui.PressedKeys = []

        # Thread
        axis_timer = RepeatTimer(0.07, s.dataTransfer, args=(ui,))
        axis_timer.start()

        # Joy Thread
        joy_timer = Thread(target=joy.joy_get)
        joy_timer.start()

        # Get Data Thread
        data_getter = Thread(target=s.getData)
        data_getter.start()

        # Packet
        packet = Packet()
        func = Func_types()
        joy_axis_list = []
        joy_button = []
        key = 0

        while True:

            # Status Check Start ----------------------------------------------
            if ui.PressedKeys != []:
                key = ui.PressedKeys.pop(0)

            elif ui.PressedKeys == []:
                key = 0

            # JOYSTICK START -------------------------------------------------
            if joy.connected:
                joy_axis_list = joy.axis_list

                if joy.pressed_buttons != []:
                    joy_button = [joy.pressed_buttons.pop(0)]
                else:
                    joy_button = []
            else:
                pass
            # JOYSTICK END --------------------------------------------------

            # PACKET START --------------------------------------------------
            arr = packet.axis_packet([func.throttle, func.forward, func.yaw, func.up], joy_axis_list)
            buttonArr = packet.joy_status(joy_button)
            keyArr = packet.key_status(key)
            # PACKET END ----------------------------------------------------

            # SENDING START -------------------------------------------------
            s.axis_list = arr
            s.dataTransfer2(buttonArr)
            s.dataTransfer2(keyArr)
            # SENDING END ----------------------------------------------------





class CameraShow_Thread(QtCore.QThread):
    changePixmap = QtCore.pyqtSignal(QtGui.QImage)

    def run(self):

        video_getter = VideoGet(ui)
        video_getter.start()
        i = 0
        start = time.time()
        self.frame = []
        img_ctr = 0
        while True:
            i += 1

            if time.time() - start > 1:
                start = time.time()
                i = 0

            # CAMERA START ---------------------------------------------------
            if video_getter.frame_data_send != "":
                frame_bytes = video_getter.frame_data_send
                self.frame = frame_bytes
            else:
                ui.camera_lb.setText("Camera is Waiting")
                time.sleep(1)
                continue

            if self.frame != []:
                frame = pickle.loads(self.frame, fix_imports=True, encoding="bytes")
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgbImage = cv2.resize(rgbImage,(640,480),interpolation=cv2.INTER_LINEAR)
                convertToQtFormat = QtGui.QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QtGui.QImage.Format_RGB888)
                if ui.takephoto_bool:
                    now = time.localtime()
                    QtGui.QImage.save(convertToQtFormat, "IMG("+time.asctime(now)+"-"+str(img_ctr)+").jpg")
                    img_ctr += 1
                    ui.takephoto_bool = False
                    ui.warnings_list.append("!! Foto is taken !!")
                self.changePixmap.emit(convertToQtFormat)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.NonModal)
        MainWindow.resize(1258, 1097)
        palette = QtGui.QPalette()
        MainWindow.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(11)
        MainWindow.setFont(font)

        self.central_vl = QtWidgets.QWidget(MainWindow)
        self.central_vl.setObjectName("central_vl")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.central_vl)
        self.verticalLayout.setObjectName("verticalLayout")
        self.main_gl = QtWidgets.QGridLayout()
        self.main_gl.setObjectName("main_gl")
        self.rightside_gl = QtWidgets.QGridLayout()
        self.rightside_gl.setObjectName("rightside_gl")
        self.status_gl = QtWidgets.QGridLayout()
        self.status_gl.setObjectName("status_gl")
        self.l3 = QtWidgets.QFrame(self.central_vl)
        self.l3.setFrameShape(QtWidgets.QFrame.HLine)
        self.l3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.l3.setObjectName("l3")
        self.status_gl.addWidget(self.l3, 1, 0, 1, 1)
        self.st_joystick_lb = QtWidgets.QLabel(self.central_vl)
        self.st_joystick_lb.setObjectName("st_joystick_lb")
        self.status_gl.addWidget(self.st_joystick_lb, 2, 2, 1, 1)
        self.comm_lb = QtWidgets.QLabel(self.central_vl)
        self.comm_lb.setObjectName("comm_lb")
        self.status_gl.addWidget(self.comm_lb, 0, 0, 1, 1)
        self.joystick_lb = QtWidgets.QLabel(self.central_vl)
        self.joystick_lb.setObjectName("joystick_lb")
        self.status_gl.addWidget(self.joystick_lb, 2, 0, 1, 1)
        self.camera_lb = QtWidgets.QLabel(self.central_vl)
        self.camera_lb.setObjectName("camera_lb")
        self.status_gl.addWidget(self.camera_lb, 4, 0, 1, 1)
        self.camera_lb.setText("Camera:")
        self.st_camera_lb = QtWidgets.QLabel(self.central_vl)
        self.st_camera_lb.setObjectName("st_comm_lb")
        self.status_gl.addWidget(self.st_camera_lb, 4, 2, 1, 1)
        self.st_camera_lb.setText("-")
        self.st_comm_lb = QtWidgets.QLabel(self.central_vl)
        self.st_comm_lb.setObjectName("st_comm_lb")
        self.status_gl.addWidget(self.st_comm_lb, 0, 2, 1, 1)
        self.l2 = QtWidgets.QFrame(self.central_vl)
        self.l2.setFrameShape(QtWidgets.QFrame.HLine)
        self.l2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.l2.setObjectName("l2")
        self.status_gl.addWidget(self.l2, 1, 2, 1, 1)
        self.l1 = QtWidgets.QFrame(self.central_vl)
        self.l1.setFrameShape(QtWidgets.QFrame.VLine)
        self.l1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.l1.setObjectName("l1")
        self.status_gl.addWidget(self.l1, 0, 1, 1, 1)
        self.l4 = QtWidgets.QFrame(self.central_vl)
        self.l4.setFrameShape(QtWidgets.QFrame.VLine)
        self.l4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.l4.setObjectName("l4")
        self.status_gl.addWidget(self.l4, 2, 1, 2, 1)
        self.l5 = QtWidgets.QFrame(self.central_vl)
        self.l5.setFrameShape(QtWidgets.QFrame.VLine)
        self.l5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.l5.setObjectName("l4")
        self.status_gl.addWidget(self.l5, 4, 1, 2, 1)
        self.l6 = QtWidgets.QFrame(self.central_vl)
        self.l6.setFrameShape(QtWidgets.QFrame.HLine)
        self.l6.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.l6.setObjectName("l2")
        self.status_gl.addWidget(self.l6, 3, 2, 1, 1)
        self.l7 = QtWidgets.QFrame(self.central_vl)
        self.l7.setFrameShape(QtWidgets.QFrame.HLine)
        self.l7.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.l7.setObjectName("l2")
        self.status_gl.addWidget(self.l7, 3, 0, 1, 1)
        self.rightside_gl.addLayout(self.status_gl, 1, 0, 1, 1)
        self.tabWidget = QtWidgets.QTabWidget(self.central_vl)
        self.tabWidget.setObjectName("tabWidget")
        self.MainControls_tab = QtWidgets.QWidget()
        self.MainControls_tab.setObjectName("MainControls_tab")
        self.gridLayout = QtWidgets.QGridLayout(self.MainControls_tab)
        self.gridLayout.setObjectName("gridLayout")
        self.data_gb = QtWidgets.QGroupBox(self.MainControls_tab)
        self.data_gb.setObjectName("data_gb")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.data_gb)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.st_temperature_lb = QtWidgets.QLabel(self.data_gb)
        self.st_temperature_lb.setObjectName("st_temperature_lb")
        self.gridLayout_2.addWidget(self.st_temperature_lb, 0, 1, 1, 1)
        self.st_pH_lb = QtWidgets.QLabel(self.data_gb)
        self.st_pH_lb.setObjectName("st_pH_lb")
        self.gridLayout_2.addWidget(self.st_pH_lb, 1, 1, 1, 1)
        self.temperature_lb = QtWidgets.QLabel(self.data_gb)
        self.temperature_lb.setObjectName("temperature_lb")
        self.gridLayout_2.addWidget(self.temperature_lb, 0, 0, 1, 1)
        self.pH_lb = QtWidgets.QLabel(self.data_gb)
        self.pH_lb.setObjectName("pH_lb")
        self.gridLayout_2.addWidget(self.pH_lb, 1, 0, 1, 1)
        self.st_pressure_lb = QtWidgets.QLabel(self.data_gb)
        self.st_pressure_lb.setObjectName("st_pressure_lb")
        self.gridLayout_2.addWidget(self.st_pressure_lb, 2, 1, 1, 1)
        self.pressure_lb = QtWidgets.QLabel(self.data_gb)
        self.pressure_lb.setObjectName("pressure_lb")
        self.gridLayout_2.addWidget(self.pressure_lb, 2, 0, 1, 1)
        self.vehicleip_lb = QtWidgets.QLabel(self.data_gb)
        self.vehicleip_lb.setObjectName("vehicleip_lb")
        self.gridLayout_2.addWidget(self.vehicleip_lb, 3, 0, 1, 1)
        self.st_vehicleip_lb = QtWidgets.QLabel(self.data_gb)
        self.st_vehicleip_lb.setObjectName("st_vehicleip_lb")
        self.gridLayout_2.addWidget(self.st_vehicleip_lb, 3, 1, 1, 1)
        self.gridLayout.addWidget(self.data_gb, 3, 0, 1, 1)
        self.cannon_gb = QtWidgets.QGroupBox(self.MainControls_tab)
        self.cannon_gb.setObjectName("cannon_gb")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.cannon_gb)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.AF_rb = QtWidgets.QRadioButton(self.cannon_gb)
        self.AF_rb.setObjectName("AF_rb")
        self.gridLayout_3.addWidget(self.AF_rb, 1, 2, 1, 1)
        self.LargeRadius_lb = QtWidgets.QLabel(self.cannon_gb)
        self.LargeRadius_lb.setObjectName("LargeRadius_lb")
        self.gridLayout_3.addWidget(self.LargeRadius_lb, 4, 0, 1, 1)
        self.SmallLength_lb = QtWidgets.QLabel(self.cannon_gb)
        self.SmallLength_lb.setObjectName("SmallLength_lb")
        self.gridLayout_3.addWidget(self.SmallLength_lb, 1, 0, 1, 1)
        self.SmallRadius_lb = QtWidgets.QLabel(self.cannon_gb)
        self.SmallRadius_lb.setObjectName("SmallRadius_lb")
        self.gridLayout_3.addWidget(self.SmallRadius_lb, 3, 0, 1, 1)
        self.LargeLength_lb = QtWidgets.QLabel(self.cannon_gb)
        self.LargeLength_lb.setObjectName("LargeLength_lb")
        self.gridLayout_3.addWidget(self.LargeLength_lb, 2, 0, 1, 1)
        self.BottomRadius_lb = QtWidgets.QLabel(self.cannon_gb)
        self.BottomRadius_lb.setObjectName("BottomRadius_lb")
        self.gridLayout_3.addWidget(self.BottomRadius_lb, 5, 0, 1, 1)
        self.BottomRadius_lb.setText("Bottom Radius:")
        self.BFIC_rb = QtWidgets.QRadioButton(self.cannon_gb)
        self.BFIC_rb.setObjectName("BFIC_rb")
        self.gridLayout_3.addWidget(self.BFIC_rb, 2, 2, 1, 1)
        self.FPF_rb = QtWidgets.QRadioButton(self.cannon_gb)
        self.FPF_rb.setObjectName("FPF_rb")
        self.gridLayout_3.addWidget(self.FPF_rb, 3, 2, 1, 1)
        self.TFJRA_rb = QtWidgets.QRadioButton(self.cannon_gb)
        self.TFJRA_rb.setObjectName("TFJRA_rb")
        self.gridLayout_3.addWidget(self.TFJRA_rb, 4, 2, 1, 1)
        self.st_wofc_lb = QtWidgets.QLabel(self.cannon_gb)
        self.st_wofc_lb.setObjectName("st_wofc_lb")
        self.gridLayout_3.addWidget(self.st_wofc_lb, 6, 1, 1, 2)
        self.wofc_lb = QtWidgets.QLabel(self.cannon_gb)
        self.wofc_lb.setObjectName("wofc_lb")
        self.gridLayout_3.addWidget(self.wofc_lb, 6, 0, 1, 1)
        self.SmallLength_le = QtWidgets.QLineEdit(self.cannon_gb)
        self.SmallLength_le.setText("")
        self.SmallLength_le.setObjectName("SmallLength_le")
        self.gridLayout_3.addWidget(self.SmallLength_le, 1, 1, 1, 1)
        self.LargeLength_le = QtWidgets.QLineEdit(self.cannon_gb)
        self.LargeLength_le.setObjectName("LargeLength_le")
        self.gridLayout_3.addWidget(self.LargeLength_le, 2, 1, 1, 1)
        self.SmallRadius_le = QtWidgets.QLineEdit(self.cannon_gb)
        self.SmallRadius_le.setObjectName("SmallRadius_le")
        self.gridLayout_3.addWidget(self.SmallRadius_le, 3, 1, 1, 1)
        self.LargeRadius_le = QtWidgets.QLineEdit(self.cannon_gb)
        self.LargeRadius_le.setObjectName("LargeRadius_le")
        self.gridLayout_3.addWidget(self.LargeRadius_le, 4, 1, 1, 1)
        self.BottomRadius_le = QtWidgets.QLineEdit(self.cannon_gb)
        self.BottomRadius_le.setObjectName("BottomRadius_le")
        self.gridLayout_3.addWidget(self.BottomRadius_le, 5, 1, 1, 1)
        self.gridLayout_3.setColumnStretch(0, 30)
        self.gridLayout_3.setColumnStretch(1, 30)
        self.gridLayout_3.setColumnStretch(2, 30)
        self.gridLayout.addWidget(self.cannon_gb, 2, 0, 1, 1)
        self.cam2_key_hl = QtWidgets.QHBoxLayout()
        self.cam2_key_hl.setObjectName("cam2_key_hl")
        self.KeyboardM_gb = QtWidgets.QGroupBox(self.MainControls_tab)
        self.KeyboardM_gb.setObjectName("KeyboardM_gb")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.KeyboardM_gb)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.Flag_cb = QtWidgets.QCheckBox(self.KeyboardM_gb)
        self.Flag_cb.setTristate(False)
        self.Flag_cb.setObjectName("Flag_cb")
        self.gridLayout_4.addWidget(self.Flag_cb, 0, 0, 1, 1)
        self.Cannon_cb = QtWidgets.QCheckBox(self.KeyboardM_gb)
        self.Cannon_cb.setTristate(False)
        self.Cannon_cb.setObjectName("Cannon_cb")
        self.gridLayout_4.addWidget(self.Cannon_cb, 0, 1, 1, 1)
        self.MotorMount_cb = QtWidgets.QCheckBox(self.KeyboardM_gb)
        self.MotorMount_cb.setTristate(False)
        self.MotorMount_cb.setObjectName("Cannon_cb")
        self.gridLayout_4.addWidget(self.MotorMount_cb, 5, 1, 1, 1)
        self.MotorMount_cb.setText("Motor Mount")
        self.Void_cb = QtWidgets.QCheckBox(self.KeyboardM_gb)
        self.Void_cb.setTristate(False)
        self.Void_cb.setObjectName("Void_cb")
        self.gridLayout_4.addWidget(self.Void_cb, 2, 0, 1, 1)
        self.Autonomous_cb = QtWidgets.QCheckBox(self.KeyboardM_gb)
        self.Autonomous_cb.setTristate(False)
        self.Autonomous_cb.setObjectName("Autonomous_cb")
        self.gridLayout_4.addWidget(self.Autonomous_cb, 4, 0, 1, 1)
        self.Gripper_cb = QtWidgets.QCheckBox(self.KeyboardM_gb)
        self.Gripper_cb.setObjectName("Gripper_cb")
        self.gridLayout_4.addWidget(self.Gripper_cb, 4, 1, 1, 1)
        self.CamS1_cb = QtWidgets.QCheckBox(self.KeyboardM_gb)
        self.CamS1_cb.setObjectName("CamS1_cb")
        self.gridLayout_4.addWidget(self.CamS1_cb, 2, 1, 1, 1)
        self.MicroROV_cb = QtWidgets.QCheckBox(self.KeyboardM_gb)
        self.MicroROV_cb.setTristate(False)
        self.MicroROV_cb.setObjectName("MicroROV_cb")
        self.gridLayout_4.addWidget(self.MicroROV_cb, 5, 0, 1, 1)
        self.cam2_key_hl.addWidget(self.KeyboardM_gb)
        self.gridLayout.addLayout(self.cam2_key_hl, 0, 0, 1, 1)
        self.cam2_gb = QtWidgets.QGroupBox(self.MainControls_tab)
        self.cam2_gb.setEnabled(True)
        self.cam2_gb.setCheckable(True)
        self.cam2_gb.setChecked(False)
        self.cam2_gb.setObjectName("cam2_gb")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.cam2_gb)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.frontcam_pb = QtWidgets.QPushButton(self.cam2_gb)
        self.frontcam_pb.setEnabled(True)
        self.frontcam_pb.setObjectName("frontcam_pb")
        self.gridLayout_6.addWidget(self.frontcam_pb, 3, 0, 1, 1)
        self.bottomcam_pb = QtWidgets.QPushButton(self.cam2_gb)
        self.bottomcam_pb.setEnabled(True)
        self.bottomcam_pb.setObjectName("bottomcam_pb")
        self.gridLayout_6.addWidget(self.bottomcam_pb, 3, 1, 1, 1)
        self.record_pb = QtWidgets.QPushButton(self.cam2_gb)
        self.record_pb.setEnabled(True)
        self.record_pb.setObjectName("record_pb")
        self.gridLayout_6.addWidget(self.record_pb, 0, 0, 1, 1)
        self.closecam_pb = QtWidgets.QPushButton(self.cam2_gb)
        self.closecam_pb.setEnabled(True)
        self.closecam_pb.setObjectName("closecam_pb")
        self.gridLayout_6.addWidget(self.closecam_pb, 4, 0, 1, 2)
        self.cannondims_pb = QtWidgets.QPushButton(self.cam2_gb)
        self.cannondims_pb.setEnabled(True)
        self.cannondims_pb.setObjectName("cannondims_pb")
        self.gridLayout_6.addWidget(self.cannondims_pb, 1, 1, 1, 1)
        self.takephoto_pb = QtWidgets.QPushButton(self.cam2_gb)
        self.takephoto_pb.setEnabled(True)
        self.takephoto_pb.setObjectName("takephoto_pb")
        self.gridLayout_6.addWidget(self.takephoto_pb, 1, 0, 1, 1)
        self.recordtime_lb = QtWidgets.QLabel(self.cam2_gb)
        self.recordtime_lb.setStyleSheet("border: 2px solid;\n"
"border-color: rgb(26, 10, 255);")
        self.recordtime_lb.setAlignment(QtCore.Qt.AlignCenter)
        self.recordtime_lb.setObjectName("recordtime_lb")
        self.gridLayout_6.addWidget(self.recordtime_lb, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.cam2_gb, 1, 0, 1, 1)
        self.tabWidget.addTab(self.MainControls_tab, "")
        self.Info_tab = QtWidgets.QWidget()
        self.Info_tab.setObjectName("Info_tab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.Info_tab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.logo_lb = QtWidgets.QLabel(self.Info_tab)
        self.logo_lb.setStyleSheet("image: url(:/prefix/ROV LOGO SİYAH DİKEY.png);")
        self.logo_lb.setText("")
        self.logo_lb.setObjectName("logo_lb")
        self.verticalLayout_2.addWidget(self.logo_lb)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_2.addItem(spacerItem)
        self.info_lb = QtWidgets.QLabel(self.Info_tab)
        self.info_lb.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.info_lb.setObjectName("info_lb")
        self.verticalLayout_2.addWidget(self.info_lb)
        self.clock_LCD = QtWidgets.QLCDNumber(self.Info_tab)
        self.clock_LCD.setSizeIncrement(QtCore.QSize(0, -15005))
        self.clock_LCD.setDigitCount(4)
        self.clock_LCD.setMode(QtWidgets.QLCDNumber.Dec)
        self.clock_LCD.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.clock_LCD.setProperty("value", 1700.0)
        self.clock_LCD.setProperty("intValue", 1700)
        self.clock_LCD.setObjectName("clock_LCD")
        self.verticalLayout_2.addWidget(self.clock_LCD)
        self.date_lb = QtWidgets.QLabel(self.Info_tab)
        font = QtGui.QFont()
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.date_lb.setFont(font)
        self.date_lb.setFocusPolicy(QtCore.Qt.NoFocus)
        self.date_lb.setAlignment(QtCore.Qt.AlignCenter)
        self.date_lb.setObjectName("date_lb")
        self.verticalLayout_2.addWidget(self.date_lb)
        self.verticalLayout_2.setStretch(0, 90)
        self.verticalLayout_2.setStretch(1, 100)
        self.verticalLayout_2.setStretch(2, 50)
        self.verticalLayout_2.setStretch(3, 50)
        self.verticalLayout_2.setStretch(4, 20)
        self.tabWidget.addTab(self.Info_tab, "")
        self.rightside_gl.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.main_gl.addLayout(self.rightside_gl, 0, 2, 1, 1)
        self.main_l = QtWidgets.QFrame(self.central_vl)
        self.main_l.setFrameShape(QtWidgets.QFrame.VLine)
        self.main_l.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.main_l.setObjectName("main_l")
        self.main_gl.addWidget(self.main_l, 0, 3, 1, 1)
        self.leftside_vl = QtWidgets.QVBoxLayout()
        self.leftside_vl.setObjectName("leftside_vl")
        self.camera_lb = QtWidgets.QLabel(self.central_vl)
        self.camera_lb.setStyleSheet("border-image: url(:/prefix/arayuz-bg.png);")
        self.camera_lb.setText("")
        self.camera_lb.setObjectName("camera_lb")
        self.leftside_vl.addWidget(self.camera_lb)
        self.warnings_static_lb = QtWidgets.QLabel(self.central_vl)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Symbol")
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(True)
        font.setWeight(9)
        self.warnings_static_lb.setFont(font)
        self.warnings_static_lb.setStyleSheet("font: 75 18pt \"MS Shell Dlg 2\";\n"
"text-decoration: underline;\n"
"font: 75 14pt \"Segoe UI Symbol\";\n"
"text-decoration: underline;")

        self.warnings_static_lb.setObjectName("warnings_static_lb")
        self.leftside_vl.addWidget(self.warnings_static_lb)
        self.warnings_lb = QtWidgets.QLabel(self.central_vl)
        self.warnings_lb.setStyleSheet("\n"
"font: 75 10pt \"Sitka Text\";\n"
"")

        self.warnings_lb.setText("")
        self.warnings_lb.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.warnings_lb.setObjectName("warnings_lb")
        self.scroll_area = QtWidgets.QScrollArea()

        self.warnings_lb.setText("\n "*100 +" "*180)
        self.scroll_area.setWidget(self.warnings_lb)
        self.leftside_vl.addWidget(self.scroll_area)
        self.leftside_vl.setStretch(0, 800)
        self.leftside_vl.setStretch(2, 200)
        self.main_gl.addLayout(self.leftside_vl, 0, 1, 1, 1)
        self.main_gl.setColumnStretch(1, 1500)
        self.main_gl.setColumnStretch(2, 420)
        self.verticalLayout.addLayout(self.main_gl)
        MainWindow.setCentralWidget(self.central_vl)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # --------------------------------------------------------
        # New Lines Start
        # --------------------------------------------------------

        self.message = ""
        self.camera_var = 0
        self.takephoto_bool = True

        self.camera_lb.setAlignment(QtCore.Qt.AlignCenter)
        self.closecam_pb.clicked.connect(self.closecam_pb_event)
        self.bottomcam_pb.clicked.connect(self.bottomcam_pb_event)
        self.frontcam_pb.clicked.connect(self.frontcam_pb_event)
        self.cannondims_pb.clicked.connect(self.cannondims_pb_event)
        self.record_pb.clicked.connect(self.record_pb_event)
        self.takephoto_pb.clicked.connect(self.takephoto_pb_event)
        self.AF_rb.clicked.connect(self.AF_rb_event)
        self.BFIC_rb.clicked.connect(self.BFIC_rb_event)
        self.FPF_rb.clicked.connect(self.FPF_rb_event)
        self.TFJRA_rb.clicked.connect(self.TFJRA_rb_event)
        finish = QtWidgets.QAction("Quit")
        finish.triggered.connect(self.closeEvent)

        self.mainThread = MainThread(MainWindow)
        self.mainThread.start()

        self.th = CameraShow_Thread(MainWindow)
        self.th.changePixmap.connect(self.setImage)
        self.th.start()

        self.comm_text = "Waiting For Connection"
        self.gripper_text = "Waiting For Connection"
        self.joystick_text = "Waiting For Connection"
        self.microrov_text = "Waiting For Connection"
        self.wofc_text = "-"
        self.ph_text = "-"
        self.pressure_text = "-"
        self.temperature_text = "-"
        self.clock_text = "-"
        self.date_text = "-"
        self.warnings_list = []
        self.vehicleip_text = "-"

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: self.timer_func())
        self.timer.start(100)
        MainWindow.keyPressEvent = self.newOnkeyPressEvent
        self.PressedKeys = []

        # ------------------------------------------------------------------------------------
        # NEW LINES END
        # ------------------------------------------------------------------------------------

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "ITU ROV CONTROLLER"))
        self.st_joystick_lb.setText(_translate("MainWindow", "not connected"))
        self.comm_lb.setText(_translate("MainWindow", "Communication:"))
        self.joystick_lb.setText(_translate("MainWindow", "Joystick:"))
        self.camera_lb.setText(_translate("MainWindow", "Camera:"))
        self.st_comm_lb.setText(_translate("MainWindow", "not connected"))
        self.data_gb.setTitle(_translate("MainWindow", "Data"))
        self.st_temperature_lb.setText(_translate("MainWindow", "-"))
        self.st_pH_lb.setText(_translate("MainWindow", "-"))
        self.temperature_lb.setText(_translate("MainWindow", "Temperature:"))
        self.pH_lb.setText(_translate("MainWindow", "pH:"))
        self.st_pressure_lb.setText(_translate("MainWindow", "-"))
        self.pressure_lb.setText(_translate("MainWindow", "Pressure:"))
        self.vehicleip_lb.setText(_translate("MainWindow", "Vehicle IP:"))
        self.st_vehicleip_lb.setText(_translate("MainWindow", "-"))
        self.cannon_gb.setTitle(_translate("MainWindow", "Cannon"))
        self.AF_rb.setText(_translate("MainWindow", "AF"))
        self.LargeRadius_lb.setText(_translate("MainWindow", "Len. of Large Radius:"))
        self.SmallLength_lb.setText(_translate("MainWindow", "Small Length:"))
        self.SmallRadius_lb.setText(_translate("MainWindow", "Len. of Small radius:"))
        self.LargeLength_lb.setText(_translate("MainWindow", "Large Length"))
        self.BFIC_rb.setText(_translate("MainWindow", "BF-IC"))
        self.FPF_rb.setText(_translate("MainWindow", "FPF"))
        self.TFJRA_rb.setText(_translate("MainWindow", "TF-JRA"))
        self.st_wofc_lb.setText(_translate("MainWindow", "-"))
        self.wofc_lb.setText(_translate("MainWindow", "Weight of cannon:"))
        self.KeyboardM_gb.setTitle(_translate("MainWindow", "Keyboard Missions"))
        self.Flag_cb.setText(_translate("MainWindow", "Flag"))
        self.Cannon_cb.setText(_translate("MainWindow", "Cannon"))
        self.Void_cb.setText(_translate("MainWindow", "Void"))
        self.Autonomous_cb.setText(_translate("MainWindow", "Autonomous"))
        self.Gripper_cb.setText(_translate("MainWindow", "Gripper"))
        self.CamS1_cb.setText(_translate("MainWindow", "Cam Servo"))
        self.MicroROV_cb.setText(_translate("MainWindow", "MicroROV"))
        self.cam2_gb.setTitle(_translate("MainWindow", "Camera "))
        self.frontcam_pb.setText(_translate("MainWindow", "Front Camera"))
        self.bottomcam_pb.setText(_translate("MainWindow", "Bottom Camera"))
        self.record_pb.setText(_translate("MainWindow", "Start/Stop Record"))
        self.closecam_pb.setText(_translate("MainWindow", "close cam"))
        self.cannondims_pb.setText(_translate("MainWindow", "Cannon Dims"))
        self.takephoto_pb.setText(_translate("MainWindow", "Take Photo"))
        self.recordtime_lb.setText(_translate("MainWindow", "0:00"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.MainControls_tab), _translate("MainWindow", "Main Controls"))
        self.info_lb.setText(_translate("MainWindow", "Designed by\n"
"Abdullah Enes Bedir\n"
"İhsan Soydemir\n"
"Recep Salih Yazar"))
        self.info_lb.setAlignment(QtCore.Qt.AlignCenter)
        self.info_lb.setStyleSheet("font: 75 18pt \"MS Shell Dlg 2\";\n"
"text-decoration: underline;\n"
"font: 75 14pt \"Segoe UI Symbol\";\n"
"text-decoration: underline;")
        self.date_lb.setText(_translate("MainWindow", "March 28th, 2019"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Info_tab), _translate("MainWindow", "Info"))
        self.warnings_static_lb.setText(_translate("MainWindow", "         WARNINGS"))

    def timer_func(self):

        for i in self.warnings_list:
            self.message = "\n       " + str(i) + self.message
        if len(self.message) > 7000:
            self.message = self.message[0:7000]
        self.warnings_lb.setText(self.message)
        self.warnings_list = []

        self.st_comm_lb.setText(str(self.comm_text))
        self.st_joystick_lb.setText(str(self.joystick_text))
        self.st_wofc_lb.setText(str(self.wofc_text))
        self.st_pH_lb.setText(str(self.ph_text))
        self.st_pressure_lb.setText(str(self.pressure_text))
        self.st_temperature_lb.setText(str(self.temperature_text))
        self.date_lb.setText(str(self.date_text))
        self.st_vehicleip_lb.setText(str(self.vehicleip_text))

    def newOnkeyPressEvent(self, e):

        key = e.key()
        if self.comm_text == "CONNECTED":
            if self.Flag_cb.isChecked() and (key == key_types.Flagger_red1 or key == key_types.Flagger_red2 or key == key_types.Flagger_blue1 or key == key_types.Flagger_blue2 or key== key_types.Flagger_main) :
                self.PressedKeys.append(key)

            elif self.Void_cb.isChecked() and (key == key_types.Void_rock or key == key_types.Void_fish or key == key_types.Void_main):
                self.PressedKeys.append(key)

            elif self.MicroROV_cb.isChecked() and (key == key_types.Receive_MicroRov or key == key_types.Send_MicroRov or key == key_types.Left_MicroRov or key == key_types.Right_MicroRov):
                self.PressedKeys.append(key)

            elif self.Cannon_cb.isChecked() and (key == key_types.Cannon_Open):
                self.PressedKeys.append(key)

            elif self.Autonomous_cb.isChecked() and (key == key_types.Auto_ModeOn or key == key_types.Auto_ModeOff):
                self.PressedKeys.append(key)

            elif key == key_types.pH:
                self.PressedKeys.append(key)
            else:
                self.warnings_list.append("Checkbox is unchecked or Pressed key is UNDEFINED")
        else:
            self.warnings_list.append("Pressed key is not valid because of disconnection")

    def setImage(self, image):
        self.camera_lb.setPixmap(QtGui.QPixmap.fromImage(image))

    #----- 2 MART CMT , BUTTON EVENTS start------------#
    def closecam_pb_event(self):
        self.camera_var = 0

    def frontcam_pb_event(self):
        if self.camera_var == 0:
            self.camera_var = 1
        elif self.camera_var == 1:
            self.camera_var = 1
            self.warnings_list.append("Front Camera already try to open")
        elif self.camera_var == 2:
            self.warnings_list.append("Close Bottom Camera first")

    def bottomcam_pb_event(self):
        if self.camera_var == 0:
            self.camera_var = 2
        elif self.camera_var == 2:
            self.camera_var = 2
            self.warnings_list.append("Bottom Camera already try to open")
        elif self.camera_var == 1:
            self.warnings_list.append("Close Front Camera first")

    def cannondims_pb_event(self):
        pass

    def record_pb_event(self):
        pass

    def takephoto_pb_event(self):
        self.takephoto_bool = True
        pass

    def AF_rb_event(self):
        try:
            volume_other_rad = math.pi*(float(self.SmallRadius_le.text())+float(self.LargeRadius_le.text()))*(float(self.LargeRadius_le.text())-float(self.SmallRadius_le.text()))*float(self.SmallLength_le.text())
            volume_bottom_rad = math.pi*float(self.BottomRadius_le.text())**2*float(self.LargeLength_le.text())

        except Exception as msg:
            self.warnings_list.append("Write Float value at Line Edit")
            return 0

        volume_total = volume_bottom_rad+volume_other_rad
        volume_total = volume_total*(10)**(-6)
        mass = volume_total * 8.03
        self.wofc_text = str(round(mass,2))

    def BFIC_rb_event(self):
        try:
            volume_other_rad = math.pi*(float(self.SmallRadius_le.text())+float(self.LargeRadius_le.text()))*(float(self.LargeRadius_le.text())-float(self.SmallRadius_le.text()))*float(self.SmallLength_le.text())
            volume_bottom_rad = math.pi*float(self.BottomRadius_le.text())**2*float(self.LargeLength_le.text())

        except Exception as msg:
            self.warnings_list.append("Write Float value at Line Edit(virgul yerine nokta kullanın.")
            return 0

        volume_total = volume_bottom_rad+volume_other_rad
        volume_total = volume_total*(10)**(-6)
        mass = volume_total * 7.87
        self.wofc_text = str(round(mass, 4))

    def FPF_rb_event(self):
        try:
            volume_other_rad = math.pi*(float(self.SmallRadius_le.text())+float(self.LargeRadius_le.text()))*(float(self.LargeRadius_le.text())-float(self.SmallRadius_le.text()))*float(self.SmallLength_le.text())
            volume_bottom_rad = math.pi*float(self.BottomRadius_le.text())**2*float(self.LargeLength_le.text())


        except Exception as msg:
            self.warnings_list.append("Write Float value at Line Edit")
            return 0

        volume_total = volume_bottom_rad+volume_other_rad
        volume_total = volume_total*(10)**(-6)
        mass = volume_total * 7.87
        self.wofc_text = str(round(mass, 4))

    def TFJRA_rb_event(self):
        try:
            volume_other_rad = math.pi*(float(self.SmallRadius_le.text())+float(self.LargeRadius_le.text()))*(float(self.LargeRadius_le.text())-float(self.SmallRadius_le.text()))*float(self.SmallLength_le.text())
            volume_bottom_rad = math.pi*float(self.BottomRadius_le.text())**2*float(self.LargeLength_le.text())

        except Exception as msg:
            self.warnings_list.append("Write Float value at Line Edit")
            return 0

        volume_total = volume_bottom_rad+volume_other_rad
        volume_total = volume_total*(10)**(-6)
        mass = volume_total * 7.87
        self.wofc_text = str(round(mass,4))

    # --------------------------------------------------
    # NEW LINE END
    # --------------------------------------------------

import bg_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
