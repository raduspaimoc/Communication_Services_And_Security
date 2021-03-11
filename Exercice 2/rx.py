#!/usr/bin/python
import socket
import time
import threading

MAX_BUFFER = 21
ACK_TIMEOUT = 2
SEGMENTS_SEQUENCE = 3
RECEIVER_BUFFER_SIZE = 10

# TX and RX connection values
HOST = 'localhost'
PORT = 50007
PORT_ACK = 50008

# Stores received packages awaiting to be read
buffer = []

# Controls the next expected packet value
next_expected = 0

# UDP socket to transfer and receive data between TX and RX
sockt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockt.bind((HOST, PORT))


def pack_checker():
    global  buffer

    next_pack = buffer[0]
    sequence = 0
    for seg in buffer:
        if seg == next_pack:
            next_pack += 1
            sequence += 1

    if sequence >= SEGMENTS_SEQUENCE:
        send_package()
        buffer = buffer[sequence:]
    return next_pack


def manage_buffer_process(num):
    global buffer, next_expected

    # Responsible of:
    # 1. Send ACK after 2 s. without a correct reception
    # 2. Send ACK immediately when 3 or more segments in sequence

    if not buffer:
        first_num = next_expected
    else:
        first_num = min(buffer[0], next_expected)

    if first_num <= num < first_num + RECEIVER_BUFFER_SIZE and num not in buffer:
        buffer.append(num)
        buffer.sort()

        if next_expected >= buffer[0]:
            return pack_checker()


    #while 1:
    #    if len(buffer) > 0 and (time.time() - last_correct_recv) > ACK_TIMEOUT:
    #        package = buffer[0]
    #        if package == next_expected:
    #            buffer = buffer[1:]
    #            next_expected = package + 1
    #            send_package(next_expected)
    #    elif len(buffer) >= 3 and buffer[0] == next_expected:
    #        package = buffer[len(buffer) - 1]
    #        buffer = buffer[len(buffer):]
    #        next_expected = package + 1
    #        send_package(next_expected)


def send_package(pack_num):
    # Code responsible of sending ACKs to TX
    datagram = 'ACK-'+str(pack_num)
    sockt.sendto(datagram.encode(), (HOST, PORT_ACK))
    print_message("Sent ACK - ", )


 #def recv_ack():
    # Thread responsible of receiving and processing ACKs from tx
#    global start_time
#    print("ACK thread started.")
#    while 1:
#        data, addr = sockt.recvfrom(1024)
#        manageIncoming_thread = threading.Thread(target=ack_process(data))
#        manageIncoming_thread.start()


def print_message(info_message):
    # Shows info data on the terminal
    global start_time
    current_time = time.time() - start_time
    print(str(round(current_time, 2)), '| ' + info_message)


#def ack_process(data):
    #  Thread responsible for receiving packages from TX
#    global buffer, next_expected, last_correct_recv

    # Receive, decode and handle data
#    data = data.decode('ascii')
#    error = int(data.split("-")[0])
#    num = int(data.split("-")[1])

#    if error == 0 and num >= next_expected:

#        if len(buffer) < MAX_BUFFER:
#            last_correct_recv = time.time()

#            buffer.append(num)
#            buffer.sort()
#        else:
#            print_message("Buffer filled. Not enoguh space to add packet.")
#            print("Current buffer: ", buffer)


def check_ack_timeout(next_expected_timeout):
    global next_expected

    time.sleep(ACK_TIMEOUT)

    if next_expected_timeout == next_expected:
        # Send ACK after 2s. without a correct reception
        check_timeout_thread = threading.Thread(target=check_ack_timeout)
        check_timeout_thread.start()

        send_package(next_expected)


if __name__ == '__main__':

    print_message("RX script started.")
    start_time = time.time()
    # Stores when the last package was received to fullfill system requirement of:
    # Send ACK after 1 s. without a correct reception

    while 1:
        data, addr = sockt.recvfrom(1024)

        # Receive, decode and handle data
        data = data.decode('ascii')
        error = int(data.split("-")[0])
        num = int(data.split("-")[1])

        if error == 0:
            print_message("| ACK received " + num)
            new_expected = manage_buffer_process(num)

            if new_expected == num:
                next_expected = new_expected
                print_message("|NEXT NUM EXPECTED| " + str(next_expected))

                # Send ACK after 2s. without a correct reception
                check_timeout_thread = threading.Thread(target=check_ack_timeout)
                check_timeout_thread.start()
        else:
            print_message("Error datagram " + num)