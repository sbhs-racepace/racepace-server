import time
import subprocess
import atexit
import os
from sanic.log import logger

import requests


class Snowflake:

    '''Generates a unique ID based on the Twitter Snowflake scheme'''

    epoch = 1142974214000 # Tue, 21 Mar 2006 20:50:14.000 GMT
    worker_id_bits = 5
    data_center_id_bits = 5
    max_worker_id = -1 ^ (-1 << worker_id_bits)
    max_data_center_id = -1 ^ (-1 << data_center_id_bits)
    sequence_bits = 12
    worker_id_shift = sequence_bits
    data_center_id_shift = sequence_bits + worker_id_bits
    timestamp_left_shift = sequence_bits + worker_id_bits + data_center_id_bits
    sequence_mask = -1 ^ (-1 << sequence_bits)

    def __init__(self, worker_id=1, data_center_id=1):
        self.worker_id = worker_id
        self.data_center_id = data_center_id
        self.last_timestamp = -1
        self.gen = self._generator()

    @staticmethod
    def to_timestamp(snowflake: int) -> int:
        snowflake = snowflake >> 22 
        snowflake += self.epoch    # adjust for twitter epoch
        snowflake = snowflake / 1000  # convert from milliseconds to seconds
        return snowflake

    def generate_id(self):
        return self.gen.next()

    def _generator(sleep=lambda x: time.sleep(x/1000.0)):
        assert self.worker_id >= 0 and self.worker_id <= self.max_worker_id
        assert self.data_center_id >= 0 and self.data_center_id <= self.max_data_center_id

        self.last_timestamp = -1
        sequence = 0

        while True:
            timestamp = long(time.time()*1000)

            if self.last_timestamp > timestamp:
                sleep(self.last_timestamp-timestamp)
                continue

            if self.last_timestamp == timestamp:
                sequence = (sequence + 1) & self.sequence_mask
                if sequence == 0:
                    sequence = -1 & self.sequence_mask
                    sleep(1)
                    continue
            else:
                sequence = 0

            self.last_timestamp = timestamp

            yield (
                ((timestamp-self.epoch) << self.timestamp_left_shift) |
                (data_center_id << self.data_center_id_shift) |
                (self.worker_id << self.worker_id_shift) |
                sequence
                )


def stop_ngrok(ngrok):
    logger.info('Ngrok tunnel closed.')
    ngrok.terminate()


def start_ngrok():
    '''Starts ngrok and returns the tunnel url'''
    ngrok = subprocess.Popen(['ngrok', 'http', '8000'], stdout=subprocess.PIPE)
    atexit.register(stop_ngrok, ngrok)
    time.sleep(3)
    localhost_url = "http://localhost:4040/api/tunnels"  # Url with tunnel details
    response = requests.get(localhost_url).json()
    tunnel_url = response['tunnels'][0]['public_url']  # Do the parsing of the get
    tunnel_url = tunnel_url.replace("https", "http")

    return tunnel_url

def run_with_ngrok(app):
    old_run = app.run
    def new_run(*args, **kwargs):
        app.ngrok_url = start_ngrok()
        logger.info(f'Public url @ {app.ngrok_url}')
        old_run(*args, **kwargs)
    app.run = new_run
