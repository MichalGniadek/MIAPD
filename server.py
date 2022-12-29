import array
from dataclasses import dataclass, field
import random
import string
from sys import argv
from sanic import Sanic
from sanic.request import Request
from inspect import isawaitable
from functools import wraps
from sanic_ext import render

from AHP_algo import AHP, Expert

app = Sanic("MIAPD")
app.static("/", "./static")


@dataclass
class User:
    expert: Expert
    curr_choice: any = None


@dataclass
class Room:
    ahp: AHP = AHP()
    users: dict[str, User] = field(default_factory=dict)


class RoomManager:
    def __init__(self) -> None:
        self.rooms: dict[str, Room] = {}

    def random_key() -> str:
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

    def new_room(self) -> str:
        key = RoomManager.random_key()

        while key in self.rooms:
            key = RoomManager.random_key()

        self.rooms[key] = Room()

        return key

    def add_user(self, code: str, name: str):
        if code in self.rooms:
            ahp = self.rooms[code].ahp
            if name not in self.rooms[code].users:
                self.rooms[code].users[name] = User(Expert(ahp))
                return True
        return False

    def get_next_choice(self, code: str, name: str):
        user = self.rooms[code].users[name]

        def try_get_prio():
            prio_choice = user.expert.get_next_prio_request()
            if prio_choice:
                user.curr_choice = "prio", prio_choice
                return prio_choice[0].pretty(), prio_choice[1].pretty()

        def try_get_cat():
            cat_choice = user.expert.get_next_cat_request()
            if cat_choice:
                user.curr_choice = "cat", cat_choice
                return cat_choice[0].pretty_restaurant(cat_choice[1]), cat_choice[0].pretty_restaurant(cat_choice[2])

        if random.choice([True, False]):
            return try_get_prio() or try_get_cat()
        else:
            return try_get_cat() or try_get_prio()

    def set_next_choice(self, code: str, name: str, value):
        user = self.rooms[code].users[name]

        choice_type, choice_args = user.curr_choice
        if choice_type == "prio":
            user.expert.set_prio_answer(*choice_args, value)
        elif choice_type == "cat":
            user.expert.set_cat_answer(*choice_args, value)
        else:
            raise ValueError(f"Incorrect choice_type {choice_type}")

    def get_result(self, code: str):
        room = self.rooms[code]

        for user in room.users.values():
            if not user.expert.is_finished():
                break
        else:
            return "McDonalds"


rooms = RoomManager()


def template_with_cookies(template_path: str):
    def inner(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            response = f(request, *args, **kwargs)

            if isawaitable(response):
                response = await response

            template = template_path
            if template:
                context, cookies = response
            else:
                template, context, cookies = response

            response = await render(template, context=context)

            for k, v in cookies.items():
                if v:
                    response.cookies[k] = v
                    response.cookies[k]["samesite"] = "strict"
                else:
                    del response.cookies[k]

            return response

        return decorated_function

    return inner


@app.get("/")
@template_with_cookies("index.html")
async def index(_: Request):
    return {'notice': 'Leave code empty for a new room'}, {'name': None, 'code': None}


@app.post("login")
@template_with_cookies(None)
async def login(rq: Request):
    name, code = rq.form.get('name'), rq.form.get('code')

    if not code:
        code = rooms.new_room()
    else:
        code = code.upper()

    if rooms.add_user(code, name):
        a, b = rooms.get_next_choice(code, name)

        return (
            "chooser.html",
            {
                'room_code': code,
                'option_a': a,
                'option_b': b
            },
            {'name': name, 'code': code}
        )
    else:
        return "login.html", {'notice': 'Invalid room code!'}, {}


@app.post("do")
@template_with_cookies(None)
async def do_stuff(rq: Request):
    name, code = rq.cookies['name'], rq.cookies['code']
    value = float(rq.form.get("value"))

    rooms.set_next_choice(code, name, value)

    choice = rooms.get_next_choice(code, name)

    if choice:
        return "chooser.html", {'room_code': code, 'option_a': choice[0], 'option_b': choice[1]}, {}
    else:
        result = rooms.get_result(code)
        if result:
            return "results.html", {"result": result}, {}
        return "waiting.html", {}, {}


@app.post("results")
@template_with_cookies(None)
async def results(rq: Request):
    _, code = rq.cookies['name'], rq.cookies['code']

    result = rooms.get_result(code)
    if result:
        return "results.html", {"result": result}, {}
    return "waiting.html", {}, {}

if __name__ == "__main__":
    dev = True
    if len(argv) == 2 and argv[1] == "prod":
        dev = False
    app.run(dev=dev)
