import time
import inspect
from functools import wraps
from threading import Timer
from pathlib import Path
import subprocess
import atexit
import platform
import os

import requests

def start_ngrok():
    '''Starts ngrok and returns the tunnel url'''
    ngrok = subprocess.Popen(['ngrok', 'http', '8000'], stdout=subprocess.PIPE)
    atexit.register(ngrok.terminate)
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
        old_run(*args, **kwargs)
    app.run = new_run

def memoized(func):
    func.cache = {}
    @wraps(func)
    async def wrapper(request):
        if str(request.json) not in func.cache:
            func.cache[request.json] = route = await func(request)
        return route
    return wrapper

def timed(f):
    """Decorator that prints out the time taken for a function to execute."""
    
    coro = inspect.iscoroutinefunction(f)

    @wraps(f)
    def wrapper(*args, **kwargs):
        time1 = time.time()
        ret = f(*args, **kwargs)
        time2 = time.time()
        time_taken = (time2-time1)*1000.0
        print(f'{f.__name__:s} function took {time_taken:.3f} ms')
        return ret

    @wraps(f)
    async def async_wrapper(*args, **kwargs):
        time1 = time.time()
        ret = await f(*args, **kwargs)
        time2 = time.time()
        time_taken = (time2-time1)*1000.0
        print(f'{f.__name__:s} function took {time_taken:.3f} ms')
        return ret
    
    return async_wrapper if coro else wrapper

