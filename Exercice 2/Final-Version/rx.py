import socket
import threading
import time
import utils as utl

# Sketch values
ACK_TIMEOUT = 2.0
SEGMENTS_SEQUENCE = 3
RECEIVER_BUFFER_SIZE = 10


buffer = []
next_expected = 0
start_time = time.time()


def buffer_control(num):
    """
    Controls buffer not to be filled.
    Checking:
    1. Reveived seg num
    2. Lowest seg num in buffer
    3. Buffer Size = 10
    """

    global buffer, next_expected

    # Checks lowest segment num in buffer
    if not buffer:
        first_num = next_expected
    else:
        first_num = min(buffer[0], next_expected)

    # Controls buffer and sends ack
    if first_num <= num < first_num + RECEIVER_BUFFER_SIZE and num not in buffer:
        buffer.append(num)
        buffer.sort()
        utl.print_trace(utl.BUFFER + str(buffer), start_time)

        if next_expected >= buffer[0]:
            return check_sequence()


def is_sequence(next_seg):
    """
    Checks if: 3 or more segments in sequence
    Computes next expected segment
    """
    sequence = 0

    for seg in buffer:
        if seg == next_seg:
            next_seg += 1
            sequence += 1

    return next_seg, sequence >= SEGMENTS_SEQUENCE


def check_sequence():
    """
    Send ACK immediately when 3 or more segments in sequence
    :return: Next expected segment
    """
    global buffer

    next_seg = buffer[0]
    sequence = 0
    #next_seg, sequence = is_sequence(next_seg)
    for seg in buffer:
        if seg == next_seg:
            next_seg += 1
            sequence += 1

    if sequence:
        send_ack(next_seg)
        # Clear sequence in buffer
        buffer = buffer[sequence:]
    return next_seg


def time_out_checker(next_expected_time_out):
    """
    Send ACK after 2 s. without a correct reception
    """
    global next_expected

    time.sleep(ACK_TIMEOUT)

    utl.print_trace(utl.RX_TIMEOUT, start_time)
    if next_expected_time_out == next_expected:

        timeout_thread = threading.Thread(target=time_out_checker, args=(next_expected,))
        timeout_thread.start()

        send_ack(next_expected)


def send_ack(next_expected):
    datagram = utl.ACK + str(next_expected)
    s.sendto(datagram.encode('utf-8'), (utl.HOST, utl.PORT_ACK))
    utl.print_trace(utl.SEGMENT_SENDED + str(next_expected), start_time)


if __name__ == '__main__':
    utl.print_trace(" RX running", start_time)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((utl.HOST, utl.PORT))

    # INFINITE LOOP IMPLEMENTIG RX.
    while True:
        # Waits for TX segments
        data, addr = s.recvfrom(1024)
        data = data.decode('utf-8')

        # Parses segment content:
        # error_indicator (0 no error, 1 error) - segment_number
        error = int(data.split("-")[0])
        num = int(data.split("-")[1])

        if error == utl.NO_ERROR:
            utl.print_trace(utl.SEGMENT_RECEIVED + str(num), start_time)
            new_expected = buffer_control(num)

            if num == next_expected:
                next_expected = new_expected
                utl.print_trace(utl.SEGMENT_EXPECTED + str(next_expected), start_time)

                timeout_thread = threading.Thread(target=time_out_checker, args=(next_expected,))
                timeout_thread.start()
        else:
            utl.print_trace(utl.SEGMENT_ERROR + str(num), start_time)
