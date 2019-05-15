import socket
import time
import os
import serial

# Serial interface must be enabled through raspi-config
# Used pins: 6: GND, 8:TXD, 10:RXD
# os.system("sudo chmod 777 /dev/ttyS0")
# ser = serial.Serial('/dev/ttyACM0')

def parse(datas):
	if datas is None or datas == []:
		print("datas is None!!")
		return False
	data_list = []
	for data in datas:
		for i in data:
			data_list.append(ord(i))
	return data_list

class Tcp():
	def __init__(self):
		self.host = "169.254.11.41"
		self.port = 5566
		self.buffer_size = 1024
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.start = time.time()

	def ping(self):
		state = os.system('ping {} {} > /dev/null'.format("-c 1", self.host)) == 0
		print(state)
		return state

	def connect(self):
		while True:
			# Wait function
			if time.time() - self.start > 0.5:  
				try:
					self.s.connect((self.host, self.port))
					print("client connected")
					break
				except :
					self.start = time.time()
					print("connection refused")
					pass

	def getData(self):
		try:
			data = self.s.recv(self.buffer_size)
			print("len",len(data))
			data1 = parse(data.decode('utf-8'))
			return data1 #.decode('utf-8')

		except Exception as msg:
			print("Get data exception ", msg)
			data = b'21'
			return data

	def sendData(self, incoming):
		try:
			self.s.send(incoming)
		except Exception as msg:
			print("Send data exception", msg)
			pass

os.system("sudo chmod 777 /dev/ttyS0")
serialPort = serial.Serial("/dev/ttyS0", 115200)

tcp = Tcp()
while True:
	if tcp.ping():
		print("ping is completed")

	else:
		print("Ethernet unplugged")

tcp.connect()
now = time.time()

while True:
	# Data coming from groundstation
	data = tcp.getData()  
	try:
		# ITUROV RPI to ST
		# Serial port reads data as "bytes" data type
		for i in data:
			serialPort.write([i])
		# EACH PACKET COMING FROM GROUNDSTATION. TYPE = LIST. 
		# EXAMPLE = [255, 12, 111, 0, 3, 150]
	except Exception as msg:
		print("serial write exception ", msg)
		pass

	if not data == []:
		now = time.time()
	if data == []:
		if time.time() - now > 2:
			tcp = Tcp()
			tcp.connect()

	# ITUROV ST UART Communication
	try:
		# Polling serial port for data
		if(serialPort.in_waiting > 0):
			# Incoming is the list holding read data
			incoming = serialPort.read(serialPort.in_waiting)
		else:
			continue
	except serial.SerialTimeoutException:
		print("Serial Time Out Exception occured")
		continue
	
	except serial.SerialException:
		print("Serial Exception occured")
		continue

	except EOFError:
		print("EOF error")
		continue

	except Exception as msg:
		print("An unexpected error occured", msg)
		continue

	# Send to GroundStation
	tcp.sendData(incoming)
