import asyncio
import functools
from functools import wraps
from sanic.exceptions import abort
import time

def jsonrequired(func):
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        if request.json is None:
            abort(400, 'Request must have a json body.')
        return await func(request, *args, **kwargs)
    return wrapper

async def validate_token(request):
    if request.token == 'ADMIN_TOKEN':
        return True
    exists = await request.app.db.users.find_one({
            'credentials.token': request.token.encode('ascii')
            })
    return bool(exists)

def authrequired(func):
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        if not request.token or not await validate_token(request):
            abort(401, "Invalid token")
        return await func(request, *args, **kwargs)
    return wrapper

def memoized(func):
    func.cache = {}

    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        key = str(request.json)
        if key not in func.cache:
            func.cache[key] = await func(request, *args, **kwargs)
        return func.cache[key]

    return wrapper

def asyncexecutor(_func=None, *, loop=None, executor=None):
    _loop = loop or asyncio.get_event_loop()

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            partial = functools.partial(func, *args, **kwargs)
            return _loop.run_in_executor(executor, partial)
        return wrapper
    
    if _func is None: # @asyncexecutor()
        return decorator
    else: # @asyncexecutor
        return decorator(_func)

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
