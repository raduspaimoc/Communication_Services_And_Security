#!/usr/bin/python

import socket
import time
import random
import threading

# TX and RX connection values
HOST = 'localhost'
PORT = 50007
PORT_ACK = 50008


# CONNECTION DURATION
LIMIT_TIME = 200

# Boolean that controls the tx execution in function of LIMIT_TIME
running = True

# Vars store last datagram sent and last ack
last_sent = -1
last_ack = -1

TO = 5.0

# Buffer containing written packages awaiting to be sent
buffer = []
# Retransmission buffer containg packages lost that will be resended
ret_buffer =[]
# List of all retransmission packages used for Karn/Partridge algorithm
all_ret_buffer = []

error_rate = 0.3

# List that stores packages sent & the time they were sent
packages = []

# Variable used to count sequentially the packages
pack_count = 0


def create_output_file(output_file_name="log.txt"):
    header = "|Time (s)|Event|Eff.Win. (MSS)|cwnd (MSS)|RTT (s)|sRTT (s)|TOut (s)\n"
    sub_header = "|--------|-----|--------------|----------|-------|--------|--------\n"
    with open(output_file_name, mode='w', newline='\n') as file:
        file.write(header)
        file.write(sub_header)
        file.close()


def ack_process():
    # Thread responsible of receiving and processing ACKs from rx
    print("ACK thread started.")


def send_package():
    # Thread responsible of sending packages to the receiver
    print("Send package thread started.")


def plot_data():
    # Thread responsible of storing csnd,  sRTT in function of time for plotting
    print("Plot data thread started.")


def start_threads():
    # Creates the list of threads
    ack_process_thread = threading.Thread(target=ack_process())
    send_package_thread = threading.Thread(target=send_package())
    plot_data_thread = threading.Thread(target=plot_data())

    # Starts list of threads
    ack_process_thread.start()
    send_package_thread.start()
    plot_data_thread.start()


def create_sockets():
    # UDP sockets to transfer and receive data between TX and RX
    transfer_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_sock.bind((HOST, PORT_ACK))


if __name__ == '__main__':

    create_output_file()
    create_sockets()
    start_threads()

    start_time = time.time()
    while running:
        # Controls the program execution in function of the
        running = time.time() - start_time < LIMIT_TIME
