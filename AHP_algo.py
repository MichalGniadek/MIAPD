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
        self.categories = ahp.categories
        self.restaurants = ahp.restaurants
        self.cat_num = len(self.categories)
        self.res_num = len(self.restaurants)
        self.c_cat = {c: np.zeros((self.res_num, self.res_num), float)
                      for c in self.categories}
        self.c_prio = np.zeros((self.cat_num, self.cat_num), float)
        for c in self.categories:
            for i in range(self.res_num):
                self.c_cat[c][i][i] = 1
        for i in range(self.cat_num):
            self.c_prio[i][i] = 1

        for r1 in range(self.res_num):
            for r2 in range(self.res_num):
                for c in self.categories:
                    v1 = self.restaurants[r1].values[c]
                    v2 = self.restaurants[r2].values[c]
                    if v1 == v2:
                        self.c_cat[c][r1][r2] = 1
                        self.c_cat[c][r2][r1] = 1
        
                    elif c == Category.LOCATION:
                        self.c_cat[c][r1][r2] = v2 / v1
                        self.c_cat[c][r2][r1] = v1 / v2

                    elif c == Category.PRICE or c == Category.REVIEWS:
                        if v1 == "low" and v2 == "high":
                            self.c_cat[c][r1][r2] = 7
                            self.c_cat[c][r2][r1] = 1/7
                        elif (v1 == "medium" and v2 == "high") or \
                             (v1 == "low" and v2 == "medium"):
                            self.c_cat[c][r1][r2] = 3
                            self.c_cat[c][r2][r1] = 1/3 


    def get_next_cat_request(self):
        for cat in self.categories:
            for i in shuffled_range(self.res_num):
                for j in shuffled_range(i+1, self.res_num):
                    if self.c_cat[cat][i][j] == 0:
                        return cat, self.restaurants[i], self.restaurants[j]

    def set_cat_answer(self, cat: Category, res1: Restaurant, res2: Restaurant, result):
        i = self.restaurants.index(res1)
        j = self.restaurants.index(res2)
        self.c_cat[cat][i][j] = result
        self.c_cat[cat][j][i] = 1 / result

    def get_next_cat_prio_request(self):
        for i in shuffled_range(self.cat_num):
            for j in shuffled_range(i+1, self.cat_num):
                if self.c_prio[i][j] == 0:
                    return self.categories[i], self.categories[j]

    def set_cat_prio_answer(self, cat1: Category, cat2: Category, result):
        i = self.categories.index(cat1)
        j = self.categories.index(cat2)
        self.c_prio[i][j] = result
        self.c_prio[j][i] = 1 / result

    def is_finished(self):
        return self.get_next_cat_request() is None and self.get_next_cat_prio_request() is None

    def all_inconstiencies(self):
        prio_CI = inconsistency_index(self.c_prio)
        cat_CIs = [inconsistency_index(cat) for cat in self.c_cat]

        return prio_CI, max(cat_CIs)

    def get_cat(self):
        return self.c_cat

    def get_prio(self):
        return self.c_prio

def inconsistency_index(arr):
    eig, _ = np.linalg.eig(arr)
    eig_max = max(abs(eig))
    n = arr.shape[0]
    CI = (eig_max  - n) / (n-1)
    return (eig_max, CI)

class Solver:
    def __init__(self, experts):
        self.experts = experts
        self.restaurants = self.experts[0].restaurants

    def eigenvalue_method(self):
        w = [1] * len(Category)
        for expert in self.experts:
            w_d1 = [ev_eig(cat) for cat in expert.get_cat()]
            w_d2 = [np.reshape(w_d1, (1, -1)) for w_ in w_d1]
            w_cat = np.concatenate(w_d2, axis=0).T
            w_prio = ev_eig(expert.get_prio())
            w *= np.dot(w_cat, w_prio)
            
        return self.restaurants[np.argmax(np.sqrt(w))] 

def ev_eig(arr):
    eig, eigv = np.linalg.eig(arr)
    i = np.argmax(abs(eig))
    wmax = abs(eigv[:, i])
    return wmax / wmax.sum()