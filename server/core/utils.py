import time
import inspect
from functools import wraps

def memoized(func):
    func.cache = {}
    @wraps(f)
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

