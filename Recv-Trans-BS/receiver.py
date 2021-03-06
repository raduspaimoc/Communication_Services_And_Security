import socket
import time
import threading


# Defining values to the connection between TX and RX
HOST = 'localhost'
PORT = 50007
PORTACK = 50006

# Creates UDP sockets to transfer and receive data between TX and RX
sockt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockt.bind((HOST, PORT))

# Defining constant time (s) to send an ack
time_to_ack = 2

# Constant that stores the time of the beginning of execution
start_time = time.time()

# Stores when the last package was received to fullfill system requirement of:
# Send ACK after 1 s. without a correct reception
lastCorrectlyReceived = time.time()

# Receive Buffer: stores received packages awaiting to be read
Buffer = []

# Marks the next Expected package to keep track of receiving all of them
nextExpected = 0


# Function ran in a separated thread, responsible for receiving ACK segments from the RX
def ReceivePackages():
    global start_time
    while 1:
        data, addr = sockt.recvfrom(1024)
        manageIncoming_thread = threading.Thread(target=manageIncoming(data))
        manageIncoming_thread.start()


# Thread responsible for receiving packages from the Transmitter
def manageIncoming(data):
    global Buffer, nextExpected

    # Receive, decode and handle data
    data = data.decode('ascii')
    error = int(data.split("-")[0])
    num = int(data.split("-")[1])

    # If package does not contain error, is still expected and there is still space in the receiver buffer
    # it is put into the buffer to me handled
    if (error == 0 and num >= nextExpected):

        if(len(Buffer) < 21):
            lastCorrectlyReceived = time.time()
            Buffer.append(num)
            Buffer.sort()
        else:
            print (Buffer)


# Code responsible for managing that ACKs are sent
# after 1 s. without a correct reception, and 
# immediately when 3 or more segments in sequence
def ManageBuffer():
    global Buffer, nextExpected

    while 1:
        # sends ACK of last package in sequence immediately when 3 or more segments in sequence
        if (len(Buffer) >= 3 and Buffer[0] == nextExpected):
            package = Buffer[len(Buffer)-1]
            Buffer = Buffer[len(Buffer):]
            nextExpected = package + 1
            SendAck(nextExpected)

        # sends ACK after 1 s. without a correct reception
        elif (len(Buffer) > 0 and (time.time() - lastCorrectlyReceived) > 2):
            package = Buffer[0]
            if(package == nextExpected):
                Buffer = Buffer[1:]
                nextExpected = package + 1
                SendAck(nextExpected)


# Code responsible for sending acknowledgments to the transmitter
def SendAck(ne):
    time.sleep(time_to_ack)
    datagram = 'ACK-'+str(ne)
    sockt.sendto(datagram.encode(), (HOST, PORTACK))
    print("SENT ACK ", ne)

# Creating and starting thread responsible for receiving incoming packages
ReceivePackages_thread = threading.Thread(target=ReceivePackages)
ReceivePackages_thread.start()

# Initiates main code execution
ManageBuffer()
