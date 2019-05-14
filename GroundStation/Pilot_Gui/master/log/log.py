import time
exceptionFile = open("ExceptionLog.txt", "w")
vehicleFile = open("VehicleLog.txt", "w")

def exceptionLog(msg):
        print(time.asctime(time.localtime())+" - "+msg+"\n", file=exceptionFile)

def vehicleLog(msg):
        print(time.asctime(time.localtime())+" - "+msg+"\n", file=vehicleFile)