import socket
import sys

#port_number = 8080
def udp_server(port_number):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    server_address = ('localhost', port_number)
    print('starting up on %s port %s' % server_address)
    sock.bind(server_address)

    while True:
        print('\nwaiting to receive message')
        data, address = sock.recvfrom(4096)

        print('received %s bytes from %s' % (len(data), address) + '\n')
        print(data)

        if data:
            sent = sock.sendto(data, address)
            print('sent %s bytes back to %s' % (sent, address))

port_number = 8002
udp_server(port_number)