from enum import Enum
from random import shuffle

import numpy as np


def img(s: str): return f'<img src="{s}" alt="{s.split(".")[0]}">'
def txt(s: str): return f'<div>{s}</div>'


def shuffled_range(*args):
    l = list(range(*args))
    shuffle(l)
    return l


class Category(Enum):
    PRICE = "price"
    LOCATION = "location"
    REVIEWS = "reviews"
    FOOD_TYPE = "food_type"

    def pretty(self):
        if self == Category.PRICE:
            return txt("💰 Price")
        if self == Category.LOCATION:
            return txt("🏃 Location")
        if self == Category.REVIEWS:
            return txt("⭐ Reviews")
        if self == Category.FOOD_TYPE:
            return txt("🍽️ Food Type")

    def pretty_restaurant(self, value):
        if self == Category.PRICE:
            return img(getattr(value, self.value))
        return txt(getattr(value, self.value))


class Restaurant:
    def __init__(self, name, price, location, reviews, food_type):
        self.name = name
        self.price = price
        self.location = location
        self.reviews = reviews
        self.food_type = food_type


class AHP:
    restaurants = [Restaurant("McDonalds", "mcdonalds.jpg", 1, 1, 1),
                   Restaurant("Poco Loco", "poco-loco.png", 2, 2, 2)]
    categories = [c for c in Category]


class Expert:
    def __init__(self, ahp: AHP):
        self.ahp = ahp
        self.cat_num = len(ahp.categories)
        self.res_num = len(ahp.restaurants)
        self.categories = ahp.categories
        self.restaurants = ahp.restaurants
        self.c_cat = {c: np.zeros((self.res_num, self.res_num), float)
                      for c in ahp.categories}
        self.c_prio = np.zeros((self.cat_num, self.cat_num), float)
        for c in ahp.categories:
            for i in range(self.res_num):
                self.c_cat[c][i][i] = 1
        for i in range(self.cat_num):
            self.c_prio[i][i] = 1

    def get_next_cat_request(self):
        for cat in self.ahp.categories:
            for i in shuffled_range(self.res_num):
                for j in shuffled_range(i+1, self.res_num):
                    if self.c_cat[cat][i][j] == 0:
                        return cat, self.restaurants[i], self.restaurants[j]

    def set_cat_answer(self, cat: Category, res1: Restaurant, res2: Restaurant, result):
        i = self.restaurants.index(res1)
        j = self.restaurants.index(res2)
        self.c_cat[cat][i][j] = result
        self.c_cat[cat][j][i] = 1 / result

    def get_next_prio_request(self):
        for i in shuffled_range(self.cat_num):
            for j in shuffled_range(i+1, self.cat_num):
                if self.c_prio[i][j] == 0:
                    return self.categories[i], self.categories[j]

    def set_prio_answer(self, cat1: Category, cat2: Category, result):
        i = self.categories.index(cat1)
        j = self.categories.index(cat2)
        self.c_prio[i][j] = result
        self.c_prio[j][i] = 1 / result

    def is_finished(self):
        return self.get_next_cat_request() is None and self.get_next_prio_request() is None
