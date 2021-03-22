from datetime import datetime
import time
import threading
import sympy
import socket
import utils as utl

# CONNECTION DURATION
LIMIT_TIME = 200

# Sketch params
ALPHA = 0.8
CWMAX = 4
MSS = 1

last_ack = -1
last_sent = -1
segment_num = 0
timeout_time = 10.0
seg_transmission_time = 1.0

cwini = MSS
cwnd = MSS
cwmax = CWMAX
eff_win = cwnd

RTT = 10.0
sRTT = 10.0

sent_segments_times = {}
ret_buffer = []

# Sequence control params
start_time = time.time()
running = True

# List of lists containing:
# ['Time (s)', 'Event', 'Eff.Win. (MSS)', 'cwnd (MSS)', 'RTT (s)', 'sRTT (s)', 'TOut (s)']
table = []


def update_table(event):
    aux_ew = eff_win

    # If effective window is negative we store it as 0.
    if aux_ew < 0:
        aux_ew = 0

    current_time = ("%.2f" % (time.time() - start_time))
    table.append([current_time,
                 event,
                 aux_ew,
                 cwnd,
                 RTT,
                 sRTT,
                 timeout_time])


def retransmit_segment():
    '''
     1. Checks if exists segments in ret_buffer
     2. Removes it from sent segments
     3. Resends segment
     4. Creates thread to check segment timeout
    '''
    global sent_segments_times

    while len(ret_buffer) > 0:
        ret_segment = ret_buffer[0]
        del ret_buffer[0]


        # Check needed
        if ret_segment[1] in sent_segments_times:
            del sent_segments_times[ret_segment[1]]

        time.sleep(seg_transmission_time)

        datagram = str(ret_segment[0]) + '-' + str(ret_segment[1])
        transfer_sock.sendto(datagram.encode('utf-8'), (utl.HOST, utl.PORT))
        utl.print_trace(utl.RETRANSMISSION_SENT + str(ret_segment), start_time)

        time_out_checker_thread = threading.Thread(target=time_out_checker, args=(ret_segment,))
        time_out_checker_thread.start()


def time_out_checker(segment):
    '''
    :param segment: [error, segment_num]
    1. Sleeps current timeout time
    2. Resend segment if LAST ACK doesn't acknowledge the received segment
    3. Updates slow_start metrics
    '''
    global ret_buffer, last_ack

    time.sleep(timeout_time)

    num = segment[1]

    if num >= last_ack:
        utl.print_trace(utl.SEGMENT_TIMEOUT + str(num) + utl.LAST_ACK + str(last_ack), start_time)

        # Retransmissions aren't considered errors.
        ret_buffer.append([utl.NO_ERROR, num])

        retransmit_segment()
        slow_start(True)


def get_next_segment():
    """
    1. If current segment is prime return error.
    2. Increases segment
    3. Returns tuple [error, segment_num]
    """
    global segment_num

    if sympy.isprime(segment_num):
        error = 1
    else:
        error = 0

    segment = [error, segment_num]
    segment_num += 1
    return segment


def send_segment():
    '''
    1. Gets segment
    2. Waits segment transmission time
    3. Sends seg to RX
    4. Updates effective window
    5. Creates thread to check timeout
    '''
    global sent_segments_times, last_sent, eff_win, last_ack, timeout_time

    is_error, num = get_next_segment()
    datagram = str(is_error) + '-' + str(num)

    time.sleep(seg_transmission_time)
    transfer_sock.sendto(datagram.encode('utf-8'), (utl.HOST, utl.PORT))

    last_sent = num
    update_table("SEND SEGMENT")

    sent_segments_times[num] = datetime.now()

    eff_win = cwnd - (last_sent - last_ack)
    utl.print_sent_segment_info(last_sent, last_ack, eff_win, cwnd, cwmax, timeout_time, start_time)

    time_out_checker_thread = threading.Thread(target=time_out_checker, args=([is_error, num],))
    time_out_checker_thread.start()


def slow_start(time_out):
    '''
    :param time_out: Indicator: True if segment exceds timeout
    Applies the slow start algorithm for computing the cwnd
    '''
    global cwini, cwmax, cwnd, eff_win, last_sent, last_ack
    if time_out:
        cwnd = cwini
        cwmax = max(cwini, cwmax / 2)
    else:
        if cwnd < cwmax:
            cwnd += MSS
        else:
            cwnd += MSS / cwnd
            cwmax = min(CWMAX, cwnd)

    eff_win = cwnd - (last_sent - last_ack)

    utl.print_congestion_control_info(last_sent, last_ack, eff_win, cwnd, cwmax, start_time)


def round_trip_time():
    '''
    Computes:
    1. RTT,
    2. sRTT
    3. Timeout for the last acknowledged and not retransmitted segment.
    '''
    global last_ack, sent_segments_times, sRTT, RTT, timeout_time

    for num_seg, init_time in list(sent_segments_times.items()):
        if num_seg + 1 == last_ack:
            RTT = (datetime.now() - init_time).total_seconds()
            sRTT = (ALPHA * sRTT) + ((1 - ALPHA) * RTT)
            timeout_time = 2 * sRTT

            utl.print_rtt_info(num_seg, RTT, sRTT, timeout_time, start_time)
        if num_seg + 1 <= last_ack:
            del sent_segments_times[num_seg]


def process_ack():
    '''
    1. Gets ACK from RX
    2. Applies the slow start algorithm to calculate the congestion windows
    '''
    global last_ack

    utl.print_trace("Process ACK thread started.", start_time)
    while True:
        data, addr = receive_sock.recvfrom(1024)
        data = data.decode('utf-8')
        num = int(data.split('-')[1])
        update_table(utl.ACK_RECEIVED_SHORT)

        # If received num is > than last_ack: Updates RTT and cwnd, cwmax
        if num > last_ack:
            utl.print_trace(utl.ACK_RECEIVED + str(data), start_time)
            last_ack = num
            round_trip_time()
            slow_start(False)


if __name__ == '__main__':
    utl.print_trace("TX running", start_time)

    # UDP sockets to transfer and receive data between TX and RX.
    transfer_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Binds RX receptor socket.
    receive_sock.bind((utl.HOST, utl.PORT_ACK))

    # Creates thread to process received ACK segments.
    process_ack_thread = threading.Thread(target=process_ack)
    process_ack_thread.start()

    while running:
        # Controls the program execution in function of the sequence limit time
        running = time.time() - start_time < LIMIT_TIME

        if eff_win > utl.ZERO:
            send_segment()

    utl.print_trace("200s sequence completed.", start_time)
    utl.write_output_table(table, start_time)
