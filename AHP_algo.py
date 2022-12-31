from enum import Enum
from random import shuffle
from typing import List

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

    def pretty_restaurant(self, restaurant: "Restaurant"):
        if False:  # for future
            return img(restaurant[self.value])
        return txt(restaurant.values[self])


class Restaurant:
    def __init__(self, name, price, location, reviews, food_type):
        self.values = {"name": name,
                       Category.PRICE: price,
                       Category.LOCATION: location,
                       Category.REVIEWS: reviews,
                       Category.FOOD_TYPE: food_type}


class AHP:
    categories = [c for c in Category]

    def __init__(self):
        self.restaurants = self.mock_data()

    def mock_data(self):
        mc_donald = Restaurant("McDonald", "low", 1, "low", "fast food")
        kawiory = Restaurant("Kawiory", "low", 0.8, "medium", "polish food")
        zaczek = Restaurant("Zaczek", "low", 0.5, "low", "polish food")
        laila = Restaurant("Laila", "medium", 0.2, "high", "vegetarian")
        sushi77 = Restaurant("Sushi 77", "high", 1, "high", "sushi")
        studio = Restaurant("Studio", "medium", 1.5, "high", "fast food")

        return [mc_donald, kawiory, zaczek, laila, sushi77, studio]


class Expert:
    def __init__(self, ahp: AHP):
        if not ahp:
            return
        self.categories = ahp.categories
        self.restaurants = ahp.restaurants
        self.cat_num = len(self.categories)
        self.res_num = len(self.restaurants)
        self.cat_mat = {c: np.zeros((self.res_num, self.res_num), float)
                        for c in self.categories}
        self.prio_mat = np.zeros((self.cat_num, self.cat_num), float)

        for i in range(self.cat_num):
            self.prio_mat[i][i] = 1

        for r1 in range(self.res_num):
            for r2 in range(r1, self.res_num):
                for c in self.categories:
                    v1 = self.restaurants[r1].values[c]
                    v2 = self.restaurants[r2].values[c]
                    if v1 == v2:
                        self.cat_mat[c][r1][r2] = 1
                        self.cat_mat[c][r2][r1] = 1

                    elif c == Category.LOCATION:
                        self.cat_mat[c][r1][r2] = v2 / v1
                        self.cat_mat[c][r2][r1] = v1 / v2

                    elif c == Category.PRICE or c == Category.REVIEWS:
                        if v1 == "low" and v2 == "high":
                            self.cat_mat[c][r1][r2] = 5
                            self.cat_mat[c][r2][r1] = 1/5
                        elif (v1 == "medium" and v2 == "high") or \
                             (v1 == "low" and v2 == "medium"):
                            self.cat_mat[c][r1][r2] = 3
                            self.cat_mat[c][r2][r1] = 1/3

    def get_next_cat_request(self):
        for cat in self.categories:
            for i in shuffled_range(self.res_num):
                for j in shuffled_range(i+1, self.res_num):
                    if self.cat_mat[cat][i][j] == 0:
                        return cat, self.restaurants[i], self.restaurants[j]

    def set_cat_answer(self, cat: Category, res1: Restaurant, res2: Restaurant, result):
        i = self.restaurants.index(res1)
        j = self.restaurants.index(res2)
        self.cat_mat[cat][i][j] = result
        self.cat_mat[cat][j][i] = 1 / result

    def get_next_cat_prio_request(self):
        for i in shuffled_range(self.cat_num):
            for j in shuffled_range(i+1, self.cat_num):
                if self.prio_mat[i][j] == 0:
                    return self.categories[i], self.categories[j]

    def set_cat_prio_answer(self, cat1: Category, cat2: Category, result):
        i = self.categories.index(cat1)
        j = self.categories.index(cat2)
        self.prio_mat[i][j] = result
        self.prio_mat[j][i] = 1 / result

    def is_finished(self):
        return self.get_next_cat_request() is None and self.get_next_cat_prio_request() is None

    def all_inconsistencies(self):
        prio_CI = inconsistency_index(self.prio_mat)
        cat_CIs = [inconsistency_index(cat) for cat in self.cat_mat]

        return prio_CI, max(cat_CIs)

    def get_cat(self):
        return self.cat_mat

    def get_prio(self):
        return self.prio_mat


def inconsistency_index(arr):
    eig, _ = np.linalg.eig(arr)
    eig_max = max(abs(eig))
    n = arr.shape[0]
    ci = (eig_max - n) / (n-1)
    return ci


def evm(mat):
    eig, eigv = np.linalg.eig(mat)
    i = np.argmax(abs(eig))
    wmax = abs(eigv[:, i])
    return wmax / wmax.sum()


def hierarchical_evm(expert: Expert):
    cat_mats = expert.get_cat().values()
    w_cat = np.array([evm(mat) for mat in cat_mats])
    w_prio = evm(expert.get_prio())
    return np.dot(w_cat.T, w_prio)


def group_evm(experts: List[Expert]):
    restaurants = experts[0].restaurants
    n = len(restaurants)

    w = [1] * n
    for expert in experts:
        w *= hierarchical_evm(expert)
    w **= 1/n

    return restaurants[np.argmax(w)]
