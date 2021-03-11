import socket
import time
import threading
import utils as u


# Defining values to the connection between TX and RX
HOST = 'localhost'
PORT = 50007
PORTACK = 50006

# Creates UDP sockets to transfer and receive data between TX and RX
sockt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockt2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockt2.bind((HOST, PORTACK))

# Boolean that indicates that the program is still executing
running = True

# Defining constants
transmition_time = 1
MSS = 1
alpha = 0.8
LimitTime = 200

# Constant that stores the time of the beginning of execution
start_time = time.time()

# Variable which will be used to calculate the current time throught the execution
currentTime = time.time()


LastSent = -1
LastAck = -1
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

packagesList = []
pack_num = 0

# Arrays that store the values to be ploted
timePlot = []
srttPlot = []
cwndPlot = []


def ProcessAck():
    global Buffer
    while 1:
        data, addr = sockt2.recvfrom(1024)
        data = data.decode('ascii')
        num = int(data.split('-')[1])

        receivedTime = (time.time() - start_time)
        # t3 = threading.Thread(target=updateValeus(num, receivedTime))
        # t3.start()
        updateValeus(num, receivedTime)
        log = "ACK " + str(num) + " received"
        u.logData(receivedTime, log, effectiveWindow, cwnd, rtt, srtt, TOut)
        Trace("ACK received " + data)


def updateValeus(ack_num, receivedTime):

    global cwnd, cwmax, MSS, packagesList, rtt, srtt, TOut, effectiveWindow, LastAck

    for item in packagesList:
        if item['num'] == ack_num:
            rtt = u.calculateRTT(receivedTime, item['transmition_time'])

    srtt = u.calculateSRTT(alpha, srtt, rtt)

    if(cwnd < cwmax):
        cwnd += MSS
    else:
        cwnd += MSS/cwnd
        cwmax = min(cwmax, cwnd)

    TOut = 2 * srtt
    LastAck = ack_num
    effectiveWindow = u.calculateEffectiveWindow(cwnd, LastSent, LastAck)


def SendRetransBuffer():
    global TOut, effectiveWindow
    while len(RetransBuffer) > 0:
        # Send a packet only if the efective window is larger than 0
        if effectiveWindow < 0:
            log = 'Negative Effective Window Retrans'
            # Trace(log)
            # u.logData((time.time() - start_time), log,
            #           effectiveWindow, cwnd, rtt, srtt, TOut)
        else:
            num = RetransBuffer[0]
            datagram = '0-'+str(num)
            del RetransBuffer[0]
            time.sleep(transmition_time)
            sockt.sendto(datagram.encode(), (HOST, PORT))

            sentAt = (time.time() - start_time)
            packagesList.append({'num': num, 'transmition_time': sentAt})

            # When a package is retransmitted, the timeout doubles
            TOut *= 2
            log = 'Sent Retrans: ' + str(num)
            u.logData((time.time() - start_time), log,
                      effectiveWindow, cwnd, rtt, srtt, TOut)
            Trace('Sent Retrans: ' + datagram)


def TimeOut(num):
    global RetransBuffer, LastAck, cwnd, cwini, cwmax
    time.sleep(TOut)
    if num >= LastAck:
        cwnd = cwini
        cwmax = max(cwini, (cwmax/2))

        RetransBuffer.append(num)
        log = "TimeOut: " + str(num)
        u.logData((time.time() - start_time), log,
                  effectiveWindow, cwnd, rtt, srtt, TOut)
        Trace(log)
        SendRetransBuffer()


def sendPackage():
    global Buffer, LastSent, LastAck, packagesList

    while 1:
        if len(Buffer) > 0:

            # Send a packet only if the efective window is larger than 0
            if effectiveWindow < 0:
                log = 'Negative Effective Window'
                # Trace(log)
                # u.logData((time.time() - start_time), log,
                #           effectiveWindow, cwnd, rtt, srtt, TOut)

            elif (LastSent - LastAck) <= effectiveWindow:
                num = Buffer[0]
                del Buffer[0]
                error = '0'
                errorlog = ''
                if u.isPrime(num):
                    error = '1'
                    errorlog = "Datagram " + str(num) + " lost"
                # Segment:  errorindicator-seqnum
                datagram = error+'-'+str(num)
                time.sleep(transmition_time)
                LastSent = num
                sockt.sendto(datagram.encode(), (HOST, PORT))

                sentAt = (time.time() - start_time)
                packagesList.append({'num': num, 'transmition_time': sentAt})

                log = 'Datagram ' + str(num) + ' sent'
                u.logData(sentAt, log, effectiveWindow, cwnd, rtt, srtt, TOut)
                Trace('Sent: ' + datagram)

                if errorlog != '':
                    u.logData((time.time() - start_time), errorlog,
                              effectiveWindow, cwnd, rtt, srtt, TOut)
                    print(errorlog)

                t2 = threading.Thread(target=TimeOut, args=(
                    num,), name="Thread-pck-"+str(num))
                t2.start()

            else:
                log = ("Exeeds effectiveWindow")
                LastSent, LastAck, effectiveWindow


def SendBuffer():
    global Buffer, pack_num
    while (0 <= len(Buffer) < 20):
        Buffer.append(pack_num)
        pack_num += 1


def Trace(mess):
    global currentTime
    currentTime = time.time()-start_time
    print(currentTime, '|', "'"+mess+"'")


def getPlotData():
    global timePlot, srttPlot, cwndPlot
    while running:
        timePlot.append(time.time()-start_time)
        srttPlot.append(srtt)
        cwndPlot.append(cwnd)
        time.sleep(1)

u.createLogFile()

t1 = threading.Thread(target=ProcessAck)
t1.start()

t2 = threading.Thread(target=sendPackage)
t2.start()

t3 = threading.Thread(target=getPlotData)
t3.start()

start_time = time.time()
while running:
    running = time.time()-start_time < LimitTime
    SendBuffer()

u.plot(timePlot, srttPlot, cwndPlot)