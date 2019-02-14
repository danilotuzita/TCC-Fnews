# encoding: utf-8
from classes.validation import brilho
import random
import math
import numpy as np


def lplFirefly(d, n=3, gamma=1, alpha=1, beta=1, maxGenerarion=100):
    """"
    :param n: number of agents
    :param d: dimension
    :param gamma: absorption coefficient
    :param alpha: step of motion
    :param beta: attractivity factor
    :param maxGenerarion: number of max generation
    """

    t = 0
    alphat = 1.0
    bests = [0]*d
    random.seed(0)  # Reset the random generator

    fireflies = []

    # Generating the initial locations of n fireflies
    for i in range(n):
        threshold = []
        for k in range(d):
            threshold.append(random.uniform(0,1))
        threshold.sort()
        fireflies.append(threshold)

    print(fireflies)

    # Iterations or pseudo time marching
    r = []
    for i in range(n):
        lin = [0.0]*n
        r.append(lin)

    Z = [0]*n

    while t < maxGenerarion:  # Start iterations
        for i in range(n):
            Z[i] = brilho(fireflies[i])
        print("brilho", Z)

        indice = np.argsort(Z)
        Z.sort()

        Z = [-x for x in Z]

        # Ranking the fireflies by their light intensity
        rank = [0]*n
        for i in range(n):
            rank[i] = fireflies[indice[i]]

        fireflies = rank

        for i in range(n):
            for j in range(n):
                r[i][j] = dist(fireflies[i], fireflies[j])

        alphat = alpha * alphat  # Reduce randomness as iterations proceed

        # Move all fireflies to the better locations
        for i in range(n):
            threshold = []
            for j in range(n):
                if Z[i] < Z[j]:
                    for k in range(d):
                        threshold.append(random.uniform(0, 1))
                    threshold.sort()

                    betat = beta*math.exp(-gamma*((r[i][j])**2))

                    if i != n-1:

                        for k in range(d):
                            fireflies[i][k] = ((1 - betat)*fireflies[i][k] + betat*fireflies[j][k] +
                                                     alphat*threshold[k]/(1+alphat))

        print(fireflies)

        bests = fireflies[0]

        t += 1

    bests.sort()

    print("bests", bests)

    return bests


def dist(a, b):
    S = 0
    for k in range(len(a)):
        S += (b[k] - a[k]) ** 2
    S = math.sqrt(S)
    return S
