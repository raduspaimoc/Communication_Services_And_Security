#!/usr/bin/python
import socket


# Contains implementations for the following params:
# 1. SRTT
# 2. RTT
# 3. Effective Window


def SRTT(alpha, srtt, rtt):
    # Calculates Estimated Round Trip Time (sRTT)
    return alpha * srtt + (1 - alpha) * rtt


def RTT(current_time, sent_at):
    # Calculates Round Trip Time (RTT)
    return current_time - sent_at


def get_effective_window(cwnd, last_sent, last_ack):
    # Calculates Effective Window (cwnd)
    return int(cwnd - (last_sent - last_ack))


def create_sockets(host, port):

    # UDP sockets to transfer and receive data between TX and RX
    transfer_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_sock.bind((host, port))
    return transfer_sock, receive_sock