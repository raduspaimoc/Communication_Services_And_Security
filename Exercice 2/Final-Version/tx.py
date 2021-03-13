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

EXECUTION_TIME = 200.0

last_ack = -1
last_sent = -1
timeout_time = 10.0
seg_t_time = 1.0
retrans_buffer = []
segment_num = 0

sent_segments_times = {}

RTT = 10.0
sRTT = 10.0

cwini = MSS
cwnd = MSS
cwmax = CWMAX
eff_win = cwnd

# Sequence control params
start_time = time.time()
running = True

# List of lists containing:
# ['Time (s)', 'Event', 'Eff.Win. (MSS)', 'cwnd (MSS)', 'RTT (s)', 'sRTT (s)', 'TOut (s)']
output_table = []


def update_output_table(event):
    eff_win_csv = eff_win
    if eff_win_csv < 0:
        eff_win_csv = 0

    current_time = ("%.2f" % (time.time() - start_time))
    output_table.append([current_time,
                         event,
                         eff_win_csv,
                         cwnd,
                         RTT,
                         sRTT,
                         timeout_time])


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
            sRTT = ALPHA * sRTT + (1 - ALPHA) * RTT
            timeout_time = 2 * sRTT

            utl.print_rtt_info(num_seg, RTT, sRTT, timeout_time, start_time)
        if num_seg + 1 <= last_ack:
            del sent_segments_times[num_seg]


def calculate_slow_start(time_out):
    '''
    :param time_out: True if a segment get a time out, false if it receive an ACK
    Calculate the congestion window using the slow start algorithm.
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


def process_ack():
    '''
    When receive an ack bigger than last ack, calculate the rrt and applies the slow start algorithm to calculate the congestion windows
    '''
    global last_ack
    while running:
        data, addr = receive_sock.recvfrom(1024)
        data = data.decode('utf-8')
        num = int(data.split('-')[1])
        update_output_table("ACK")

        #num = int(data)
        if num > (last_ack):
            utl.print_trace("_____ACK RECEIVED_______: " + str(data), start_time)
            last_ack = num
            round_trip_time()
            calculate_slow_start(False)


def send_retrans_buffer():
    '''
     Send the segments of the retransmission buffer
    '''
    global sent_segments_times

    while len(retrans_buffer) > 0:
        retrans_segment = retrans_buffer[0]
        del retrans_buffer[0]
        # Mesure RTT only when no retransmission

        # Check needed
        if retrans_segment[1] in sent_segments_times:
            del sent_segments_times[retrans_segment[1]]

        time.sleep(seg_t_time)

        datagram = str(retrans_segment[0]) + '-' + str(retrans_segment[1])
        transfer_sock.sendto(datagram.encode('utf-8'), (utl.HOST, utl.PORT))
        utl.print_trace("_____RETRANSMISSION SENDED_____: " + str(retrans_segment), start_time)

        t = threading.Thread(target=time_out, args=(retrans_segment,))
        t.start()


def time_out(segment):
    '''
    :param segment: [error, segment num]
    Sleeps during the current time out, and resend the segment if the last ACK don't acknowledges that segment
    '''
    global retrans_buffer, last_ack

    time.sleep(timeout_time)

    num = segment[1]

    if num >= last_ack:
        utl.print_trace("_____Time out. SEG num_____: " + str(num) + " LAST ACK: " + str(last_ack), start_time)

        retrans_buffer.append([0, num])  # Retrans is not error

        send_retrans_buffer()
        calculate_slow_start(True)


def send_segment(segment):
    '''
    :param segment: [error, segment num]
    Send a segment, recalculate the effective window and start a time out for that segment.
    '''
    global sent_segments_times, last_sent, eff_win, last_ack, timeout_time

    num = segment[1]
    #struct_segment = struct.pack('ii', segment[0], segment[1])  # error , segment num
    datagram = str(segment[0]) + '-' + str(segment[1])

    time.sleep(seg_t_time)
    transfer_sock.sendto(datagram.encode('utf-8'), (utl.HOST, utl.PORT))

    last_sent = num
    update_output_table("SEND SEGMENT")

    sent_segments_times[num] = datetime.now()

    utl.print_trace("_______________SEND NUM_______________", start_time)
    eff_win = cwnd - (last_sent - last_ack)
    utl.print_trace("last_Sent: " + str(last_sent), start_time)
    utl.print_trace("last_ACK: " + str(last_ack), start_time)
    utl.print_trace("Eff_win: " + str(eff_win), start_time)
    utl.print_trace("Timeout: " + str(timeout_time), start_time)

    t = threading.Thread(target=time_out, args=(segment,))
    t.start()


def get_next_segment():
    global segment_num

    if sympy.isprime(segment_num):
        error = 1
    else:
        error = 0

    segment = [error, segment_num]
    segment_num += 1
    return segment


if __name__ == '__main__':
    utl.print_trace("TX running", start_time)

    #transfer_sock,  receive_sock = utl.create_sockets(utl.HOST, utl.PORT_ACK)
    transfer_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    receive_sock.bind((utl.HOST, utl.PORT_ACK))

    x = threading.Thread(target=process_ack)
    x.start()

    while running:
        # Controls the program execution in function of the sequence limit time
        running = time.time() - start_time < LIMIT_TIME

        if eff_win > 0:
            send_segment(get_next_segment())

    utl.print_trace("200s sequence completed.", start_time)
    utl.write_output_table(output_table, start_time)
