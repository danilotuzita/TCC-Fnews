# encoding: utf-8
import os
import csv
import math
import random
import numpy as np
from classes.db import DB
from classes.text import Text
from datetime import datetime
import matplotlib.pyplot as plt
from multiprocessing.dummy import Pool


class TextHandler:
    real_prob = 0  # holds the human-classificated probability
    phrases = []  # holds an array of calculated probabilities for each phrases

    def __init__(self, real_prob=0.0, phrases=()):
        self.real_prob = real_prob
        self.phrases = phrases

    def append(self, classification: float, probabilities: list):
        self.real_prob = classification
        self.phrases = probabilities

    def print(self):
        p = str(self.real_prob) + " - ["
        comma = False
        for phrase in self.phrases:
            if comma:
                p += ", "
            p += str(phrase)
            comma = True
        print(p + "]")


class DbHandler:
    texts = []  # holds an array of text handlers

    def append(self, text_handler: TextHandler):
        self.texts.append(text_handler)

    def text_count(self):
        return len(self.texts)

    def print(self):
        for th in self.texts:
            th.print()

    def get_real_prob(self):
        temp = []
        for text in self.texts:
            temp.append(text.real_prob)
        return temp

    def get_text_prob(self):
        temp = []
        for text in self.texts:
            temp2 = []
            for phrase in text.phrases:
                temp2.append(phrase)
            temp.append(temp2)
            del temp2
        return temp

    def to_file(self, path, filename):
        f = open(path + filename, 'w')
        for text in self.texts:
            f.write(str(text.real_prob) + ';')
            space = False
            for phrase in text.phrases:
                if space:
                    f.write(' ')
                f.write(str(phrase))
                space = True
            f.write('\n')
        f.close()

    def from_file(self, path, filename):
        with open(path + filename, encoding='utf-8-sig') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                phrases = []
                for phr in row[1].split(' '):
                    if phr:
                        phrases.append(float(phr))
                self.texts.append(TextHandler(float(row[0]), phrases))


# Gets the index of a cluster
def alpha_index(prob, dimension):
    ret = int(prob / (1 / dimension))
    if ret == dimension:
        return dimension - 1
    return ret


# Creates a DbHandler from a DB
def get_all_phrases_prob(data_validation_source, db: DB, phrase_size):
    dbh = DbHandler()

    print("Phrase count: ", db.query("select count(*) from phrases;"))

    with open(data_validation_source, encoding='utf-8-sig') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            txt = str.split(str.upper(row[1]))
            t = Text(txt, row[0])
            th = TextHandler()
            if t:
                t.build_phrases(phrase_size)
                phrases_prob = []
                for phrase in t.phrases:
                    phrases_prob.append(db.get_phrase_prob(phrase))

                if not len(t.phrases):  # if text has less words than phrase_size
                    phrases_prob.append(-1)

                th.append(float(t.probability), phrases_prob)
                dbh.append(th)
            del t

        return dbh


def get_used_clusters(phrase_probs, firefly_dimension, consider_not_found=0):
    not_found = 0
    used_clusters = np.zeros(firefly_dimension)
    for phrase_prob in phrase_probs:
        if phrase_prob == -1:
            not_found += 1
            if consider_not_found:
                phrase_prob = consider_not_found
            else:
                continue
        used_clusters[alpha_index(phrase_prob, firefly_dimension)] += 1

    return [normalize(used_clusters), not_found]


# Calculates the probability of a text
def calc_text_prob(text="", database=None, w_firefly=(1, 1, 1, 1, 1), phrase_size=3, consider_not_found=0):
    firefly_dimension = len(w_firefly)
    t = Text(str.split(str.upper(text)), 0)
    t.build_phrases(phrase_size)

    phrase_prob = []

    for phrase in t.phrases:
        phrase_prob.append(database.get_phrase_prob(phrase))

    [used_clusters, not_found] = get_used_clusters(phrase_prob, firefly_dimension, consider_not_found)

    used_clusters = normalize(used_clusters)
    if not len(t.phrases):
        return [-1, 0, 0]

    found_ratio = 1 - (not_found / len(t.phrases))
    # print("Found: ", len(t.phrases) - not_found, " of ", len(t.phrases), " | ", found_ratio)
    if found_ratio:
        return [calc_prob(used_clusters, w_firefly), len(t.phrases) - not_found, len(t.phrases)]
    else:
        return [-1, 0, len(t.phrases)]


# Bayesian probability calculator
def calc_prob(used_clusters=(0, 0, 0), w_firefly=(1, 1, 1)):
    firefly_dimension = len(w_firefly)
    if firefly_dimension != len(used_clusters):
        return -1

    text_prob = np.zeros(firefly_dimension)
    for i, clusters in enumerate(used_clusters):
        text_prob[i] = (1 - clusters) ** w_firefly[i]

    n = int(firefly_dimension / 2)

    false = 1 - np.prod(text_prob[:n])
    true = 1 - np.prod(text_prob[n + 1:])

    if true > false:
        return true
    return 1 - false


def brightness_evaluation(w_firefly, dbh, consider_not_found=0) -> DbHandler:
    firefly_dimension = len(w_firefly)
    total_error = 0
    for th in dbh.texts:
        used_clusters = np.zeros(firefly_dimension)

        for phrase in th.phrases:
            phrase_prob = phrase
            if phrase_prob == -1:
                if consider_not_found:
                    phrase_prob = consider_not_found
                else:
                    continue
            used_clusters[alpha_index(phrase_prob, firefly_dimension)] += 1

        used_clusters = normalize(used_clusters)
        text_prob = calc_prob(used_clusters, w_firefly)
        error = abs(th.real_prob - text_prob)
        total_error += error

    return 1 - (total_error / dbh.text_count())


# Helper function (multi-thread)
def brightness_helper(args):
    return brightness_evaluation(*args)


# Moves each firefly to it's new position
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

    return w_fireflies


# Get euclidean distance of two points
def dist(a, b):
    s = 0
    for k in range(len(a)):
        s += (b[k] - a[k]) ** 2
    return math.sqrt(s)


# Normalizes a array
def normalize(array) -> np.ndarray:
    array = np.array([np.array(item) for item in array])
    temp = array
    if isinstance(array[0], np.ndarray):
        for i, a in enumerate(array):
            temp[i] = normalize(a)
    else:
        total = sum(array)
        if total:
            normalized = []
            for i, item in enumerate(array):
                normalized.append(item / total)
            temp = normalized
    return temp


# Generates a random normalized fireflies position
def init_ff(n, d, plus_delta):
    return np.random.rand(n, d) + plus_delta


def firefly(dimension, number_fireflies=100, alpha=0.8, gamma=0.5, delta=0.95, max_generation=100, dbh=None,
            processes=0, phrase_size=3, plot=False, plus_delta=0):
    """
    :param dimension: dimension of the fireflies
    :param number_fireflies: number of agents
    :param alpha: step of motion
    :param gamma: absorption coefficient
    :param delta: Randomness reduction
    :param max_generation: number of generation
    :param dbh: DbHandler class loaded with data
    :param processes: number of threads
    :param phrase_size: number of words in a phrase
    :param plot: Print and save firefly
    :param plus_delta: firefly rand() + plus_delta
    """
    original_alpha = alpha
    best_firefly = np.zeros(dimension)  # will return this guy right here
    random.seed(datetime.now())  # Reset the random generator
    w_fireflies = init_ff(number_fireflies, dimension, plus_delta)  # Generate the fireflies (their alpha powers)
    distances = np.zeros((number_fireflies, number_fireflies))  # Distance matrix
    brightness = np.zeros(number_fireflies)  # Brightness Array

    best_brightness = []  # saves the best brightness of each generation

    for i in range(max_generation):
        start = datetime.now()

        # get brightness of generation
        if processes:  # multi-threaded brightness calculation
            args = list()
            pool = Pool(processes)
            for j in range(number_fireflies):
                args.append((w_fireflies[j], dbh))

            brightness = pool.map(brightness_helper, args)
            pool.close()
            pool.join()
        else:  # single-threaded brightness calculation
            for j in range(number_fireflies):
                brightness[j] = brightness_evaluation(w_fireflies[j], dbh)

        # sorting fireflies
        index = np.argsort(brightness)[::-1]  # best fireflies index order; brightness[index[0]] = best brightness
        brightness = np.sort(brightness)[::-1]  # ordering brightness; [0] = best brightness
        w_fireflies = w_fireflies[index]  # ordering fireflies; [0] = best firefly
        best_firefly = w_fireflies[0]  # storing the best firefly of generation
        best_brightness.append(1 - brightness[0])

        print("GENERATION " + str(i).zfill(3) + ":   " + str(best_firefly))
        print("Best Brightness:  " + str(brightness[0]))
        print("Worst Brightness: " + str(brightness[-1]))
        print("Most Bright FF:   " + str(index[0]))
        print("Processing Time:  " + str(datetime.now() - start))
        print("====")

        # loops through upper triangular matrix without its diagonal
        for row in range(number_fireflies):
            for col in range(row + 1, number_fireflies):
                distances[row][col] = dist(w_fireflies[row], w_fireflies[col])

        w_fireflies = move_fireflies(w_fireflies, brightness, distances, alpha, gamma)
        alpha *= delta

    if plot:
        # graphs setup
        plt.plot(best_brightness)
        plt.xlabel("Generation")
        plt.ylabel("1 - Brightness")
        plt.suptitle(
            'FF: ' + str(best_firefly) + "\n" +
            "alpha: " + str(original_alpha) + "; " +
            "gamma: " + str(gamma) + "; " +
            "delta: " + str(delta)
        )
        plot = str(plot)
        if os.path.isdir(plot):
            filename = str(phrase_size) + \
                datetime.now().strftime("%Y%m%d_%H%M%S") + '-' + str(max_generation) + '-' + \
                str(original_alpha) + '_' + str(gamma) + '_' + str(delta) + '.png'
            file = open(plot + filename[:-4] + '.txt', 'w')
            file.write('\n'.join(map(str, best_brightness)))
            file.close()
            plt.savefig(plot + filename)
        plt.show()
        plt.clf()

    return [best_brightness, best_firefly]
