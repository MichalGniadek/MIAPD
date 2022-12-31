import numpy as np

arr = np.array([
    [1, 7, 1/6, 1/2, 1/4, 1/6, 4],
    [1/7, 1, 1/3, 5, 1/5, 1/7, 5],
    [6, 3, 1, 6, 3, 2, 8],
    [2, 1/5, 1/6, 1, 8, 1/5, 8],
    [4, 5, 1/3, 1/8, 1, 1/9, 2],
    [6, 7, 1/2, 5, 9, 1, 2],
    [1/4, 1/5, 1/8, 1/8, 1/2, 1/2, 1],
])

eig, _ = np.linalg.eig(arr)

eig_max = max(abs(eig))

n = arr.shape[0]

CI = (eig_max - n) / (n-1)

print(eig_max, CI)

arr = np.array([
    [1, 2, 3],
    [1/2, 1, 4],
    [1/3, 1/4, 1]
])

eig, eigv = np.linalg.eig(arr)
i = np.argmax(eig)
wmax = abs(eigv[:, i])
wmax /= wmax.sum()

print(wmax)
