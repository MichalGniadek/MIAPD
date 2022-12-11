from sanic import Sanic
from sanic.response import text

app = Sanic("MyHelloWorldApp")


@app.route('/')
@app.route('/<path:path>')
async def index(request, path=""):
    return text(path)
