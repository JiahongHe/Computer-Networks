#!/usr/bin/env python
import threading
from client import *
from server import *


def __main__():
    port_number = 8080
    ip_add = '35.185.116.250'#'localhost'
    try:
        udp_cleint(port_number, ip_add,interval=2)
        #udp_server(port_number)

    except:
        print('error')

if __name__ == "__main__":
    __main__()