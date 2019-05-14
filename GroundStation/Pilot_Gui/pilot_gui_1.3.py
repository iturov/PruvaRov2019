from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPainter, QColor, QFont, QPalette, QFontMetricsF, QPen, QPolygon
from PyQt5.QtCore import Qt, QPoint, pyqtProperty, QSize, pyqtSlot
from master.camera.videoGet import VideoGet
import time
import cv2
import pickle

class CameraShowThread(QtCore.QThread):
    changePixmap = QtCore.pyqtSignal(QtGui.QImage)

    def run(self):
        self.record_sec = 0
        self.record_min = 0
        self.frame = []
        # cap = cv2.VideoCapture(0)
        self.start_time = time.time()
        out = cv2.VideoWriter('Saved_video0.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (600,800))
        video_getter = VideoGet(ui)
        video_getter.start()
        while True:
            if video_getter.frame_data_send != "":
                frame_bytes = video_getter.frame_data_send
                ui.th.frame = frame_bytes
            else:
                continue

            if self.frame != []:
                frame = pickle.loads(self.frame, fix_imports=True, encoding="bytes")
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgbImage = cv2.resize(rgbImage, (1800, 890), interpolation=cv2.INTER_LINEAR)
                if ui.record_bool:
                    out.write(self.frame)
                    self.record_sec += time.time() - self.start_time
                    self.start_time = time.time()
                    if self.record_sec > 60:
                        self.record_sec = 0
                        self.record_min += 1
                else:
                    self.start_time = time.time()

                self.frame_qt = QtGui.QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QtGui.QImage.Format_RGB888)
                self.changePixmap.emit(self.frame_qt)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.main_gl = QtWidgets.QGridLayout()
        self.main_gl.setObjectName("main_gl")
        self.controls_gl = QtWidgets.QGridLayout()
        self.controls_gl.setObjectName("controls_gl")
        self.logo_lb = QtWidgets.QLabel(self.centralwidget)
        self.logo_lb.setStyleSheet("border-image: url(:/images/itu_rov_logo.png);")
        self.logo_lb.setText("")
        self.logo_lb.setObjectName("logo_lb")
        self.controls_gl.addWidget(self.logo_lb, 0, 1, 1, 1)
        self.buttons_gb = QtWidgets.QGroupBox(self.centralwidget)
        self.buttons_gb.setStyleSheet("")
        self.buttons_gb.setTitle("")
        self.buttons_gb.setCheckable(False)
        self.buttons_gb.setChecked(False)
        self.buttons_gb.setObjectName("buttons_gb")
        self.record_pb = QtWidgets.QPushButton(self.buttons_gb)
        self.record_pb.setGeometry(QtCore.QRect(210, 20, 75, 75))
        self.record_pb.setStyleSheet("border-image: url(:/images/stop_record.png);\n"
"border-image: url(:/images/start_record.png);")
        self.record_pb.setText("")
        self.record_pb.setObjectName("record_pb")
        self.takephoto_pb = QtWidgets.QPushButton(self.buttons_gb)
        self.takephoto_pb.setGeometry(QtCore.QRect(20, 20, 75, 75))
        self.takephoto_pb.setStyleSheet("border-image: url(:/images/takepic_b.png);\n"
"border-image: url(:/images/takepic_w.png);\n"
"\n"
"")
        self.takephoto_pb.setText("")
        self.takephoto_pb.setObjectName("takephoto_pb")
        self.startimgprocess_pb = QtWidgets.QPushButton(self.buttons_gb)
        self.startimgprocess_pb.setGeometry(QtCore.QRect(590, 40, 131, 41))
        self.startimgprocess_pb.setObjectName("startimgprocess_pb")
        self.linedetector_pb = QtWidgets.QPushButton(self.buttons_gb)
        self.linedetector_pb.setGeometry(QtCore.QRect(440, 40, 121, 41))
        self.linedetector_pb.setStyleSheet("")
        self.linedetector_pb.setObjectName("linedetector_pb")
        self.cannonphoto_pb = QtWidgets.QPushButton(self.buttons_gb)
        self.cannonphoto_pb.setGeometry(QtCore.QRect(110, 20, 81, 81))
        self.cannonphoto_pb.setStyleSheet("\n"
"\n"
"border-image: url(:/images/cannon.png);")
        self.cannonphoto_pb.setText("")
        self.cannonphoto_pb.setObjectName("cannonphoto_pb")
        self.recordtime_lb = QtWidgets.QLabel(self.buttons_gb)
        self.recordtime_lb.setGeometry(QtCore.QRect(310, 30, 101, 61))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(22)
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.recordtime_lb.setFont(font)
        self.recordtime_lb.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.recordtime_lb.setStyleSheet("border: 2px solid;\n"
"border-color: rgb(85, 0, 127);\n"
"")
        self.recordtime_lb.setAlignment(QtCore.Qt.AlignCenter)
        self.recordtime_lb.setObjectName("recordtime_lb")
        self.camera_gb = QtWidgets.QGroupBox(self.buttons_gb)
        self.camera_gb.setEnabled(True)
        self.camera_gb.setGeometry(QtCore.QRect(1450, 10, 331, 91))
        self.camera_gb.setCheckable(True)
        self.camera_gb.setChecked(False)
        self.camera_gb.setObjectName("camera_gb")
        self.gridLayout = QtWidgets.QGridLayout(self.camera_gb)
        self.gridLayout.setObjectName("gridLayout")
        self.frontcam_pb = QtWidgets.QPushButton(self.camera_gb)
        self.frontcam_pb.setObjectName("frontcam_pb")
        self.gridLayout.addWidget(self.frontcam_pb, 0, 0, 1, 1)
        self.bottomcam_pb = QtWidgets.QPushButton(self.camera_gb)
        self.bottomcam_pb.setObjectName("bottomcam_pb")
        self.gridLayout.addWidget(self.bottomcam_pb, 0, 1, 1, 1)
        self.closecam_pb = QtWidgets.QPushButton(self.camera_gb)
        self.closecam_pb.setObjectName("closecam_pb")
        self.gridLayout.addWidget(self.closecam_pb, 0, 2, 1, 1)
        self.cameratype_lb = QtWidgets.QLabel(self.camera_gb)
        self.cameratype_lb.setObjectName("cameratype_lb")
        self.gridLayout.addWidget(self.cameratype_lb, 1, 0, 1, 1)
        self.st_cameratype_lb = QtWidgets.QLabel(self.camera_gb)
        self.st_cameratype_lb.setText("")
        self.st_cameratype_lb.setObjectName("st_cameratype_lb")
        self.gridLayout.addWidget(self.st_cameratype_lb, 1, 1, 1, 2)
        self.warnings_lb = QtWidgets.QLabel(self.buttons_gb)
        self.warnings_lb.setGeometry(QtCore.QRect(694, 10, 701, 81))
        self.warnings_lb.setText("")
        self.warnings_lb.setObjectName("warnings_lb")
        self.takephoto_pb.raise_()
        self.startimgprocess_pb.raise_()
        self.linedetector_pb.raise_()
        self.cannonphoto_pb.raise_()
        self.recordtime_lb.raise_()
        self.record_pb.raise_()
        self.camera_gb.raise_()
        self.warnings_lb.raise_()
        self.controls_gl.addWidget(self.buttons_gb, 0, 0, 1, 1)
        self.controls_gl.setColumnStretch(0, 95)
        self.controls_gl.setColumnStretch(1, 5)
        self.main_gl.addLayout(self.controls_gl, 1, 0, 1, 1)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.camera_lb = QtWidgets.QLabel(self.frame)
        self.camera_lb.setGeometry(QtCore.QRect(2, 2, 1891, 951))
        self.camera_lb.setText("")
        self.camera_lb.setObjectName("camera_lb")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.frame)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(1619, 10, 261, 251))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        compass = CompassWidget()
        self.verticalLayout.addWidget(compass)
        self.main_gl.addWidget(self.frame, 0, 0, 1, 1)
        self.main_gl.setRowStretch(0, 90)
        self.main_gl.setRowStretch(1, 10)
        self.gridLayout_2.addLayout(self.main_gl, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.camera_lb.setAlignment(QtCore.Qt.AlignTop)
        self.warnings_lb.setAlignment(QtCore.Qt.AlignHCenter)
        self.takephoto_pb.clicked.connect(self.takepic)
        self.record_pb.clicked.connect(self.record)
        self.cannonphoto_pb.clicked.connect(self.cannonpic)
        self.closecam_pb.clicked.connect(self.closecam_pb_event)
        self.bottomcam_pb.clicked.connect(self.bottomcam_pb_event)
        self.frontcam_pb.clicked.connect(self.frontcam_pb_event)

        self.record_bool = False
        self.takepic_bool = False
        self.record_bool1 = True
        self.i = 0
        self.img_ctr = 0
        self.camera_var = 0
        self.st_cameratype_lb_text = "Close"
        self.message = ""
        self.warnings_list = []

        self.th = CameraShowThread(MainWindow)
        self.th.changePixmap.connect(self.setImage)
        self.th.start()

        self.timer = QtCore.QTimer() 
        self.timer.timeout.connect(lambda: self.timer_func()) 
        self.timer.start(200)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate(       "MainWindow", "ITU ROV PILOT GUI"))
        self.startimgprocess_pb.setText(_translate( "MainWindow", "Start Image Process"))
        self.linedetector_pb.setText(_translate(    "MainWindow", "Line Detector"))
        self.recordtime_lb.setText(_translate(      "MainWindow", "0:21"))
        self.camera_gb.setTitle(_translate(         "MainWindow", "Camera"))
        self.frontcam_pb.setText(_translate(        "MainWindow", "Front Camera"))
        self.bottomcam_pb.setText(_translate(       "MainWindow", "Bottom Camera"))
        self.closecam_pb.setText(_translate(        "MainWindow", "Close Camera"))
        self.cameratype_lb.setText(_translate(      "MainWindow", "Camera:"))

    def timer_func(self):
        for i in self.warnings_list:
            self.message = "\n       " + str(i) + self.message
        if len(self.message) > 7000:
            self.message = self.message[0:7000]
        self.warnings_lb.setText(self.message)
        self.warnings_list = []
        self.st_cameratype_lb.setText(self.st_cameratype_lb_text)
        if self.record_bool and self.record_bool1:
                    self.recordtime_lb.setStyleSheet("border: 2px solid;\n"
"border-color: rgb(85, 0, 127);\n"
"")
                    self.record_bool1=False
        elif self.record_bool and not self.record_bool1:
                    self.recordtime_lb.setStyleSheet(
"border-color: rgb(85, 0, 127);\n"
"")
                    self.record_bool1=True
        self.warnings_list = []
        self.recordtime_lb.setText("{}:{}".format(str(self.th.record_min), str(int(self.th.record_sec))))


    def setImage(self, image):
        self.camera_lb.setPixmap(QtGui.QPixmap.fromImage(image))

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


    def record(self):
        if not self.record_bool:
            self.record_pb.setStyleSheet("border-image: url(:/images/stop_record.png);")
            self.record_bool = True
        else:
            self.record_pb.setStyleSheet("border-image: url(:/images/start_record.png);")
            self.record_bool = False

    def cannonpic(self):
        try:
            QtGui.QImage.save(self.th.frame_qt, "cannon.jpg")
        except:
            print("Photo can not taken")

    def takepic(self):
        now = time.localtime()
        self.img_ctr += 1
        try:
            QtGui.QImage.save(self.th.frame_qt, "media/IMG("+time.asctime(now)+"-"+str(self.img_ctr)+").jpg")
        except Exception as msg:
            print("Camera frame error!" + str(msg))

        if not self.takepic_bool:
            self.takephoto_pb.setStyleSheet("border-image: url(:/images/takepic_b.png);\n")
            self.takepic_bool = True
        else:
            self.takephoto_pb.setStyleSheet("border-image: url(:/images/takepic_w.png);\n")
            self.takepic_bool = False

class CompassWidget(QtWidgets.QWidget):
    angleChanged = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self._angle = 0.0
        self.my_angle = 0
        self._margins = 10
        self._pointText = {0: "N", 45: "NE", 90: "E", 135: "SE", 180: "S",
                           225: "SW", 270: "W", 315: "NW"}
        self.timer = QtCore.QTimer()  # timer çağırılır
        self.timer.timeout.connect(lambda: self.timer_func())
        self.timer.start(100)
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        self.drawMarkings(painter)
        self.drawNeedle(painter)
        painter.end()

    def drawMarkings(self, painter):

        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        scale = min((self.width() - self._margins) / 120.0,
                    (self.height() - self._margins) / 120.0)
        painter.scale(scale, scale)
        font = QFont(self.font())
        font.setPixelSize(10)
        metrics = QFontMetricsF(font)
        painter.setFont(font)
        painter.setPen(self.palette().color(QPalette.Shadow))
        painter.setPen(QColor(0,0,0))
        i = 0
        while i < 360:
            if i % 45 == 0:
                painter.drawLine(0, -40, 0, -50)
                painter.drawText(-metrics.width(self._pointText[i]) / 2.0, -52,
                                 self._pointText[i])
            else:
                painter.drawLine(0, -45, 0, -50)
            painter.rotate(15)
            i += 15

        painter.restore()

    def drawNeedle(self, painter):
        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self._angle)
        scale = min((self.width() - self._margins) / 120.0,
                    (self.height() - self._margins) / 120.0)
        painter.scale(scale, scale)
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(self.palette().brush(QPalette.Shadow))
        painter.drawPolygon(
            QPolygon([QPoint(-10, 0), QPoint(0, -45), QPoint(10, 0),
                      QPoint(0, 45), QPoint(-10, 0)])
        )

        painter.setBrush(self.palette().brush(QPalette.Highlight))
        painter.drawPolygon(
            QPolygon([QPoint(-5, -25), QPoint(0, -45), QPoint(5, -25),
                      QPoint(0, -30), QPoint(-5, -25)])
        )
        painter.restore()

    def sizeHint(self):
        return QSize(500, 500)

    def angle(self):
        return self._angle

    @pyqtSlot(int)
    def setAngle(self, angle):
        if angle != self._angle:
            self._angle = angle
            self.angleChanged.emit(angle)
            self.update()

    def timer_func(self):
        self.my_angle += 3
        self.setAngle(self.my_angle)

    angle = pyqtProperty(float, angle, setAngle)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

