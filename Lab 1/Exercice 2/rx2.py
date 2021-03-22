import struct
import socket
import threading
from datetime import datetime
import time

HOST = 'localhost'
PORT = 50007  # Arbitrary non-privileged port
PORT_ACK = 50008
rx_buffer = []
timeout_time = 2.0
next_expected = 0


def send_ack(next_expected):
    datagram = '0-'+ str(next_expected)
    s.sendto(datagram.encode(), (HOST, PORT_ACK))
    print_trace("|SEND ACK| " + str(next_expected))


def print_trace(trace):
    print(str(datetime.now()) + '  |  ' + str(trace))


def time_out(next_expected_time_out):
    global next_expected
    time.sleep(timeout_time)
    print_trace("|RX TIMEOUT|")
    if next_expected_time_out == next_expected:
        t = threading.Thread(target=time_out, args=(next_expected,))
        t.start()

        send_ack(next_expected)


def check_sequence():
    global rx_buffer

    next_seg = rx_buffer[0]
    sequence = 0

    for seg in rx_buffer:
        if seg == next_seg:
            next_seg += 1
            sequence += 1

    if sequence >= 3:
        send_ack(next_seg)
        # Clear sequence in buffer
        rx_buffer = rx_buffer[sequence:]
    return next_seg


def buffer_management(num):
    global rx_buffer, next_expected
    # Send ACK immediately when 3 or more segments in sequence

    if not rx_buffer:
        first_num = next_expected
    else:
        first_num = min(rx_buffer[0], next_expected)

    if first_num <= num < first_num + 10 and num not in rx_buffer:
        rx_buffer.append(num)
        rx_buffer.sort()
        print_trace("|BUFFER| " + str(rx_buffer))

        if next_expected >= rx_buffer[0]:
            return check_sequence()


if __name__ == '__main__':
    print("RX running")

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, PORT))

    while 1:
        data, addr = s.recvfrom(1024)
        data = data.decode('ascii')
        num = int(data.split('-')[1])
        error = int(data.split('-')[0])
        #segment = struct.unpack('ii', data)

        #error = segment[0]
        #num = segment[1]

        if error == 0:
            print_trace("|NUM RECEIVED| " + str(num))

            new_expected = buffer_management(num)

            if num == next_expected:
                next_expected = new_expected
                print_trace("|NEXT NUM EXPECTED| " + str(next_expected), )

                # Send ACK after 2 s. without a correct reception
                t = threading.Thread(target=time_out, args=(next_expected,))
                t.start()
        else:
            print_trace("|ERROR NUM| " + str(num))
