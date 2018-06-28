import socket
import sys
import random
import json
import time
from udp import *

l = 0.1
p = 8080
RECEIVER_ADDR = ('localhost', p)

global count
global k

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

# Receive packets from the sender
def server_receive(sock, filename):
    with open(filename, 'wb') as file:
        seq_expected = 0
        lost_count = 0

        while seq_expected<100:
            # Get the next packet from the sender
            pkt, addr = udp_recv(sock)

            seq_num, data = packet_extract(pkt)
            print('packet received', seq_num)

            # Send back an ACK
            if (random.random()) < l:
                print('packet lost' + '\n')
                lost_count += 1
            elif seq_num == seq_expected:
                print('packet received, sending ACK: ', seq_expected)
                pkt = packet_create(seq_expected)
                udp_send(pkt, sock, addr)
                seq_expected += 1
                file.write(data)
            else:
                pkt = packet_create(seq_expected - 1)
                udp_send(pkt, sock, addr)
            k = 100 - lost_count

    q = {'time': time.strftime("%a %b %d %H:%M:%S %Y", time.localtime()), 'Goodput Rate at': '%s/100' % (k),
         '160:39:142:231': '%s' % (p), 'uni:': 'jh3863'}

    with open('files/jrip2.json', 'a') as f:
        json.dump(q, f, indent=4, separators=(',', ': '))


# Main function
if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(RECEIVER_ADDR)
    filename = 'files/data_received.txt'
    server_receive(sock, filename)
    sock.close()
