import time
import socket
import pandas as pd
import matplotlib.pyplot as plt

PORT = 50007
PORT_ACK = 50008
HOST = 'localhost'

SEGMENT_RECEIVED = " SEGMENT RECEIVED \t| "
SEGMENT_EXPECTED = " NEXT SEGMENT EXPECTED \t| "
SEGMENT_ERROR = " ERROR SEGMENT \t| "
SEGMENT_SENDED = " SENDED ACK \t| "
BUFFER = " BUFFER \t| "
RX_TIMEOUT = " RX TIMEOUT \t| "
ACK = 'ACK-'


def print_trace(trace, start_time):
    """
        Prints trace
    """
    current_time = time.time() - start_time
    print(str(("%.2f" % current_time)) + '\t |  ' + str(trace))


def print_rtt_info(num_seg, rtt, srtt, timeout_time, start_time):
    print_trace("______RTT______", start_time)
    print_trace("Segment Num: {0} RTT: {1} sRTT: {2} Timeout: {3}".format(str(num_seg), str(rtt), str(srtt),
                                                                          str(("%.2f" % timeout_time))), start_time)


def print_congestion_control_info(last_sent, last_ack, eff_win, cwnd, cwmax, start_time):
    print_trace("______Slow Start______", start_time)
    print_trace("LAST_SENT: {0} LAST_ACK: {1} EFF.WIN: {2} Cwnd: {3} CWMAX: {4}".format(str(last_sent), str(last_ack),
                                                                                        str(eff_win), str(cwnd), str(cwmax)), start_time)

def print_sended_segment_info():
    utl.print_trace("_______________SEND NUM_______________", start_time)
    utl.print_trace("last_Sent: " + str(last_sent), start_time)
    utl.print_trace("last_ACK: " + str(last_ack), start_time)
    utl.print_trace("Eff_win: " + str(eff_win), start_time)
    utl.print_trace("Timeout: " + str(timeout_time), start_time)


def write_output_table(output_table, start_time):
    """
        Writes output table in .csv format:
        ['Time (s)', 'Event', 'Eff.Win. (MSS)', 'cwnd (MSS)', 'RTT (s)', 'sRTT (s)', 'TOut (s)']
        Also calls the plot generator function
    """
    print_trace("Writing file...", start_time)
    df = pd.DataFrame(output_table,
                      columns=['Time (s)', 'Event', 'Eff.Win. (MSS)', 'cwnd (MSS)', 'RTT (s)', 'sRTT (s)', 'TOut (s)'])
    df.to_csv("First(200s) values.csv", index=False)
    print_trace("Generating plot...", start_time)
    create_plot(df)
    print_trace("Files created.", start_time)


def create_plot(df):
    fig, ax = plt.subplots()
    ax.plot(df['Time (s)'], df['cwnd (MSS)'], label="Congestion Window (cwnd)")
    ax.plot(df['Time (s)'], df['sRTT (s)'], label="Estimated RTT (sRTT)")
    plt.xlabel('Time (s)')
    plt.title('CWND and sRTT as a function of time')
    plt.legend()
    plt.xticks([1, 25, 50, 75, 100, 125, 150, 175, 200, 225])
    plt.savefig('CWND and sRTT (Script generated).jpg')


def create_sockets(host, port):
    # UDP sockets to transfer and receive data between TX and RX
    transfer_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_sock.bind((host, port))
    return transfer_sock, receive_sock
