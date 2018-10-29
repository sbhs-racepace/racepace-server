import asyncio
from sanic import Sanic
from sanic.response import HTTPResponse
import ujson


app = Sanic('majorproject')

def json(data, status=200, headers=None):
    return HTTPResponse(
        ujson.dumps(data, indent=4), 
        status=status,
        headers=headers,
        content_type='application/json'
        )

@app.get("/")
async def index(request):
    return json({"hello": "World!"})

if __name__ == "__main__":
    app.run()