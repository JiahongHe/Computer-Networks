import re

class Logger:

    def __init__(self, time, duration, throughput_avg, bit_rate, throughput,  server_ip, chunk_name):
        self.bit_rate = str(bit_rate)
        self.duration = str(duration)
        self.time = str(time)
        self.throughput = str(throughput)
        self.throughput_avg = str(throughput_avg)
        self.server_ip = str(server_ip)
        self.chunk_name = chunk_name

    def log(self, path):
        # write logging file
        file = path
        try:
            with open(file, 'a') as f:
                f.write('\n', self.time,' ', self.duration,' ', self.throughput,' ', self.throughput_avg,
                        ' ', self.bit_rate,' ', self.server_ip, ' ',self.chunk_name)
        except IOError as e:
            return e

class request_module:

    def __init__(self, file):
        # get the request object
        self.first_line = file.split('\n')[0]
        try:
            self.url = self.first_line.split(' ')[1]
        except:
            print ("url error")
            pass
        self.request_obj = 'N/A'
        pattern = re.compile('GET (.*) HTTP/1.1')
        for line in file.split('\n'):
            match = pattern.match(line)
            if match is not None:
                self.request_obj = match.group(1).strip()
                print('request object: ', self.request_obj)
        self.request_queue = file.split('\n')[1:]
        self.request_chunk = False

    def throuhput_adjust(self, estimated_throughput):
        # adjust throughput according to the estimated throughput
        self.get_size()
        if self.request_chunk:
            filenames = ''.join(self.request_obj.split("/")[2].split("S")[1:])
            if estimated_throughput <= 100*1.5:
                self.bitrate = str(10)
            elif estimated_throughput <= 500*1.5:
                self.bitrate = str(100)
            elif estimated_throughput <= 1000*1.5:
                self.bitrate = str(500)
            else:
                self.bitrate = str(1000)
            self.request_obj = "/vod/" + self.bitrate + "S" + filenames
            print('request object: ', self.request_obj)
            return self.bitrate

    def get_bitrate(self):
        if self.bitrate:
            return self.bitrate
        return "N/A"

    def replace_f4m(self):
        if self.request_obj == "/vod/big_buck_bunny.f4m":
            self.request_obj == "/vod/big_buck_bunny_nolist.f4m"
            print ("request object replaced :/big_buck_bunny.f4m")

    def request_reconstruct(self):
        # reconstruct the request
        self.queue_joined = '\n'.join(self.request_queue)
        self.request_reconstructed = "GET " + self.request_obj + " HTTP/1.1" + '\n' + self.queue_joined
        return self.request_reconstructed

    def get_size(self):
        if len(self.request_obj.split('/')) < 3:
            return 0
        if self.request_obj.split('/')[2].split('S')[0].isdigit():
            self.request_chunk = True
            return float(self.request_obj.split("/")[2].split("S")[0])
        return 0

    def get_url(self):
        return self.url

    def get_first_line(self):
        return self.first_line

    def get_request_object(self):
        return self.request_obj

    def get_rest_request(self):
        return self.request_queue

    def get_rest_joined(self):
        return self.queue_joined








