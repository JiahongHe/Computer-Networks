import random
import socket

DROP_PROB = 10

def udp_send(packet, sock, addr):
    if random.randint(0, DROP_PROB) > 0:
        sock.sendto(packet, addr)
    return

# Receive a packet from the unreliable channel
def udp_recv(sock):
    packet, addr = sock.recvfrom(1024)
    return packet, addr