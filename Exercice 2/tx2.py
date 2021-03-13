import csv
import struct
from datetime import datetime
import socket
import time
import threading
import sympy

HOST = 'localhost'
PORT = 50007
PORT_ACK = 50008
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

# Flow Control
RTT = 10.0
sRTT = 10.0

# Congestion Control
cwini = MSS
cwnd = MSS
cwmax = CWMAX
eff_win = cwnd

output_table = []


def write_output_table():
    with open('output_table.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in output_table:
            writer.writerow(row)


def calculate_rtt():
    '''
    Calculate the RTT, sRTT and time out for the last acknowledged and not retransmitted segment.
    '''
    global last_ack, sent_segments_times, sRTT, RTT, timeout_time

    for num_seg, init_time in sent_segments_times.items():
        if num_seg + 1 == last_ack:
            RTT = (datetime.now() - init_time).total_seconds()
            sRTT = ALPHA * sRTT + (1 - ALPHA) * RTT
            timeout_time = 2 * sRTT

            print_trace("______RTT calculation____")
            print_trace("Num: " + str(num_seg))
            print_trace("rtt: " + str(RTT))
            print_trace("srtt: " + str(sRTT))
            print_trace("timeout: " + str(timeout_time))
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

    print_trace("_____Slow Start Calculation_______")
    print_trace("last_Sent: " +str(last_sent))
    print_trace("last_ACK: " +str(last_ack))
    print_trace("eff_win: " + str(eff_win))
    print_trace("cwnd: " + str(cwnd))
    print_trace("cwmax: " + str(cwmax))


def process_ack():
    '''
    When receive an ack bigger than last ack, calculate the rrt and applies the slow start algorithm to calculate the congestion windows
    '''
    global last_ack
    while 1:
        data, addr = s2.recvfrom(1024)
        data = data.decode('ascii')
        num = int(data.split('-')[1])
        update_output_table("ACK")

        if num > (last_ack):
            print_trace("_____ACK rec_______: " + str(data))
            last_ack = num
            calculate_rtt()
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

        del sent_segments_times[retrans_segment[1]]

        time.sleep(seg_t_time)

        datagram = str(retrans_segment[0]) + '-' + str(retrans_segment[1])

        s.sendto(datagram.encode(), (HOST, PORT))
        print_trace("_____Send retrans_____: " + str(retrans_segment))

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
        print_trace("_____Time out. SEG num_____: " + str(num) + " LAST ACK: " + str(last_ack))

        retrans_buffer.append([0, num])  # Retrans is not error

        send_retrans_buffer()
        calculate_slow_start(True)


def update_output_table(event):
    eff_win_csv = eff_win
    if eff_win_csv < 0:
        eff_win_csv = 0
    output_table.append([datetime.now().strftime('%H:%M:%S'),
                         event,
                         eff_win_csv,
                         cwnd,
                         str(RTT).replace('.', ','),
                         str(sRTT).replace('.', ','),
                         str(timeout_time).replace('.', ',')])


def send_segment(segment):
    '''
    :param segment: [error, segment num]
    Send a segment, recalculate the effective window and start a time out for that segment.
    '''
    global sent_segments_times, last_sent, eff_win, last_ack, timeout_time

    num = segment[1]
    datagram = str(segment[0]) + '-' + str(segment[1])
    #struct_segment = struct.pack('ii', segment[0], segment[1])  # error , segment num

    time.sleep(seg_t_time)
    s.sendto(datagram.encode(), (HOST, PORT))

    last_sent = num
    update_output_table("SEND SEGMENT")

    sent_segments_times[num] = datetime.now()

    print_trace("_______________SEND NUM_______________")
    eff_win = cwnd - (last_sent - last_ack)
    print_trace("last_Sent: " + str(last_sent))
    print_trace("last_ACK: " + str(last_ack))
    print_trace("Eff_win: " + str(eff_win))
    print_trace("Timeout: " + str(timeout_time))

    t = threading.Thread(target=time_out, args=(segment,))
    t.start()


def print_trace(trace):
    print(str(datetime.now()) + '  |  ' + str(trace))


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
    print("TX running")

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    s2.bind((HOST, PORT_ACK))

    x = threading.Thread(target=process_ack)
    x.start()

    initial_time = datetime.now()
    while (datetime.now() - initial_time).total_seconds() < EXECUTION_TIME:
        if eff_win > 0:
            send_segment(get_next_segment())

    write_output_table()
