import time
import inspect

def timed():
    def decorator(f):
        coro = inspect.iscoroutinefunction(f)

        def wrapper(*args, **kwargs):
            time1 = time.time()
            ret = f(*args, **kwargs)
            time2 = time.time()
            time_taken = (time2-time1)*1000.0
            print(f'{f.__name__:s} function took {time_taken:.3f} ms')
            return ret

        async def async_wrapper(*args, **kwargs):
            time1 = time.time()
            ret = await f(*args, **kwargs)
            time2 = time.time()
            time_taken = (time2-time1)*1000.0
            print(f'{f.__name__:s} function took {time_taken:.3f} ms')
            return ret
        
        return async_wrapper if coro else wrapper
    return decorator
