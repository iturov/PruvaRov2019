import datetime
import time
exceptionFile = open("ExceptionLog.txt", "w")

def exceptionLog(msg):
        if msg == "":
                return 0
        else:
                print(time.asctime(time.localtime())+" Exception Log: "+msg+"\n", file=exceptionFile)

def vehicleLog(msg):
        if msg == "":
                return 0
        else:
                print(time.asctime(time.localtime())+" Vehicle Log: "+msg+"\n", file=exceptionFile)
