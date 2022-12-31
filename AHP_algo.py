from enum import Enum
from random import shuffle
from typing import List, Dict
import csv


import numpy as np


def shuffled_range(*args):
    l = list(range(*args))
    shuffle(l)
    return l


class BuiltinCategories(Enum):
    PRICE = "💰 Affordable"
    LOCATION = "🏃 Near"
    REVIEWS = "⭐ Well-reviewed"
    FOOD_TYPE = "🍽️ Specific Food Type"
    PHOTO = "photo"


class AHP:
    def __init__(self, file):
        with open(file, encoding='utf8') as csvfile:
            reader = csv.DictReader(
                csvfile, delimiter="|", quotechar="\"", quoting=csv.QUOTE_NONNUMERIC)

            self.categories = list(reader.fieldnames)[1:]
            self.restaurants = list(reader)


class Expert:
    def __init__(self, ahp: AHP):
        if not ahp:
            return
        self.categories: List[str] = ahp.categories
        self.restaurants: List[Dict] = ahp.restaurants
        self.cat_num = len(self.categories)
        self.res_num = len(self.restaurants)
        self.cat_mat = {c: np.zeros((self.res_num, self.res_num), float)
                        for c in self.categories}
        self.prio_mat = np.zeros((self.cat_num, self.cat_num), float)

        for i in range(self.cat_num):
            self.prio_mat[i][i] = 1

        for i in range(self.cat_num):
            # -1 is photo category index
            self.prio_mat[-1][i] = 1
            self.prio_mat[i][-1] = 1

        for r1 in range(self.res_num):
            for r2 in range(r1, self.res_num):
                for c in self.categories:
                    v1 = self.restaurants[r1][c]
                    v2 = self.restaurants[r2][c]
                    if v1 == v2:
                        self.cat_mat[c][r1][r2] = 1
                        self.cat_mat[c][r2][r1] = 1

                    elif c == BuiltinCategories.LOCATION.value:
                        self.cat_mat[c][r1][r2] = v2 / v1
                        self.cat_mat[c][r2][r1] = v1 / v2

                    elif c == BuiltinCategories.PRICE.value:
                        table = {
                            ("low", "high"): 5,
                            ("low", "medium"): 3,
                            ("medium", "high"): 3,
                            ("high", "low"): 1/5,
                            ("medium", "low"): 1/3,
                            ("high", "medium"): 1/3,
                        }
                        if (v1, v2) in table:
                            self.cat_mat[c][r1][r2] = table[(v1, v2)]
                            self.cat_mat[c][r2][r1] = 1/table[(v1, v2)]
                    elif c == BuiltinCategories.REVIEWS.value:
                        table = {
                            ("low", "high"): 1/5,
                            ("low", "medium"): 1/3,
                            ("medium", "high"): 1/3,
                            ("high", "low"): 5,
                            ("medium", "low"): 3,
                            ("high", "medium"): 3,
                        }
                        if (v1, v2) in table:
                            self.cat_mat[c][r1][r2] = table[(v1, v2)]
                            self.cat_mat[c][r2][r1] = 1/table[(v1, v2)]

    def get_next_cat_request(self):
        for cat in self.categories:
            for i in shuffled_range(self.res_num):
                for j in shuffled_range(i+1, self.res_num):
                    if self.cat_mat[cat][i][j] == 0:
                        return cat, self.restaurants[i], self.restaurants[j]

    def set_cat_answer(self, cat: str, res1: Dict, res2: Dict, result: float) -> None:
        v1, v2 = res1[cat], res2[cat]

        for i in range(self.res_num):
            for j in range(self.res_num):
                if self.restaurants[i][cat] == v1 and self.restaurants[j][cat] == v2:
                    self.cat_mat[cat][i][j] = result
                    self.cat_mat[cat][j][i] = 1 / result

    def get_next_cat_prio_request(self):
        for i in shuffled_range(self.cat_num):
            for j in shuffled_range(i+1, self.cat_num):
                if self.prio_mat[i][j] == 0:
                    return self.categories[i], self.categories[j]

    def set_cat_prio_answer(self, cat1: str, cat2: str, result: float) -> None:
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
