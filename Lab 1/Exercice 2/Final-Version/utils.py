import time
import pandas as pd
import matplotlib.pyplot as plt

# Shared values
PORT = 50007
PORT_ACK = 50008
HOST = 'localhost'
NO_ERROR = 0
ZERO = 0

# Info Strings
ACK_RECEIVED_SHORT = "ACK RECEIVED"
LAST_ACK = " LAST ACK: "
SEGMENT_TIMEOUT = "______TIMEOUT. SEGMENT______: "
ACK_RECEIVED = "______ACK RECEIVED______: "
RETRANSMISSION_SENT = "______RETRANSMISSION SENDED______: "
SEGMENT_RECEIVED = " SEGMENT RECEIVED      \t| "
SEGMENT_EXPECTED = " NEXT SEGMENT EXPECTED \t| "
SEGMENT_ERROR = " ERROR SEGMENT         \t| "
SEGMENT_SENDED = " SENDED ACK            \t| "
BUFFER = " BUFFER                \t| "
RX_TIMEOUT = " RX TIMEOUT            \t| "
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
    print_trace("LAST_SENT: {0} LAST_ACK: {1} EFF.WIN: {2} CWND: {3} CWMAX: {4}".format(str(last_sent), str(last_ack),
                                                                                        str(eff_win), str(cwnd),
                                                                                        str(cwmax)), start_time)


def print_sent_segment_info(last_sent, last_ack, eff_win, cwnd, cwmax, timeout_time, start_time):
    print_trace("______SEND NUM______", start_time)
    print_trace("LAST_SENT: {0} LAST_ACK: {1} EFF.WIN: {2} CWND: {3} CWMAX: {4} TIMEOUT: {5}".format(str(last_sent),
                                                                                                     str(last_ack),
                                                                                                     str(eff_win),
                                                                                                     str(cwnd),
                                                                                                     str(cwmax),
                                                                                                     str(("%.2f" % timeout_time))),
                start_time)


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
    """
       Creates plot with 2 lines:
       1. x: 'Time (s)' -  cwnd (MSS)'
       2. x: 'Time (s)' - 'RTT (s)'
       ['Time (s)', 'Event', 'Eff.Win. (MSS)', 'cwnd (MSS)', 'RTT (s)', 'sRTT (s)', 'TOut (s)']
       Also calls the plot generator function
    """
    fig, ax = plt.subplots()
    plt.figure(figsize=(12, 7))
    plt.plot(df['Time (s)'], df['cwnd (MSS)'], linewidth=4, label="Congestion Window (cwnd)")
    plt.plot(df['Time (s)'], df['sRTT (s)'], linewidth=4,
             label="Estimate RTT (sRTT)")
    plt.xlabel('Time (s)')
    plt.title('CWND and sRTT as a function of time', fontweight='bold')
    plt.legend()
    plt.savefig('CWND and sRTT.jpg')
