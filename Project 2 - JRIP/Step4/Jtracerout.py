import sys, socket, json, time


def key_to_addr(key):
    host, port = key.split(':')
    return (host, int(port))

def addr_to_key(host, port):
    return "{host}:{port}".format(host=host, port=port)

def get_host(host):
    localhost = socket.gethostbyname(socket.gethostname())
    return localhost if host == 'localhost' else host

def addr_to_key(host, port):
    return "{host}:{port}".format(host=host, port=port)

def get_host(host):
    localhost = socket.gethostbyname(socket.gethostname())
    return localhost if host == 'localhost' else host

if __name__ == '__main__':

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    host_ori = 'localhost'
    host = get_host(host_ori)
    port_origin = input('port_origin: ')
    sock.bind((host, int(port_origin)))
    addr_origin = host + ':' + str(port_origin)
    addr_designated = input('addr_designated: ')
    addr_designated_a, addr_designated_port = key_to_addr(addr_designated)
    addr_designated_a = get_host(addr_designated_a)
    addr_designated = addr_to_key(addr_designated_a, addr_designated_port)
    addr_destination = input('addr_destination: ')
    addr_destination_a, addr_destination_port = key_to_addr(addr_designated)
    addr_destination_a = get_host(addr_destination_a)
    addr_destination = addr_to_key(addr_destination_a, addr_destination_port)

    data = {}
    Data = {}
    data['uni'] = 'jh3863'
    Data['Type'] = 'TRACE'
    Data["Destination"] = addr_destination
    data['Data'] = Data
    print('starting up on: ', (host, addr_origin))
    loaded = json.dumps(data)
    print("packet: ", loaded)
    for i in range(0, 50):
        sock.sendto(loaded.encode('utf-8'), key_to_addr(addr_designated))
        print('trace packet sent to: ' + addr_designated)
        try:
            print('waiting for traceback file... ')
            data, address = sock.recvfrom(4096)
            if data:
                print('tracroute file received')
                writeup = json.loads(data)
                print('TRACE')
                for trace in writeup['Data']['Trace']:
                    print(trace)
                with open('files/traceroute.json', 'w') as f:
                    json.dump(writeup, f, indent=4, separators=(',', ': '))
            break

        except socket.timeout:
            print('timeout, Trying again...')
            continue

'''
            
    if addr_origin == 'test':
        data = {}
        Data = {}
        addr_origin = '192.168.0.4:8080'
        addr_designated = '192.168.0.4:8003'
        data['uni'] = 'jh3863'
        Data['Type'] = 'TRACE'
        Data["Destination"] = '192.168.0.4:8005'
        Data['Origin'] = addr_origin
        Data['Trace'] = []
        data['Data'] = Data
        print('starting up on: ', (host, port))
        loaded = json.dumps(data)
        print("packet: ", loaded)
        sock.sendto(loaded.encode('utf-8'), key_to_addr(addr_designated))
        print('trace packet sent to: ' + addr_designated)
'''