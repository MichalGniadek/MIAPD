import numpy as np
from numpy.testing import assert_allclose

from AHP_algo import Expert, evm, hierarchical_evm, inconsistency_index


def test_inconsistency_index():
    arr = np.array([
        [1, 7, 1/6, 1/2, 1/4, 1/6, 4],
        [1/7, 1, 1/3, 5, 1/5, 1/7, 5],
        [6, 3, 1, 6, 3, 2, 8],
        [2, 1/5, 1/6, 1, 8, 1/5, 8],
        [4, 5, 1/3, 1/8, 1, 1/9, 2],
        [6, 7, 1/2, 5, 9, 1, 2],
        [1/4, 1/5, 1/8, 1/8, 1/2, 1/2, 1],
    ])

    result = inconsistency_index(arr)

    assert result == 0.7057317509943074


def test_evm():
    arr = np.array([
        [1, 2, 3],
        [1/2, 1, 4],
        [1/3, 1/4, 1]
    ])

    result = evm(arr)

    assert_allclose(result, [0.51713362, 0.35856042, 0.12430596])


def test_hierarchical_evm():
    expert = Expert(None)
    expert.cat_mat = {
        "1": np.array([
            [1, 1/7, 1/5],
            [7, 1, 3],
            [5, 1/3, 1],
        ]),
        "2": np.array([
            [1, 5, 9],
            [1/5, 1, 4],
            [1/9, 1/4, 1],
        ]),
        "3": np.array([
            [1, 4, 1/5],
            [1/4, 1, 1/9],
            [5, 9, 1],
        ]),
        "4": np.array([
            [1, 9, 4],
            [1/9, 1, 1/4],
            [1/4, 4, 1],
        ]),
        "5": np.array([
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
        ]),
        "6": np.array([
            [1, 6, 4],
            [1/6, 1, 1/3],
            [1/4, 3, 1],
        ]),
        "7": np.array([
            [1, 9, 6],
            [1/9, 1, 1/3],
            [1/6, 3, 1],
        ]),
        "8": np.array([
            [1, 1/2, 1/2],
            [2, 1, 1],
            [2, 1, 1],
        ]),
    }
    expert.prio_mat = [
        [1, 4, 7, 5, 8, 6, 6, 2],
        [1/4, 1, 5, 3, 7, 6, 6, 1/3],
        [1/7, 1/5, 1, 1/3, 5, 3, 3, 1/5],
        [1/5, 1/3, 3, 1, 6, 3, 4, 1/2],
        [1/8, 1/7, 1/5, 1/6, 1, 1/3, 1/4, 1/7],
        [1/6, 1/6, 1/3, 1/3, 3, 1, 1/2, 1/5],
        [1/6, 1/6, 1/3, 1/4, 4, 2, 1, 1/5],
        [1/2, 3, 5, 2, 7, 5, 5, 1]
    ]

    result = hierarchical_evm(expert)

    assert_allclose(result, [0.34634713, 0.36914035, 0.28451251])
