import socket
import sys
import time
import numpy as np

#port_number = 8080
#ip_address = '35.185.116.250'
#ip_add = 'localhost'
#p_loss = 0.1
PACKET_SIZE = 64
SENDER_ADDR = ('localhost', 0)
SLEEP_INTERVAL = 0.05
TIMEOUT_INTERVAL = 0.5
WINDOW_SIZE = 4

packet_last = 0
mutex = _thread.allocate_lock()
send_timer = Timer(TIMEOUT_INTERVAL)

def set_window_size(num_packets):
    global packet_last
    return min(WINDOW_SIZE, num_packets - packet_last)
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
def process(file, addr):
    packets= []
    seq_num = 0
    with open(file, 'rb') as f:
        i = 0
        while i < 100:
            data = file.read(PACKET_SIZE)
            if not data:
                break
            packets.append(packet_create(seq_num, data))
            seq_num += 1
            i += 1
    num_packets = len(packets)
    window_size = set_window_size(num_packets)




ip_add = '35.185.116.250'
port_number = 8080
udp_cleint(port_number, ip_add, p_loss=0.1, interval=10)





