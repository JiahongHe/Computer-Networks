from threading import Thread, Timer
from datetime import datetime
from copy import deepcopy
from collections import defaultdict
import socket
import sys
import json
import time
SIZE = 4096

SHOWRT        = "showrt"
CLOSE         = "close"
JRIP          = "jrip"
SHOWNEIGHBORS = "neighbors"

class ThreadTimer(Thread):
    """ thread that will call a function every interval seconds """
    def __init__(self, interval, target):
        Thread.__init__(self)
        self.target = target
        self.interval = interval
        self.daemon = True
        self.stopped = False
    def run(self):
        while not self.stopped:
            time.sleep(self.interval)
            self.target()

class ResettableTimer():
    def __init__(self, interval, args=None):
        if args != None: assert type(args) is list
        self.interval = interval
        self.args = args
        self.countdown = self.create_timer()
    def start(self):
        self.countdown.start()
    def reset(self):
        self.countdown.cancel()
        self.countdown = self.create_timer()
        self.start()
    def create_timer(self):
        t = Timer(self.interval, self.args)
        t.daemon = True
        return t
    def cancel(self):
        self.countdown.cancel()

def estimate_costs(nodes, node_self):
    """ recalculate inter-node path costs using bellman ford algorithm """
    for destination_addr, destination in nodes.items():
        if destination_addr != node_self:
            cost = float("inf")
            nexthop = ''
            for neighbor_addr, neighbor in get_neighbors(nodes).items():
                # distance = direct cost to neighbor + cost from neighbor to destination
                if destination_addr in neighbor['costs']:
                    dist = neighbor['direct'] + neighbor['costs'][destination_addr]
                    if dist < cost:
                        cost = dist
                        nexthop = neighbor_addr
            # set new estimated cost to node in the network
            destination['cost'] = cost
            destination['route'] = nexthop



def setup_server(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((host, port))
        print ("listening on {0}:{1}\n".format(host, port))
    except:
        print ("socket.error")
        sys.exit(1)
    return sock

def default_node():
    return { 'cost': float("inf"), 'is_neighbor': False, 'route': '' }

def formatted_now():
    return datetime.now().strftime("%b-%d-%Y, %I:%M %p, %S seconds")

def close():
    sys.exit()

def in_network(addr):
    if addr not in nodes:
        print ('node {0} not in the network\n'.format(addr))
        return False
    return True

def key_to_addr(key):
    host, port = key.split(':')
    return (host, int(port))

def addr_to_key(host, port):
    return "{host}:{port}".format(host=host, port=port)

def get_host(host):
    localhost = socket.gethostbyname(socket.gethostname())
    return localhost if host == 'localhost' else host

def get_neighbors(nodes):
    """ return dict of all neighbors (does not include self) """
    return dict([d for d in nodes.items() if d[1]['is_neighbor']])

def is_number(n):
    try:
        float(n)
        return True
    except ValueError:
        return False

def is_int(i):
    try:
        int(i)
        return True
    except ValueError:
        return False

def parse_argv():
    s = sys.argv[1:]
    parsed = {}
    # validate port
    port = s.pop(0)
    if not is_int(port):
        return { 'error': "port values must be integers. {0} is not an int.".format(port) }
    parsed['port'] = int(port)
    # validate timeout
    timeout = s.pop(0)
    if not is_number(timeout):
        return { 'error': "timeout must be a number. {0} is not a number.".format(timeout) }
    parsed['timeout'] = float(timeout)
    parsed['neighbors'] = []
    parsed['costs'] = []
    while len(s):
        if len(s) < 3:
            return { 'error': "please provide host, port, and link cost for each link." }
        host = get_host(s[0].lower())
        port = s[1]
        if not is_int(port):
            return { 'error': "port values must be integers. {0} is not an int.".format(port) }
        parsed['neighbors'].append(addr_to_key(host, port))
        cost = s[2]
        if not is_number(cost):
            return { 'error': "link costs must be numbers. {0} is not a number.".format(cost) }
        parsed['costs'].append(float(s[2]))
        del s[0:3]
    return parsed


