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

# Variable which will be used to calculate the current time throughout the execution
currentTime = time.time()

# Variables that store the, respectively, the last datagram sent and the last acknowledged one
LastSent = -1
LastAck = -1

# Transmition Buffer: stores written packages awaiting to be sent
Buffer = []

# Retransmition Buffer: stores packages lost that will be resend
RetransBuffer = []

# List of all Retransmitted packages used for Karn/Partridge algorithm
allRetrans = []

# Various variables used throughout the code
cwmax = 4
cwini = 1
cwnd = cwini
effectiveWindow = cwnd
rtt = 11
srtt = rtt
srtt = u.calculateSRTT(alpha, srtt, rtt)
TOut = 10

# List that stores packages sent as well as the time they were sent
packagesList = []

# Variable used to enumerate sequentially the packages
pack_num = 0

# Arrays that store the values to be ploted
timePlot = []
srttPlot = []
cwndPlot = []


# Function ran in a separated thread, responsible for receiving ACK segments from the Receiver
def ProcessAck():
    global Buffer

    # Keep the thread running while the program is running
    while running:

        # Receive, decode and handle data, as well as marking its arrival time
        data, addr = sockt2.recvfrom(1024)
        data = data.decode('ascii')
        num = int(data.split('-')[1])
        receivedTime = (time.time() - start_time)

        # Calls function to update TCP values
        updateValues(num, receivedTime)

        # Log both in log file as well as terminal
        log = "ACK " + str(num) + " received"
        u.logData(receivedTime, log, effectiveWindow, cwnd, rtt, srtt, TOut)
        Trace("ACK received " + data)


# Update various TCP metrics, using the received data and performing some calculations
def updateValues(ack_num, receivedTime):

    global cwnd, cwmax, MSS, packagesList, rtt, srtt, TOut, effectiveWindow, LastAck
    
    # checks if its not a retransmition (Karn/Partridge algorithm)
    if ack_num not in allRetrans:
        # finds the respective package and updates Round Trip Time based on its sending and arrival times    
        for item in packagesList:        
            if item['num'] == ack_num:
                rtt = u.calculateRTT(receivedTime, item['transmition_time'])

        # Updates Estimated Round Trip Time
        srtt = u.calculateSRTT(alpha, srtt, rtt)

    # Updates Congestion Window
    if(cwnd < cwmax):
        cwnd += MSS
    else:
        cwnd += MSS/cwnd
        cwmax = min(cwmax, cwnd)

    # Updates Time Out
    TOut = 2 * srtt

    # Updates last acknowledged package
    LastAck = ack_num

    # Updates Effective Window
    effectiveWindow = u.calculateEffectiveWindow(cwnd, LastSent, LastAck)


# Send packages marked for retransmition
def SendRetransBuffer():
    global TOut, effectiveWindow

    # Run while there are packages to be retransmitted
    while len(RetransBuffer) > 0:

        # Send a packet only if the effective window is larger than 0
        if effectiveWindow > 0:

            # Selects package to be retransmitted, create its datagram, remove it from the
            # Retransmition Buffer awaits the appropriate transmition time, resends the package
            # and finally add it to the sent packages list
            if RetransBuffer:
                num = RetransBuffer[0]
                datagram = '0-'+str(num)
                del RetransBuffer[0]
                time.sleep(transmition_time)
                sockt.sendto(datagram.encode(), (HOST, PORT))

                sentAt = (time.time() - start_time)
                packagesList.append({'num': num, 'transmition_time': sentAt})

                # Loggin
                log = 'Sent Retrans: ' + str(num)
                u.logData((time.time() - start_time), log,
                        effectiveWindow, cwnd, rtt, srtt, TOut)
                Trace('Sent Retrans: ' + datagram)

# Thread created for each sent package. Creates a timeout based in the sent time
# and takes appropriated action in case of package not being acknowledged
def TimeOut(num):

    global RetransBuffer, LastAck, cwnd, cwini, cwmax

    # Awaiting Timeout time
    time.sleep(TOut)

    # If timmer is over and ack has not yet been received:
    # - updates congestion window values 
    # - mark package to retransmition
    # - call appropriated function to deal with it
    if num >= LastAck:
        cwnd = cwini
        cwmax = max(cwini, (cwmax/2))

        RetransBuffer.append(num)
        allRetrans.append(num)
        log = "TimeOut: " + str(num)
        u.logData((time.time() - start_time), log,
                  effectiveWindow, cwnd, rtt, srtt, TOut)
        Trace(log)
        SendRetransBuffer()

# Thread responsible for sending packages to the receiver
def sendPackage():
    global Buffer, LastSent, LastAck, packagesList

    while running:
        if len(Buffer) > 0:

            # Send a packet only if the effective window is larger than 0
            # and if Effective Window allows it
            if effectiveWindow > 0 and (LastSent - LastAck) <= effectiveWindow:
                num = Buffer[0]
                del Buffer[0]
                error = '0'
                errorlog = ''

                # Packages with Prime Sequence Number are lost, therefore marked with an Error Indicator (1)
                if u.isPrime(num):
                    error = '1'
                    errorlog = "Datagram " + str(num) + " lost"
                
                # Segment:  "errorindicator-sequencenumber"
                datagram = error+'-'+str(num)

                # Awaits transmition time
                time.sleep(transmition_time)

                # Updates last sent variable, send package, records its sending time and updates packagesList
                LastSent = num
                sockt.sendto(datagram.encode(), (HOST, PORT))

                sentAt = (time.time() - start_time)
                packagesList.append({'num': num, 'transmition_time': sentAt})

                # Logging, also in case of package lost
                log = 'Datagram ' + str(num) + ' sent'
                u.logData(sentAt, log, effectiveWindow, cwnd, rtt, srtt, TOut)
                Trace('Sent: ' + datagram)

                if errorlog != '':
                    u.logData((time.time() - start_time), errorlog,
                              effectiveWindow, cwnd, rtt, srtt, TOut)
                    print(errorlog)

                # Creates thread responsible for taking care of possible timeout
                TimeOut_thread = threading.Thread(target=TimeOut, args=(
                    num,), name="Thread-pck-"+str(num))
                TimeOut_thread.start()


# Thread responsible to handle the Buffer containing the data that will be converted into packages to be sent
def SendBuffer():
    global Buffer, pack_num
    while (0 <= len(Buffer) < 20):
        Buffer.append(pack_num)
        pack_num += 1


# Responsible for logging data in the terminal
def Trace(mess):
    global currentTime
    currentTime = time.time()-start_time
    print(currentTime, '|', "'"+mess+"'")


# Thread that every second acquires data that will be used in the graph plot
def getPlotData():
    global timePlot, srttPlot, cwndPlot
    while running:
        timePlot.append(time.time()-start_time)
        srttPlot.append(srtt)
        cwndPlot.append(cwnd)
        time.sleep(1)


# Creating File that will contains the table from your output code
u.createLogFile()

# Creating and starting various threads that will execute the program
ProcessAck_thread = threading.Thread(target=ProcessAck)
ProcessAck_thread.start()

sendPackage_thread = threading.Thread(target=sendPackage)
sendPackage_thread.start()

getPlotData_thread = threading.Thread(target=getPlotData)
getPlotData_thread.start()

# Annotating program start time
start_time = time.time()

# Main execution, when time limit is reached execution of this loop ends
while running:

    # Running changes to false in case the time limit is reached
    running = time.time()-start_time < LimitTime
    SendBuffer()

# Plots of cwnd and sRTT as a function of time
u.plot(timePlot, srttPlot, cwndPlot)
u.plot_cwnd(timePlot, cwndPlot)
u.plot_sRTT(timePlot, srttPlot)

