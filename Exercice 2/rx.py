#!/usr/bin/python
import socket
import time
import random
import threading


# TX and RX connection values
HOST = 'localhost'
PORT = 50007
PORT_ACK = 50008


def manage_buffer_process():
    # Responsible of:
    # Send ACK after 2 s. without a correct reception
    # Send ACK immediately when 3 or more segments in sequence
    print("Manage buffer process thread started.")


def ack_process():
    # Thread responsible of receiving and processing ACKs from tx
    print("ACK thread started.")

if __name__ == '__main__':
    # Creating and starting thread responsible for receiving incoming packages
    ack_process_thread = threading.Thread(target=ack_process)
    ack_process_thread.start()


    manage_buffer_process()