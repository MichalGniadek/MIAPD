from sanic import Sanic
from sanic.response import html
from sanic.request import Request
from sanic.websocket import WebSocketConnection

app = Sanic("MyHelloWorldApp")
# with open("choice.html", encoding='utf-8') as f:
#     app.choice_html = f.read()
# print(app.choice_html)


# @app.get("/api/server")
# async def index(_: Request):
#     return html(app.choice_html)


@app.websocket("api/server/connect")
async def connect(_: Request, ws: WebSocketConnection):
    async for msg in ws:
        await ws.send(msg)

if __name__ == "__main__":
    app.run()
