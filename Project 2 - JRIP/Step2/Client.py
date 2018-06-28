import socket
import sys
import time
import numpy as np
import _thread
from timer import Timer
from udp import *

port_number = 8080
PACKET_SIZE = 64
SENDER_ADDR = ('localhost', 0)
SLEEP_INTERVAL = 0.01
TIMEOUT_INTERVAL = 0.5
WINDOW_SIZE = 5
RECEIVER_ADDR = ('localhost', port_number)

seq_last = 0
mutex = _thread.allocate_lock()
send_timer = Timer(TIMEOUT_INTERVAL)

def set_window_size(num_packets):
    global seq_last
    return min(WINDOW_SIZE, num_packets - seq_last)
# create a packet
def packet_create(seq_num, data = b''):
    seq_bytes = seq_num.to_bytes(4, byteorder = 'little', signed = True)
    return seq_bytes + data

# create an empty packet
def empty_packet_create():
    return b''

# extract data from a packet
def packet_extract(packet):
    seq_num = int.from_bytes(packet[0:4], byteorder = 'little', signed = True)
    return seq_num, packet[4:]

# client sending process
def client_send(sock, file):
    packets= []
    seq_num = 0
    with open(file, 'rb') as f:
        i = 0
        while i < 100:
            data = f.read(PACKET_SIZE)
            if not data:
                break
            packets.append(packet_create(seq_num, data))
            seq_num += 1
            i += 1
    num_packets = len(packets)
    window_size = set_window_size(num_packets)
    seq_next = 0

    # Start the receiver thread
    _thread.start_new_thread(client_receive, (sock,))

    while seq_last < num_packets:
        mutex.acquire()
        # Send all the packets in the window
        while seq_next < seq_last + window_size:
            print('Sending packet, seq: ', seq_next)
            udp_send(packets[seq_next], sock, RECEIVER_ADDR)
            seq_next += 1

        # Start the timer
        if not send_timer.if_running():
            print('timeout timer reset')
            send_timer.start()
        # Wait until a timer goes off or we get an ACK
        while send_timer.if_running() and not send_timer.if_timeout():
            mutex.release()
            time.sleep(SLEEP_INTERVAL)
            mutex.acquire()

        if send_timer.if_timeout():
            # Looks like we timed out
            print('packet timeout')
            send_timer.stop();
            seq_next = seq_last
        else:
            window_size = set_window_size(num_packets)
        mutex.release()

        # send an empty packet to sentinel the end of transfer
        udp_send(empty_packet_create(), sock, RECEIVER_ADDR)

def client_receive(sock):
    global mutex
    global seq_last
    global send_timer

    while True:
        pkt, _ = udp_recv(sock);
        ack, _ = packet_extract(pkt);

        # If we get an ACK for the first in-flight packet
        print('ACK received: ', ack)
        if (ack >= seq_last):
            mutex.acquire()
            seq_last = ack + 1
            print('last received: ', seq_last)
            send_timer.stop()
            mutex.release()


if __name__ == '__main__':

    i = 0
    while i < 100:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(SENDER_ADDR)
        filename = 'files/data_to_send.txt'
        i = i+1
    client_send(sock, filename)
    sock.close()

