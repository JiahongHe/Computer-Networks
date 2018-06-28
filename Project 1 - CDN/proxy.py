#!/usr/bin/env python

import sys
import re
import time
import thread
import select
import socket
from utils import  *

# define constans
NUM_LOG = 15 # maximum number of pending connections in queue
MAX_DATA_RECV = 1024 # max byte/s we receive

# default parameters
PORT_DEFAULT = 8000
SERVER_IP_DEFAULT = '4.0.0.1'
FAKE_IP_DEFAULT = '1.0.0.1'
ALPHA_DEFAULT = 0.5
LOG_DEFAULT = '/home/networks/project1-starter/proxy/log1.txt '

class Proxy:

    def __init__(self):
        # initialize throughput as 0
        self.throughput_current = 0

    def get_throughtput(self, length=0, interval=100):
        return length/interval/1000

    def EWMA(self, alpha=0.5, T_current=0, T_new=0):
        if alpha<=1 and alpha>=0:
            return T_current * (1-alpha) + T_new + alpha
        else:
            return T_new

    def proxy_thread(self, connection, client_addr):
        request = connection.recv(MAX_DATA_RECV)
        request_mod = request_module(request) # if client is asking for big_buck_bunny.f4m, replace it with big_buck_bunny_nolist.f4m
        request_mod.replace_f4m()
        request_mod.throuhput_adjust(self.throughput_current)
        request_modified = request_mod.request_reconstruct()
        port = 8080
        web_server = self.server_ip
        send_time = time.time()

        try:
            s_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_out.bind((self.fake_ip, 0))
            s_out.connect((web_server, port))
            s_out.send(request_modified)
            content_len = 0
            recv_time = time.time()

            while True:
                rs, ws, es = select.select([s_out],[],[])
                data = s_out.recv(MAX_DATA_RECV)
                if len(data) > 0:
                    if len(data.split('\n')) > 1 and request_mod.request_chunk:
                        recv_time = time.time() # update receive time
                        pattern = re.compile('Content-Length:(.*)')
                        for line in data.split('\n'):
                            match = pattern.match(line)
                            if match is not None:
                                content_len = int(match.group(1).strip())
                                content_len = content_len * 8 # get content length in bits
                    connection.send(data)
                else:
                    break
            interval = recv_time - send_time
            throughput_new = self.get_throughtput(content_len, interval)
            bitrate = request_mod.get_bitrate()
            self.throughput_current = self.EWMA(self.alpha, self.throughput_current, throughput_new)

            print ('time_interval', interval)
            print ("content length:", content_len)
            print ("new throughput :", "%.2f" % throughput_new, "Kbps")
            print ("current throughput :", "%.2f" % self.throughput_current, "Kbps")

            logger = Logger(time=int(time.time()),
                            duration= '%.5f'%interval,
                            throughput='%.2f'%throughput_new,
                            throughput_avg = '%.2f' %self.throughput_current,
                            bit_rate= bitrate,
                            server_ip=self.server_ip,
                            chunk_name=request_modified.request_obj)
            logger.log(path=self.log_file)
            s_out.close()
            connection.close()
        except socket.error, (value, message):
            if s_out:
                s_out.close()
            if connection:
                connection.close()
            print ("reset")
            sys.exit(1)

    def proxy_init(self):
        # set web server ip
        if len(sys.argv)<6:
            print('no web server ip given, using default: ', SERVER_IP_DEFAULT)
            self.server_ip = SERVER_IP_DEFAULT
        else:
            self.server_ip = sys.argv[5]

        # set fake ip
        if len(sys.argv) < 5:
            print('no fake ip given, using default: ', FAKE_IP_DEFAULT)
            self.fake_ip = FAKE_IP_DEFAULT
        else:
            self.fake_ip = sys.argv[4]

        # set listen port
        if len(sys.argv) < 4:
            print('no listen port given, using default: ', PORT_DEFAULT)
            self.listen_port = PORT_DEFAULT
        else:
            self.listen_port = int(sys.argv[3])

        # set alpha
        if len(sys.argv) < 3:
            print('no alpha given, using default: ', ALPHA_DEFAULT)
            self.alpha = ALPHA_DEFAULT
        else:
            self.alpha = sys.argv[2]

        # set log file
        if len(sys.argv) < 2:
            print('no log file, using default: ', LOG_DEFAULT)
            self.log_file = LOG_DEFAULT
        else:
            self.log_file = sys.argv[1]

        host = ''
        self.host = ''
        print('proxy server runing on ', self.listen_port )
        print('log file path: ', self.log_file)

        try:
            s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            s.bind((host, self.listen_port))
            s.listen(NUM_LOG)

        except socket.error, (value, message):
            if s:
                s.close()
            print ("socket error:", message)
            sys.exit(1)

        while True:
            connection, client_addr = s.accept() # get connection from client
            client_addr = self.fake_ip # set client address
            thread.start_new_thread(self.proxy_thread, (connection, client_addr))
        s.close()

if __name__ == '__main__':
    print('proxy starts')
    proxy = Proxy()
    proxy.proxy_init()











