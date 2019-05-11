# encoding: utf-8
import csv
import math
import random
import numpy as np
from classes.db import DB
from classes.text import Text
from datetime import datetime
import matplotlib.pyplot as plt
import os
import configparser
from multiprocessing.dummy import Pool


def alpha_index(prob, dimension):
    ret = int(prob / (1 / dimension))
    if ret == dimension:
        return dimension - 1
    return ret


def brilho(data_validation_source, w_firefly, db: DB):
    firefly_dimension = len(w_firefly)
    with open(data_validation_source, encoding='utf-8-sig') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')

        total_error = 0

        alpha_error = []  # stores the alpha power error for each index
        for i in range(firefly_dimension):
            alpha_error.append([])  # creating the lists for each alpha power

        for row in csv_reader:
            t = Text(str.split(str.upper(row[1])), row[0])
            if t:
                t.build_phrases(3)
                used_alphas = []
                text_prob = 1

                for phrase in t.phrases:
                    phrase_prob = db.get_phrase_prob(phrase)
                    index = alpha_index(phrase_prob, firefly_dimension)
                    used_alphas.append(index)  # saves the index of the used alpha power
                    text_prob *= (1 - phrase_prob) ** w_firefly[index]

                error = abs(float(t.probability) - text_prob)
                total_error += error
                for alpha in used_alphas:
                    alpha_error[alpha].append(error)  # saves the error of the used alphas; it can repeat an index

                del used_alphas
                del t

        alpha_error = normalize(alpha_error)

        # TODO: verificar se é isso mesmo
        temp = []
        for alpha_cluster in alpha_error:
            if not alpha_cluster:
                temp.append(0)
            else:
                temp.append(sum(alpha_cluster) / len(alpha_cluster))
        temp = normalize(np.array(temp))
        powers = np.zeros(firefly_dimension)
        dif = abs(powers - temp) + 1
        total = sum(dif)
        s = 0

        if total:
            dif = dif / total
            for i in range(firefly_dimension):
                if dif[i]:
                    s += dif[i] * np.log(dif[i])
        return -s


def brilho_helper(args):
    return brilho(*args)


def move_fireflies(w_fireflies, brightness, distance, alpha, gamma):
    n = len(w_fireflies)
    d = len(w_fireflies[0])

    for i in range(n):
        for j in range(n):
            if brightness[j] > brightness[i]:
                beta0 = 1.0
                beta = beta0 * np.exp(-gamma * distance[i][j] ** 2)
                interference = alpha * np.random.rand(d)
                if i != j:
                    for k in range(d):
                        w_fireflies[i][k] = \
                            (1 - beta) * w_fireflies[i][k] + \
                            beta * w_fireflies[j][k] + \
                            interference[k]

    return normalize(w_fireflies)


def dist(a, b):
    s = 0
    for k in range(len(a)):
        s += (b[k] - a[k]) ** 2
    return math.sqrt(s)


def _brilho(powers, w_firefly):
    dim = len(w_firefly)
    dif = abs(powers - w_firefly) + 1
    total = sum(dif)
    s = 0

    if total:
        dif = dif / total
        for i in range(dim):
            if dif[i]:
                s += dif[i] * np.log(dif[i])
    return -s


# Normalizes a array
def normalize(array) -> np.ndarray:
    array = np.array([np.array(item) for item in array])
    temp = array
    if isinstance(array[0], np.ndarray):
        for i, a in enumerate(array):
            temp[i] = normalize(a)
    else:
        total = sum(array)
        normalized = []
        for i, item in enumerate(array):
            normalized.append(item / total)
        temp = normalized
    return temp


# Generates a random normalized firefiles position
def init_ff(n, d):
    return normalize(np.random.rand(n, d))


def firefly(dimension, number_fireflies=50, gamma=0.7, alpha=0.002, delta=0.95, max_generation=100, data_source="",
            database="", file=None, processes=0):
    if processes:
        db = []
        for i in range(processes):
            db.append(DB(database + "/", "database", debug=False, run_on_ram=database + "/database.sql"))
    else:
        db = DB(database + "/", "database", debug=False, run_on_ram=database + "/database.sql")
    """"
    :param dimension: dimension of the fireflies
    :param number_fireflies: number of agents
    :param gamma: absorption coefficient
    :param alpha: step of motion
    :param delta: Randomness reduction
    :param maxGenerarion: number of max generation
    """
    original_alpha = alpha

    best_firefly = np.zeros(dimension)  # will return this guy right here

    # random.seed(datetime.now())  # Reset the random generator
    random.seed(0)  # Reset the random generator
    w_fireflies = init_ff(number_fireflies, dimension)  # Generate the 'physical' fireflies (their alpha powers)
    distances = np.zeros((number_fireflies, number_fireflies))  # Distance matrix
    brightness = np.zeros(number_fireflies)  # Brigthness Array

    powers = np.array([0.2, 0.35, 0.15, 0.1, 0.2])
    print(w_fireflies)
    print("-----")

    best_brightness = []

    for i in range(max_generation):
        # get birghtness of generation
        if processes:
            for j in range(0, number_fireflies, processes):
                pool = Pool(processes)
                args = []
                for process in range(processes):
                    if j + process < number_fireflies:
                        args.append((data_source, w_fireflies[j], db[process]))
                results = pool.map(brilho_helper, args)
                for process in range(processes):
                    if j + process < number_fireflies:
                        brightness[j + process] = results[process]
                pool.close()
                pool.join()
        else:
            for j in range(number_fireflies):
                # brightness[j] = _brilho(powers, w_fireflies[j])
                brightness[j] = brilho(data_source, w_fireflies[j], db)

        index = np.argsort(brightness)[::-1]  # best fireflies index order; brightness[index[0]] = best brightness
        brightness = np.sort(brightness)[::-1]  # ordering brightness; [0] = best brightness
        # brightness = np.sort(-brightness)  # ordering brightness; [0] = best brightness
        w_fireflies = w_fireflies[index]  # ordering fireflies; [0] = best firefly
        best_firefly = w_fireflies[0]  # storing the best firefly of genereation

        best_brightness.append(brightness[0])
        print("GERAÇÃO " + format(i, "000") + ": " + str(best_firefly))
        print("Melhor brilho: " + str(brightness[0]))
        print("Melhor firefly: " + str(index[0]))
        print("====")

        # loops through upper triangular matrix without its diagonal
        for row in range(number_fireflies):
            for col in range(row + 1, number_fireflies):
                distances[row][col] = dist(w_fireflies[row], w_fireflies[col])

        w_fireflies = move_fireflies(w_fireflies, brightness, distances, alpha, gamma)
        alpha *= delta

    # graphs setup
    plt.plot(best_brightness)
    plt.xlabel("Gerações")
    plt.ylabel("Proximidade do padrão ouro")
    plt.suptitle(
        "alpha: " + str(original_alpha) +
        "; gamma: " + str(gamma) +
        "; delta: " + str(delta)
    )

    dif = powers - best_firefly

    plt.text(
        max_generation / 2,
        (best_brightness[0] + best_brightness[-1]) / 2,
        "Padrão ouro: " + str(powers) +
        "\nEncontrado: " + str(np.round(best_firefly, 5)) +
        "\nDiferença: " + str(np.round(dif, 5)),
        horizontalalignment='center',
        fontsize=10
    )
    filename = str(np.round(dif, 3)) + '-' + str(original_alpha) + '_' + str(gamma) + '_' + str(delta) + '.png'
    plt.savefig('../Reports/firefly/graphs/' + filename)
    # plt.show()
    if file:
        file.write(
            '"' + filename + '";' +
            '"' + str(original_alpha) + '";' +
            '"' + str(gamma) + '";' +
            '"' + str(delta) + '";' +
            '"' + str(powers) + '";' +
            '"' + str(best_firefly) + '";' +
            '"' + str(dif) + '"\n'
        )

    plt.clf()
    return best_firefly


def main():
    start = datetime.now()
    ini_filename = '../Reports/firefly/firefly.ini'

    config = configparser.ConfigParser()
    config.read(ini_filename)

    exists = os.path.isfile('../Reports/firefly/firefly.csv')

    if exists:
        file = open('../Reports/firefly/firefly.csv', mode='a')
    else:
        file = open('../Reports/firefly/firefly.csv', mode='w')
        file.write('sep=;\n')
        file.write('"firefly";"alpha";"gamma";"delta";"padrão ouro";"encontrado";"diferença"\n')

    _delta = [float(config['delta']['run']), float(config['delta']['end']), float(config['delta']['step'])]
    _gamma = [float(config['gamma']['run']), float(config['gamma']['end']), float(config['gamma']['step'])]
    _alpha = [float(config['alpha']['run']), float(config['alpha']['end']), float(config['alpha']['step'])]

    for delta in np.arange(_delta[0], _delta[1], _delta[2]):
        for gamma in np.arange(_gamma[0], _gamma[1], _gamma[2]):
            for alpha in np.arange(_alpha[0], _alpha[1], _alpha[2]):
                firefly(5, alpha=alpha, gamma=gamma, delta=delta, file=file)
                file.flush()
                os.fsync(file.fileno())
                config['delta']['run'] = str(delta)
                config['gamma']['run'] = str(gamma)
                config['alpha']['run'] = str(alpha)

                with open(ini_filename, 'w') as config_file:
                    config.write(config_file)

    file.close()

    end = datetime.now()
    print('Começou: ' + start.strftime("%H:%M:%S"))
    print('Terminou: ' + end.strftime("%H:%M:%S"))
    print('Delta: ' + str(end - start))


# main()
