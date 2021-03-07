#!/usr/bin/python
import socket
import time
import threading

MAX_BUFFER = 21
ACK_TIMEOUT = 2

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


def manage_buffer_process():
    # Responsible of:
    # 1. Send ACK after 2 s. without a correct reception
    # 2. Send ACK immediately when 3 or more segments in sequence
    global buffer, next_expected, last_correct_recv
    print("Manage buffer process thread started.")

    while 1:
        if len(buffer) > 0 and (time.time() - last_correct_recv) > ACK_TIMEOUT:
            package = buffer[0]
            if package == next_expected:
                buffer = buffer[1:]
                next_expected = package + 1
                send_package(next_expected)
        elif len(buffer) >= 3 and buffer[0] == next_expected:
            package = buffer[len(buffer) - 1]
            buffer = buffer[len(buffer):]
            next_expected = package + 1
            send_package(next_expected)


def send_package(pack_num):
    # Code responsible of sending ACKs to TX
    time.sleep(ACK_TIMEOUT)
    datagram = 'ACK-'+str(pack_num)
    sockt.sendto(datagram.encode(), (HOST, PORT_ACK))
    print_message("Sent ACK - ", )


def recv_ack():
    # Thread responsible of receiving and processing ACKs from tx
    global start_time
    print("ACK thread started.")
    while 1:
        data, addr = sockt.recvfrom(1024)
        manageIncoming_thread = threading.Thread(target=ack_process(data))
        manageIncoming_thread.start()


def print_message(info_message):
    # Shows info data on the terminal
    global start_time
    current_time = time.time() - start_time
    print(current_time, '| ' + info_message)


def ack_process(data):
    #  Thread responsible for receiving packages from TX
    global buffer, next_expected, last_correct_recv

    # Receive, decode and handle data
    data = data.decode('ascii')
    error = int(data.split("-")[0])
    num = int(data.split("-")[1])

    if error == 0 and num >= next_expected:

        if len(buffer) < MAX_BUFFER:
            last_correct_recv = time.time()

            buffer.append(num)
            buffer.sort()
        else:
            print_message("Buffer filled. Not enoguh space to add packet.")
            print("Current buffer: ", buffer)


if __name__ == '__main__':
    #global start_time, sockt, last_correct_recv

    start_time = time.time()
    # Stores when the last package was received to fullfill system requirement of:
    # Send ACK after 1 s. without a correct reception
    last_correct_recv = time.time()

    ack_process_thread = threading.Thread(target=recv_ack)
    ack_process_thread.start()
    manage_buffer_process()