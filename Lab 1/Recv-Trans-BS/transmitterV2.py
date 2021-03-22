import socket
import time
import threading
import utils as u


HOST = 'localhost'
PORT = 50007
PORTACK = 50008

sockt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockt2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockt2.bind((HOST, PORTACK))

transmition_time = 1.
MSS = 1
alpha = 0.8
LimitTime = 200

LastSent = -1
LastAck = 0
TOut = 10

Buffer = []
RetransBuffer = []

cwmax = 4
cwini = 1
cwnd = cwini
effectiveWindow = cwnd
rtt = 11
srtt = rtt
srtt = u.calculateSRTT(alpha, srtt, rtt)

currentTime = time.time()
start_time = time.time()

packagesList = []


def ProcessAck():
    global Buffer, LastAck
    while 1:
        data, addr = sockt2.recvfrom(1024)
        data = data.decode('ascii')
        num = int(data.split('-')[1])

        if num == (LastAck+1):
            receivedTime = (time.time() - start_time)
            t3 = threading.Thread(target=updateValeus(num, receivedTime))
            t3.start()
            # updateValeus(num, receivedTime)
            log = "ACK " + str(num) + " received"
            u.logData(receivedTime, log, effectiveWindow, cwnd, rtt, srtt, TOut)
            Trace("ACK received " + data)
            LastAck = num

def updateValeus(ack_num, receivedTime):

    global cwnd, cwmax, MSS, packagesList, rtt, srtt

    for item in packagesList:
        if item['num'] == ack_num:
            rtt = u.calculateRTT(receivedTime, item['transmition_time'])

    srtt = u.calculateSRTT(alpha, srtt, rtt)

    if(cwnd < cwmax):
        cwnd += MSS
    else:
        cwnd += MSS/cwnd
        cwmax = min(cwmax, cwnd)


def SendRetransBuffer():
    global TOut
    while len(RetransBuffer) > 0:
        TOut *= 2
        num = RetransBuffer[0]
        datagram = '0-'+str(num)
        del RetransBuffer[0]
        time.sleep(transmition_time)
        sockt.sendto(datagram.encode(), (HOST, PORT))
        log = 'Sent Retrans: ' + str(num)
        u.logData((time.time() - start_time), log, effectiveWindow, cwnd, rtt, srtt, TOut)
        Trace('Sent Retrans: ' + datagram)


def TimeOut(num):
    global RetransBuffer, LastAck, cwnd, cwini, cwmax
    time.sleep(TOut)
    cwnd = cwini
    cwmax = max(cwini, (cwmax/2))
    if num >= LastAck:
        RetransBuffer.append(num)
        log = "TimeOut: " + str(num)
        u.logData((time.time() - start_time), log, effectiveWindow, cwnd, rtt, srtt, TOut)
        Trace(log)
        SendRetransBuffer()


def SendBuffer():
    global Buffer, LastSent, packagesList
    while len(Buffer) > 0:
        num = Buffer[0]
        del Buffer[0]
        error = '0'
        if u.isPrime(num):
            error = '1'
            log = "Datagram " + str(num) + " lost"
            u.logData((time.time() - start_time), log, effectiveWindow, cwnd, rtt, srtt, TOut)
            print(log)
        datagram = error+'-'+str(num)  # Segment:  errorindicator-seqnum
        time.sleep(transmition_time)
        LastSent = num
        sockt.sendto(datagram.encode(), (HOST, PORT))

        sentAt = (time.time() - start_time)
        packagesList.append({'num':num,'transmition_time':sentAt})

        log = 'Datagram ' + str(num) + ' sent'
        u.logData(sentAt, log, effectiveWindow, cwnd, rtt, srtt, TOut)
        Trace('Sent: ' + datagram)
        t2 = threading.Thread(target=TimeOut, args=(num,))
        t2.start()


def Trace(mess):
    global currentTime
    currentTime = time.time()-start_time
    print(currentTime, '|', "'"+mess+"'")

u.createLogFile()

t1 = threading.Thread(target=ProcessAck)
t1.start()

for i in range(30):
    Buffer.append(i)

start_time = time.time()
while time.time()-start_time < LimitTime:
    SendBuffer()
