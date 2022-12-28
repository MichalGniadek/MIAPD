from sanic import Sanic
from sanic.request import Request
from inspect import isawaitable
from functools import wraps
from sanic_ext import render

app = Sanic("MIAPD")
app.static("/", "./static")


def template_with_cookies(template_path: str):
    def inner(f):
        @wraps(f)
        @app.ext.template(template_path)
        async def decorated_function(request, *args, **kwargs):
            response = f(request, *args, **kwargs)

            if isawaitable(response):
                response = await response

            if type(response) == tuple:
                context, cookies = response
            else:
                context, cookies = response, {}

            response = await render(context=context)

            for k, v in cookies.items():
                if v:
                    response.cookies[k] = v
                    response.cookies[k]["samesite"] = "Strict"
                else:
                    del response.cookies[k]

            return response

        return decorated_function

    return inner


@app.get("/")
@template_with_cookies("index.html")
async def index(_: Request):
    return {}, {'name': None, 'code': None}


@app.post("login")
@template_with_cookies("chooser.html")
async def login(rq: Request):
    name, code = rq.form.get('name'), rq.form.get('code')
    return {'option_a': 'asdasdasd asdadasdasd asd asd asd as dasd as dasdsasda', 'option_b': 'b'}, {'name': name, 'code': code}


@app.post("do")
@template_with_cookies("chooser.html")
async def do_stuff(rq: Request):
    name, code = rq.cookies['name'], rq.cookies['code']
    value = rq.form.get("value")
    return {'option_a': 'a', 'option_b': 'b'}

if __name__ == "__main__":
    app.run(dev=True)
