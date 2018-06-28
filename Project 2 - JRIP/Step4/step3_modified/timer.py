import time

class Timer(object):

    def __init__(self, duration):
        self.t = None
        self.start_time = self.t
        self.duration = duration

    # start the timer
    def start(self):
        if self.start_time == self.t:
            self.start_time = time.time()

    # stop the timer
    def stop(self):
        if self.start_time != self.t:
            self.start_time = self.t

    # decide if there is a timeout
    def if_timeout(self):
        if not self.if_running():
            return False
        else:
            return time.time() - self.start_time >= self.duration

    # decide if the timer is running
    def if_running(self):
        return self.start_time != self.t