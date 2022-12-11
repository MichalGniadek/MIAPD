from sanic import Sanic
from sanic.response import text
from sanic.request import Request
from sanic.websocket import WebSocketConnection

app = Sanic("MyHelloWorldApp")


@app.get("hello")
async def hello(_: Request):
    return text("hello")


@app.websocket("api/server/connect")
async def connect(_: Request, ws: WebSocketConnection):
    async for msg in ws:
        await ws.send(msg)

if __name__ == "__main__":
    app.run()
