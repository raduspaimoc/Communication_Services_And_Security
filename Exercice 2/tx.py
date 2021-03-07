#!/usr/bin/python
import time
import threading
import tcp_proto as tcp

NO_ERROR_MESSAGE = ''

# TX and RX connection values
HOST = 'localhost'
PORT = 50007
PORT_ACK = 50008

TO = 5.0

# CONNECTION DURATION
LIMIT_TIME = 200
TIMEOUT = 10

# Buffers sizes
MAX_SEND_BUFFER = 20
MAX_RECV_BUFFER = 20
EMPTY = 0

# Boolean that controls the tx execution in function of LIMIT_TIME
running = True

# Vars store last datagram sent and last ack
last_sent = -1
last_ack = -1

# Buffer containing written packages awaiting to be sent
buffer = []
# Retransmission buffer containg packages lost that will be resended
ret_buffer = []
# List of all retransmission packages used for Karn/Partridge algorithm
all_ret_buffer = []

error_rate = 0.3

# List that stores packages sent & the time they were sent
packages = []

# Variable used to count sequentially the packages
pack_count = 0

# Variables used to generate plots
t_plt = []
srtt_plt = []
cwnd_plt = []

# Sketch variables used in the script
MSS = 1
transmission_time = 1
alpha = 0.8
cwmax = 4
cwini = 1
cwnd = cwini
effective_window = cwnd
rtt = 11  # Segment transmission time = 1 + timeout = 10
srtt = rtt
srtt = tcp.SRTT(alpha, srtt, rtt)
start_time = time.time()
current_time = time.time()

# Get sockets needed
transfer_sock, receive_sock = tcp.create_sockets(HOST, PORT_ACK)


def is_prime(num):
    # Returns True if number is prime
    # 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101,
    # 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199,
    if num >= 2:
        for y in range(2, num):
            if not (num % y):
                return False
    else:
        return False
    return True


def create_output_file(output_file_name="log.txt"):
    header = "|Time (s)|Event|Eff.Win. (MSS)|cwnd (MSS)|RTT (s)|sRTT (s)|TOut (s)\n"
    sub_header = "|--------|-----|--------------|----------|-------|--------|-------|\n"
    with open(output_file_name, mode='w', newline='\n') as file:
        file.write(header)
        file.write(sub_header)
        file.close()


def add_log_to_output_file(t, log, effective_window, cwnd, rtt, srtt, timeout, output_file_name="log.txt"):
    # Adds values to log.txt in a table format
    with open(output_file_name, mode='a', newline='\n') as file:
        row = ("%.2f" % t)
        row += "|" + log
        row += "|" + str(effective_window)
        row += "|" + str(cwnd)
        row += "|" + ("%.2f" % rtt)
        row += "|" + ("%.2f" % srtt)
        row += "|" + str(timeout)
        row += "\n"
        file.write(row)
        file.close()


def print_message(info_message, error=False):
    # Shows info data on the terminal
    global current_time, start_time
    current_time = time.time() - start_time
    if error:
        print(str(round(current_time, 2)), ' | ', info_message)
    else:
        print(str(round(current_time, 2)), ' | ', info_message)


def ack_process():
    global receive_sock
    # Thread responsible of receiving and processing ACKs from rx
    print("ACK thread started.")

    while running:
        # Receive, decode and handle data, as well as marking its arrival time
        data, addr = receive_sock.recvfrom(1024)
        data = data.decode('ascii')
        num = int(data.split('-')[1])
        received_at = (time.time() - start_time)

        # Calls function to update TCP values
        update_tcp_metrics(num, received_at)

        # Log both in log file as well as terminal
        print_message("ACK received " + data)
        log = "ACK " + str(num) + " received"
        add_log_to_output_file(received_at, log, effective_window, cwnd, rtt, srtt, TIMEOUT)

    print("ACK thread finished.")


def update_tcp_metrics(ack_num, received_at):
    global cwnd, cwmax, MSS, rtt, srtt, TIMEOUT, effective_window, last_ack, packages, all_ret_buffer

    # 1. Checks if it's not a retrans (Karn/Partridge algorithm)
    # 2. Finds the respective packet updating RRT depending on its sending and received times
    # 3. Updates SRTT value
    if ack_num not in all_ret_buffer:
        for item in packages:
            if item['num'] == ack_num:
                rtt = tcp.RTT(received_at, item["transmission_time"])

        srtt = tcp.SRTT(alpha, srtt, rtt)

    # Updates Congestion Window
    if cwnd < cwmax:
        cwnd += MSS
    else:
        cwnd += MSS / cwnd
        cwmax = min(cwmax, cwnd)

    # Updates Time Out
    TIMEOUT = 2 * srtt

    # Updates last acknowledged package
    last_ack = ack_num

    # Updates Effective Window
    effective_window = tcp.get_effective_window(cwnd, last_sent, last_ack)


def send_package():
    global running, buffer, last_sent, last_ack, packages, transfer_sock
    # Thread responsible of sending packages to the receiver

    print("Send package thread started.")

    while running:
        if len(buffer) > EMPTY:
            # Send a packet only if:
            # the effective_window > 0
            # last_sent - last_ack <= effective_window
            if effective_window > EMPTY and (last_sent - last_ack) <= effective_window:
                num = buffer[0]
                error = '0'
                error_log = NO_ERROR_MESSAGE
                del buffer[0]

                # Segments with a prime sequence number are considered lost (when transmitted for
                # the first time)
                if is_prime(num):
                    error = '1'
                    error_log = "Datagram " + str(num) + " lost"

                datagram = error + '-' + str(num)

                time.sleep(transmission_time)

                last_sent = num
                transfer_sock.sendto(datagram.encode(), (HOST, PORT))

                sent_at = (time.time() - start_time)
                packages.append({'num': num, 'transmission_time': sent_at})

                # Adds log to output file
                log = 'Datagram ' + str(num) + ' sent'
                add_log_to_output_file(sent_at, log, effective_window, cwnd, rtt, srtt, TIMEOUT)
                # Shows info on terminal
                print_message('Sent: ' + datagram)

                if error_log != NO_ERROR_MESSAGE:
                    add_log_to_output_file((time.time() - start_time),
                                           error_log, effective_window, cwnd, rtt, srtt, TIMEOUT)
                    print_message(error_log, error=True)

                # Creates thread responsible for taking care of possible timeout
                start_threads(timeout_thread=True, num=num)
                timeout_checker_thread = threading.Thread(target=timeout_checker, args=(
                    num,), name="Thread-pck-" + str(num))
                timeout_checker_thread.start()

    print("Send package thread closed.")


def timeout_checker(num):
    # Thread created for each packet sent.
    global cwnd, cwini, cwmax, last_ack, ret_buffer, all_ret_buffer, effective_window

    # Awaiting Timeout time
    time.sleep(TIMEOUT)

    # If timer is over and ack has not yet been received:
    # - updates congestion window values
    # - mark package to retransmission
    # - call appropriated function to deal with it
    if num >= last_ack:
        cwnd = cwini
        cwmax = max(cwini, (cwmax/2))

        ret_buffer.append(num)
        all_ret_buffer.append(num)
        log = "TimeOut: " + str(num)
        print_message(log)
        add_log_to_output_file((time.time() - start_time), log, effective_window, cwnd, rtt, srtt, TIMEOUT)

        send_ret_packages()


def send_ret_packages():
    # Function responsible of sending packages of the retransmission buffer
    global effective_window, ret_buffer, transmission_time, transfer_sock, start_time

    while len(ret_buffer) > 0:
        # Send a packet only if the effective window is larger than 0
        if effective_window > 0:

            # Selects package to be retransmitted, create its datagram, remove it from the
            # Retransmition Buffer awaits the appropriate transmition time, resends the package
            # and finally add it to the sent packages list
            if ret_buffer:
                num = ret_buffer[0]
                datagram = '0-'+str(num)
                del ret_buffer[0]

                time.sleep(transmission_time)
                transfer_sock.sendto(datagram.encode(), (HOST, PORT))

                sent_at = (time.time() - start_time)
                packages.append({'num': num, 'transmission_time': sent_at})

                print_message('Sent Retrans: ' + datagram)
                log = 'Sent Retrans: ' + str(num)
                add_log_to_output_file((time.time() - start_time), log, effective_window, cwnd, rtt, srtt, TIMEOUT)


def plot_data():
    global t_plt, srtt_plt, cwnd_plt
    # Thread responsible of storing cwnd,  sRTT each second for plotting
    print("Plot data thread started.")

    while running:
        t_plt.append(time.time() - start_time)
        srtt_plt.append(srtt)
        cwnd_plt.append(cwnd)
        time.sleep(1)


def start_threads(timeout_thread=False, num=0):
    if timeout_thread:
        # Creates thread to check timeout of receiving acknowledgment
        timeout_checker_thread = threading.Thread(target=timeout_checker, args=(
            num,), name="Thread-pck-" + str(num))
        timeout_checker_thread.start()
    else:
        # Creates the list of threads
        ack_process_thread = threading.Thread(target=ack_process)
        send_package_thread = threading.Thread(target=send_package)
        plot_data_thread = threading.Thread(target=plot_data)

        # Starts list of threads
        ack_process_thread.start()
        send_package_thread.start()
        plot_data_thread.start()


def send_buffer_process():
    # Function on the main thread responsible of handling
    # the ***buffer** which contains the data to be converted
    # into packets to be send to rx
    global pack_count, buffer
    while EMPTY <= len(buffer) < MAX_SEND_BUFFER:
        buffer.append(pack_count)
        pack_count += 1


if __name__ == '__main__':
    #global running
    create_output_file()
    start_threads()

    while running:
        # Controls the program execution in function of the
        running = time.time() - start_time < LIMIT_TIME
        # Controls buffer
        send_buffer_process()

    print_message("200s sequence completed.")
    # print("TIME: ", t_plt)
    # print("CWND: ", cwnd_plt)
    # print("SRTT: ", srtt_plt)

# Plots of cwnd and sRTT as a function of time
# u.plot(timePlot, srttPlot, cwndPlot)
# u.plot_cwnd(timePlot, cwndPlot)
# u.plot_sRTT(timePlot, srttPlot)
