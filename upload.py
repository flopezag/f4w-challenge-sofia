from config.settings import LOGLEVEL, TEMP, RAIN_GAUGE, LEVEL_METER, FILES
from processor.ngsi import NGSI
import concurrent.futures
import logging
import time


def thread_function(name):
    logging.info("Thread %s: starting", name)
    time.sleep(2)
    logging.info("Thread %s: finishing", name)


if __name__ == '__main__':
    '''
    Main: Load file(s) and upload content to Context Broker
    '''
    ngsi = NGSI(loglevel=LOGLEVEL)

    # Multithread code to send at the same time measurements from 2xsensors, 1xrain gauge, and 1 level meter
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(thread_function, range(3))

    # Read each file and upload their content into Context Broker
    ngsi.process(file=FILES[0], type=0)
