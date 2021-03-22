import socket
import time
import threading
from collections import deque


HOST = 'localhost'
PORT = 50007
PORTACK = 50006

sockt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockt.bind((HOST, PORT))

time_to_ack = 2

Buffer = []
BufferList = []
nextExpected = 0
lastCorrectlyReceived = time.time()
lastInsertedInBuffer = -1

start_time = time.time()
last_received_time = 0


def ReceivePackages():
    global last_received_time, start_time
    while 1:
        data, addr = sockt.recvfrom(1024)
        last_received_time = start_time - time.time()
        t3 = threading.Thread(target=manageIncomming(data))
        t3.start()


def manageIncomming(data):
    global Buffer, BufferList, nextExpected, lastInsertedInBuffer

    data = data.decode('ascii')
    error = int(data.split("-")[0])
    num = int(data.split("-")[1])

    if (error == 0 and num >= nextExpected):

        if(len(Buffer) < 21):
            lastCorrectlyReceived = time.time()
            Buffer.append(num)
            Buffer.sort()
            lastInsertedInBuffer = num
        else:
            print (Buffer)


def ManageBuffer():
    global Buffer, last_received_time, nextExpected

    while 1:
        if (len(Buffer) >= 3 and Buffer[0] == nextExpected):
            package = Buffer[len(Buffer)-1]
            Buffer = Buffer[len(Buffer):]
            nextExpected = package + 1
            SendAck(nextExpected)

        elif (len(Buffer) > 0 and (time.time() - lastCorrectlyReceived) > 2):
            package = Buffer[0]
            if(package == nextExpected):
                Buffer = Buffer[1:]
                nextExpected = package + 1
                SendAck(nextExpected)
                    


def SendAck(ne):
    time.sleep(time_to_ack)
    datagram = 'ACK-'+str(ne)
    sockt.sendto(datagram.encode(), (HOST, PORTACK))
    print("SENT ACK ", ne)


t1 = threading.Thread(target=ReceivePackages)
t1.start()

# ReceivePackages()

# t2 = threading.Thread(target=ManageBuffer())
# t2.start()

ManageBuffer()
