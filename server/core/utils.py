import time
import subprocess
import atexit
import os
from sanic.log import logger
import requests
import time
import random

EPOCH = 946702800

TIMESTAMP_LENGTH = 41
RANDOM_LENGTH = 23

RANDOM_SHIFT = 0
TIMESTAMP_SHIFT = 23

"""Password hashing"""

def pad_bytes_to_64(string):
    return format(string, "064b")

def binary(num, padding=True):
    """Show binary digits of a number, pads to 64 bits unless specified."""
    binary_digits = "{0:b}".format(int(num))
    if not padding:
        return binary_digits
    return pad_bytes_to_64(int(num))


def extract_bits(data, shift, length):
    """Extract a portion of a bit string. Similar to substr()."""
    bitmask = ((1 << length) - 1) << shift
    return ((data & bitmask) >> shift)


def snowflake(timestamp=None, random_bits=None, epoch=EPOCH):
    """Generate a 64 bit, roughly-ordered, globally-unique ID."""
    second_time = timestamp if timestamp is not None else time.time()
    second_time -= epoch
    millisecond_time = int(second_time * 1000)

    randomness = random.SystemRandom().getrandbits(RANDOM_LENGTH)
    randomness = random_bits if random_bits is not None else randomness

    flake = (millisecond_time << TIMESTAMP_SHIFT) + randomness

    return flake

def parse_snowflake(flake):
    """Parses a snowflake and returns a named tuple with the parts."""
    timestamp = EPOCH + extract_bits(flake, TIMESTAMP_SHIFT, TIMESTAMP_LENGTH) / 1000.0
    random = extract_bits(flake, RANDOM_SHIFT, RANDOM_LENGTH)
    return (timestamp, random)


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
