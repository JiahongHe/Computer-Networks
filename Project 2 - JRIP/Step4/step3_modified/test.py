import threading
from time import sleep
import time

class my_thread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        super(my_thread, self).__init__()
        self._stop_event = threading.Event()

    def stop(self):
        print("stopping the thread")
        self._stop_event.set()

    def stopped(self):
        return(self._stop_event.is_set())

    def run(self):
        print("running the thread")
        print("start function startt()")
        self._stop_event.clear()
        self.startt()

    def startt(self):
        print("it is going to wait forever")
        while not self.stopped():
            #wait forever, this part is going to run again and again
            print('looping')
            time.sleep(1)
        print("This line never executes")


if __name__+'__main__':
    thr=my_thread()
    thr.start()
    while True:
        print('loop 2')
        sleep(1)
    print("stopping the thread")
    #thr.stop()
    # I cant start the thread and relative while loop again
    #thr.start()
    print("Exiting the whole program")