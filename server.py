from dataclasses import dataclass, field
import random
import string
from typing import Dict
from functools import wraps
from flask import Flask, make_response, render_template, request

from ahp_algo import AHP, Expert, group_evm

app = Flask(__name__, static_url_path="/")


@dataclass
class User:
    expert: Expert
    curr_choice: any = None


@dataclass
class Room:
    ahp: AHP = AHP()
    users: Dict[str, User] = field(default_factory=dict)


class RoomManager:
    def __init__(self) -> None:
        self.rooms: Dict[str, Room] = {}

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
            prio_choice = user.expert.get_next_cat_prio_request()
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
            user.expert.set_cat_prio_answer(*choice_args, value)
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
            return group_evm([user.expert for user in room.users.values()]).values["name"]


rooms = RoomManager()


def template_with_cookies(template_path: str):
    def inner(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)

            template = template_path
            if template:
                context, cookies = response
            else:
                template, context, cookies = response

            response = make_response(render_template(template, **context))

            for k, v in cookies.items():
                if v:
                    response.set_cookie(k, v, samesite="strict")
                else:
                    response.delete_cookie(k)

            return response

        return decorated_function

    return inner


@app.get("/")
@template_with_cookies("index.html")
def index():
    return {'notice': 'Leave code empty for a new room'}, {'name': None, 'code': None}


@app.post("/login")
@template_with_cookies(None)
def login():
    name, code = request.form.get('name'), request.form.get('code')

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


@app.post("/do")
@template_with_cookies(None)
def do_stuff():
    name, code = request.cookies['name'], request.cookies['code']
    value = float(request.form.get("value"))

    rooms.set_next_choice(code, name, value)

    choice = rooms.get_next_choice(code, name)

    if choice:
        return "chooser.html", {'room_code': code, 'option_a': choice[0], 'option_b': choice[1]}, {}
    else:
        result = rooms.get_result(code)
        if result:
            return "results.html", {"result": result}, {}
        return "waiting.html", {}, {}


@app.post("/results")
@template_with_cookies(None)
def results():
    _, code = request.cookies['name'], request.cookies['code']

    result = rooms.get_result(code)
    if result:
        return "results.html", {"result": result}, {}
    return "waiting.html", {}, {}
