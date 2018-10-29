from sanic.response import HTTPResponse
import ujson

def json(data, status=200, headers=None):
    return HTTPResponse(
        ujson.dumps(data, indent=4), 
        status=status,
        headers=headers,
        content_type='application/json'
        )