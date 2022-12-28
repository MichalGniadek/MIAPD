from enum import Enum

import numpy as np


class Category(Enum):
    PRICE = "price",
    LOCATION = "location"
    REVIEWS = "reviews"
    FOOD_TYPE = "type"


class Restaurant:
    def __init__(self, name, price, location, reviews, food_type):
        self.name = name
        self.price = price
        self.location = location
        self.reviews = reviews
        self.food_type = food_type


class AHP:
    restaurants = []
    categories = [c for c in Category]


class Expert:
    def __init__(self, ahp: AHP):
        self.cat_num = len(ahp.categories)
        self.res_num = len(ahp.restaurants)
        self.categories = ahp.categories
        self.restaurants = ahp.restaurants
        self.c_cat = {c: np.zeros((self.res_num, self.res_num), int)
                      for c in ahp.categories}
        self.c_prio = np.zeros((self.cat_num, self.cat_num), int)
        for c in ahp.categories:
            for i in range(self.res_num):
                self.c_cat[c][i][i] = 1
        for i in range(self.cat_num):
            self.c_prio[i][i] = 1

    def get_next_cat_request(self, cat: Category):
        for i in range(self.res_num):
            for j in range(i+1, self.res_num):
                if self.c_cat[cat][i][j] == 0:
                    return cat, (self.restaurants[i], self.restaurants[j])

        return cat, (None, None)

    def set_cat_answer(self, cat: Category, res1: Restaurant, res2: Restaurant, result):
        i = self.restaurants.index(res1)
        j = self.restaurants.index(res2)
        self.c_cat[cat][i][j] = result
        self.c_cat[cat][j][i] = 1 / result

    def get_next_prio_request(self):
        for i in range(self.cat_num):
            for j in range(i+1, self.cat_num):
                if self.c_prio[i][j] == 0:
                    return self.categories[i], self.categories[j]

    def set_prio_answer(self, cat1: Category, cat2: Category, result):
        i = self.categories.index(cat1)
        j = self.categories.index(cat2)
        self.c_prio[i][j] = result
        self.c_prio[j][i] = 1 / result
