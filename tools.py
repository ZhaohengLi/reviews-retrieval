import numpy as np


def sigmoid(x):
    s = 1 / (1 + np.exp(-x))
    return s


def nan():
    for i in range(5, -4, -1):
        print(i)


if __name__ == '__main__':
    nan()
