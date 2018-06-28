import sys, socket, json, time
from select import select
from collections import defaultdict, namedtuple
from func_utils import *
from copy import deepcopy

SIZE = 4096

def address_rebuild(addr):
    address = addr.split(':')
    addr = address[0]
    port_designated = int(address[1])
    return ((addr, port_designated))

def showrt():
    """ display routing info: cost to destination; route to take """
    print(formatted_now())
    print("Distance vector list is:")
    for addr, node in nodes.items():
        if addr != node_self:
            print("DESTINATION = {}, DISTANCE = {}, NEXTHOP = ({})".format(addr,node['cost'],node['route']))
    print ('\n')

def print_nodes():
    print ("nodes: ")
    for addr, node in nodes.items():
        print (addr)
        for k,v in node.items():
            print ('---- ', k, '\t\t', v)
    print ("\n")

def broadcast_costs():
    # send estimated path costs to neighbors
    costs = { addr: node['cost'] for addr, node in nodes.items() }
    data = { 'type': JRIP }
    for neighbor_addr, neighbor in get_neighbors(nodes).items():
        poisoned_costs = deepcopy(costs)
        for dest_addr, cost in costs.items():
            if dest_addr not in [node_self, neighbor_addr]:
                if nodes[dest_addr]['route'] == neighbor_addr:
                    poisoned_costs[dest_addr] = float("inf")
        data['Data'] = { 'costs': poisoned_costs }
        data['Data']['neighbor'] = { 'direct': neighbor['direct'] }
        packet = json.dumps(data)
        sock.sendto(packet.encode('utf-8'), key_to_addr(neighbor_addr))

def create_node(cost, is_neighbor, direct=None, costs=None, addr=None):
    # create new node
    node = default_node()
    node['cost'] = cost
    node['is_neighbor'] = is_neighbor
    node['direct'] = direct if direct != None else float("inf")
    node['costs']  = costs  if costs  != None else defaultdict(lambda: float("inf"))
    if is_neighbor:
        node['route'] = addr
        monitor = ResettableTimer(
            interval = 3*run_args.timeout,
            args = list(key_to_addr(addr)))
        monitor.start()
        node['silence_monitor'] = monitor
    return node

def show_neighbors():
    """ show active neighbors """
    print (formatted_now())
    print ("Neighbors: ")
    for addr, neighbor in get_neighbors(nodes).items():
        print ("{addr}, cost:{cost}, direct:{direct}".format(
                addr   = addr,
                cost   = neighbor['cost'],
                direct = neighbor['direct']))
    print ('\n')



def update_costs(host, port, **kwargs):
    # update neighbor's costs
    costs = kwargs['costs']
    addr = addr_to_key(host, port)
    # if a node listed in costs is not in the list of nodes
    for node in costs:
        if node not in nodes:
            # create a new node
            nodes[node] = default_node()
    # if node not a neighbor
    if not nodes[addr]['is_neighbor']:
        print ('making new neighbor {0}\n'.format(addr))
        del nodes[addr]
        nodes[addr] = create_node(
                cost        = nodes[addr]['cost'],
                is_neighbor = True,
                direct      = kwargs['neighbor']['direct'],
                costs       = costs,
                addr        = addr)
    else:
        # otherwise just update node costs
        node = nodes[addr]
        node['costs'] = costs
        # restart silence monitor
        node['silence_monitor'].reset()
    # run bellman ford
    estimate_costs(nodes, node_self)

updates = {
    "jrip": update_costs,
}

user_cmds = {
    SHOWRT     : showrt,
    CLOSE      : close,
    SHOWNEIGHBORS : show_neighbors}

def parse_user_input(user_input):
    # parse user input
    parsed = { 'addr': (), 'Data': {} }
    user_input = user_input.split()
    if not len(user_input):
        return { 'error': "please provide a command\n" }
    cmd = user_input[0].lower()
    # verify cmd is valid
    if cmd not in user_cmds:
        return { 'error': "'{0}' is not a valid command\n".format(cmd) }
    parsed['cmd'] = cmd
    return parsed



if __name__ == '__main__':
    localhost = socket.gethostbyname(socket.gethostname())
    parsed = parse_argv()
    if 'error' in parsed:
        print (parsed['error'])
        sys.exit(1)
    RunArgs = namedtuple('RunInfo', 'port timeout neighbors costs')
    run_args = RunArgs(**parsed)
    # initialize dict of nodes to all neighbors
    nodes = defaultdict(lambda: default_node())
    for neighbor, cost in zip(run_args.neighbors, run_args.costs):
        nodes[neighbor] = create_node(cost=cost, direct=cost, is_neighbor=True, addr=neighbor)
    # begin accepting UDP packets
    sock = setup_server(localhost, run_args.port)
    # set cost to myself to 0
    node_self = addr_to_key(*sock.getsockname())
    nodes[node_self] = create_node(cost=0.0, direct=0.0, is_neighbor=False, addr=node_self)
    broadcast_costs()
    ThreadTimer(run_args.timeout, broadcast_costs).start()
    thr = my_thread(sock, nodes, node_self)
    thr.start()
    # listen for updates from other nodes and user input
    inputs = [sock, sys.stdin]
    running = True
    while running:
        in_ready, out_ready, except_ready = select(inputs,[],[])
        for s in in_ready:
            if s == sys.stdin:
                # user input command
                parsed = parse_user_input(sys.stdin.readline())
                if 'error' in parsed:
                    print (parsed['error'])
                    continue
                cmd = parsed['cmd']
                user_cmds[cmd](*parsed['addr'], **parsed['Data'])
            else:
                try:
                    # update from another node
                    data, sender = s.recvfrom(SIZE)
                    loaded = json.loads(data)
                    update = loaded['type']
                    payload = loaded['Data']
                    if update not in updates:
                        print("'{}' is not in the update protocol\n".format(update))
                        continue
                    updates[update](*sender, **payload)
                except:
                    print('route yet unknown, please try again')
                    continue

    sock.close()



