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
        f = open(path + '/' + filename, 'w')
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
        with open(path + '/' + filename, encoding='utf-8-sig') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                phrases = []
                for phr in row[1].split(' '):
                    if phr:
                        phrases.append(float(phr))
                self.texts.append(TextHandler(float(row[0]), phrases))


def alpha_index(prob, dimension):
    ret = int(prob / (1 / dimension))
    if ret == dimension:
        return dimension - 1
    return ret


def get_all_phrases_prob(data_validation_source, db: DB, phrase_size):
    dbh = DbHandler()

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

                th.append(float(t.probability), phrases_prob)
                dbh.append(th)
            del t

        return dbh


def calc_text_prob(text="", database=None, w_firefly=(1, 1, 1, 1, 1), phrase_size=3, consider_not_found=0):
    firefly_dimension = len(w_firefly)
    used_clusters = np.zeros(firefly_dimension)
    t = Text(str.split(str.upper(text)), 0)
    t.build_phrases(phrase_size)

    not_found = 0

    for phrase in t.phrases:
        phrase_prob = database.get_phrase_prob(phrase)
        if phrase_prob == -1:
            not_found += 1
            if consider_not_found:
                phrase_prob = consider_not_found
            else:
                continue
        used_clusters[alpha_index(phrase_prob, firefly_dimension)] += 1

    used_clusters = normalize(used_clusters)
    if not len(t.phrases):
        return -1

    found_ratio = 1 - (not_found / len(t.phrases))
    # print("Found: ", len(t.phrases) - not_found, " of ", len(t.phrases), " | ", found_ratio)
    if found_ratio:
        return [calc_prob(used_clusters, w_firefly), len(t.phrases) - not_found, len(t.phrases)]
    else:
        return [-1, 0, len(t.phrases)]


def calc_prob(used_clusters=(0, 0, 0), w_firefly=(1, 1, 1)):
    firefly_dimension = len(w_firefly)
    if firefly_dimension != len(used_clusters):
        return -1

    text_prob = 1
    # print(used_clusters)
    for i, clusters in enumerate(used_clusters):
        if i >= firefly_dimension / 2:
            text_prob *= (1 - clusters) ** (1 - w_firefly[i])
        else:
            text_prob *= (1 - clusters) ** w_firefly[i]

    return 1 - text_prob


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


def brightness_helper(args):
    return brightness_evaluation(*args)


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
def init_ff(n, d):
    return normalize(np.random.rand(n, d))


def firefly(dimension, number_fireflies=100, alpha=0.8, gamma=0.5, delta=0.95, max_generation=100, data_source="",
            database_path="", file=None, processes=0, dbh=None, phrase_size=3):
    """"
    :param dimension: dimension of the fireflies
    :param number_fireflies: number of agents
    :param alpha: step of motion
    :param gamma: absorption coefficient
    :param delta: Randomness reduction
    :param max_generation: number of generation
    :param data_source: csv file to compare
    :param database_path: sql file to load database
    :param file: file to write some data
    :param processes: number of threads
    :param dbh: DbHandler class loaded with data
    :param phrase_size: number of words in a phrase
    """
    original_alpha = alpha

    if not dbh:
        db = DB(database_path + "/", "database-dump", debug=False, run_on_ram=database_path + '/basefull_phrases3.sql')
        dbh = get_all_phrases_prob(data_source, db, phrase_size)
        dbh.to_file(database_path, 'base_full3.txt')
        del db

    best_firefly = np.zeros(dimension)  # will return this guy right here
    random.seed(datetime.now())  # Reset the random generator
    w_fireflies = init_ff(number_fireflies, dimension)  # Generate the 'physical' fireflies (their alpha powers)
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

        print("GENERATION " + str(i).zfill(3) + ": " + str(best_firefly))
        print("Best Brightness: " + str(brightness[0]))
        print("Worst Brightness: " + str(brightness[-1]))
        print("Most Bright FF: " + str(index[0]))
        print('Processing Time: ' + str(datetime.now() - start))
        print("====")

        # loops through upper triangular matrix without its diagonal
        for row in range(number_fireflies):
            for col in range(row + 1, number_fireflies):
                distances[row][col] = dist(w_fireflies[row], w_fireflies[col])

        w_fireflies = move_fireflies(w_fireflies, brightness, distances, alpha, gamma)
        alpha *= delta

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
    filename = 'firefly' + str(phrase_size) + \
        datetime.now().strftime("%Y%m%d_%H%M%S") + '-' + str(max_generation) + '-' + \
        str(original_alpha) + '_' + str(gamma) + '_' + str(delta) + '.png'
    plt.savefig('experiments/1/graphs/' + filename)
    plt.clf()

    if file:
        file.write(
            '"' + filename + '";' +
            '"' + str(original_alpha) + '";' +
            '"' + str(gamma) + '";' +
            '"' + str(delta) + '";' +
            '"' + str(best_firefly) + '"\n'
        )

    return [best_brightness, best_firefly]


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


def gera_base_testes(path='../Reports/base_full/testes'):
    start = datetime.now()
    print('db2: ' + datetime.now().strftime("%H:%M:%S"))
    db2 = DB(path + "/", "database-dump", debug=False, run_on_ram=path + '/basefull_phrases2.sql')
    print('db3: ' + datetime.now().strftime("%H:%M:%S"))
    db3 = DB(path + "/", "database-dump", debug=False, run_on_ram=path + '/basefull_phrases3.sql')
    print('dbh2: ' + datetime.now().strftime("%H:%M:%S"))
    dbh = get_all_phrases_prob(path + '/validation_tab.csv', db2, 2)
    print('dbh2-tofile: ' + datetime.now().strftime("%H:%M:%S"))
    dbh.to_file(path, 'basefull_phrases2.txt')
    print('dbh3: ' + datetime.now().strftime("%H:%M:%S"))
    dbh = get_all_phrases_prob(path + '/validation_tab.csv', db3, 3)
    print('dbh3-tofile: ' + datetime.now().strftime("%H:%M:%S"))
    dbh.to_file(path, 'basefull_phrases3.txt')
    end = datetime.now()
    print("-")
    print('Começou: ' + start.strftime("%H:%M:%S"))
    print('Terminou: ' + end.strftime("%H:%M:%S"))
    print('Delta: ' + str(end - start))


def main2(path='../Reports/base_full/testes'):
    dbh = DbHandler()
    dbh.from_file(path, 'base_full2.txt')
    best_ff = firefly(
        dimension=5,
        number_fireflies=100,
        max_generation=100,
        data_source='../database/LIAR_1_10700.csv',
        database_path=path,
        processes=16,
        phrase_size=2,
        dbh=dbh
    )
    print("Melhor FF: ", best_ff)


def main3(ff, text, path='../Reports/base_full/testes', db=None, ps=3):
    if not db:
        db = DB(path + "/", "database-dump", debug=False, run_on_ram=path + '/basefull_phrases2.sql')
        db.ram = False
    return calc_text_prob(
            text=text,
            database=db,
            w_firefly=ff,
            phrase_size=ps
        )


def main4():
    db3 = DB('../Reports/base_full/testes' + "/", "database-dump", debug=False,
             run_on_ram='../Reports/base_full/testes' + '/basefull_phrases3.sql')
    db3.ram = False
    db2 = DB('../Reports/base_full/testes' + "/", "database-dump", debug=False,
             run_on_ram='../Reports/base_full/testes' + '/basefull_phrases2.sql')
    db2.ram = False
    t = input()

    while t:
        print("FF3   : ", main3([0.01516190, 0.13934191, 0.34223577, 0.26711407, 0.23614635], t, db=db3, ps=3))
        print("FF2   : ", main3([0.02620581, 0.15741069, 0.36506735, 0.14562509, 0.30569106], t, db=db2, ps=2))
        print("WHALES: ", main3([0.11556000, 0.17738700, 0.01242800, -0.4284020, 0.02998000], t, db=db3, ps=3))

        t = input()


def train(file, phrase_size):
    db = DB(path='', filename=file, run_on_ram=True)
    with open(file, newline='', encoding='utf-8-sig') as csvfile:  # lendo o csv
        reader = csv.reader(csvfile, delimiter=";", quoting=csv.QUOTE_NONE)
        for row in reader:  # para cada linha
            t = Text(str.split(str.upper(row[1])), row[0])  # cria um Text
            if t:
                t.build_phrases(phrase_size)
                db.insert_text(t)
                del t
            else:
                return -100


def isprimentos(path='../experiments/1', treino='treino.csv', ff='firefly.csv', validation='validation.csv',
                phrase_size=[2, 3]):
    for ps in phrase_size:
        print("Start loop for phrase size: ", ps)
        start = datetime.now()

        # Setting up DATABASE
        database_filename = 'database' + str(ps) + '.sql'
        print("Load DB: ", path + '/' + database_filename)
        db = DB(run_on_ram=path + '/' + database_filename)
        print("DB Loaded")
        db.ram = False

        # Setting up DBH
        dbh_filename = 'dbh' + str(ps) + '.txt'
        if os.path.isfile(path + '/' + dbh_filename):
            print("DBH already exists")
            print("Loading DBH: ", dbh_filename)
            dbh = DbHandler()
            dbh.from_file(path, dbh_filename)
            print("DBH Loaded")
        else:
            print("Finding Probability")
            dbh = get_all_phrases_prob(path + '/' + ff, db, ps)
            print("to_file")
            dbh.to_file(path, 'dbh' + str(ps) + '.txt')

        # Setting up Firefly
        best_ff = []
        config = configparser.ConfigParser()
        ff_filename = 'ff' + str(ps) + '.ini'
        if os.path.isfile(path + '/' + ff_filename):
            print("Firefly already exists")
            print("Loading Firefly: ", ff_filename)
            config.read(path + '/' + ff_filename)
            temp = str.split(config['Firefly']['alpha_powers'])
            for t in temp:
                best_ff.append(float(t))
        else:
            print("Calculating firefly")
            [brightness, best_ff] = firefly(
                dimension=5,
                number_fireflies=100,
                max_generation=100,
                data_source=path + '/' + ff,
                database_path=path,
                processes=16,
                phrase_size=ps,
                dbh=dbh
            )
            config.add_section('Firefly')
            best_ff = str(best_ff)
            best_ff = best_ff.replace('[', '')
            best_ff = best_ff.replace(']', '')
            config.set('Firefly', 'alpha_powers', best_ff)
            config.set('Firefly', 'brightness', brightness)
            config.write(path + '/' + ff_filename)

        print('BEST FIREFLY: ', best_ff)
        print("")

        # Setting up Tests
        print("Testing")
        output = open(path + '/' + 'results' + str(ps) + '.csv', 'w')
        output.write('text;grand_truth;calculated;dif;found phrases;out of\n')
        row_number = 0
        with open(path + '/' + validation, newline='', encoding='utf-8-sig') as csvfile:  # lendo o csv
            reader = csv.reader(csvfile, delimiter=";", quoting=csv.QUOTE_NONE)
            for row in reader:
                line = row[1] + ';' + str(row[0]) + ';'
                [text_prob, found, out_of] = calc_text_prob(row[1], db, best_ff, ps)
                difference = float(row[0]) - text_prob
                line += str(text_prob) + ';' + str(difference) + ';' + str(found) + ';' + str(out_of)
                output.write(line + '\n')
                row_number += 1

        print(row_number, " lines tested")
        output.close()
        # print("Saving parameters")
        # description = open(path + '/' + 'desc' + str(ps) + '.txt', 'w')
        # description.write(
        #     'Path:        ' + path + '\n' +
        #     'Train DB:    ' + treino + '\n' +
        #     'Firefly:     ' + ff + '\n' +
        #     'Validation:  ' + validation + '\n' +
        #     'Found FF:    ' + best_ff + '\n' +
        #     'Phrase size: ' + str(ps) + '\n' +
        #     'Start time:  ' + start.strftime("%H:%M:%S") + '\n' +
        #     'End time:    ' + datetime.now().strftime("%H:%M:%S") + '\n'
        # )
        # description.close()

def isprimento1():
    exp = 'Experimento_1_5_10700'
    words = 3

    db = DB(run_on_ram='experiments/1/' + exp + '/database.sql')
    db.ram = False

    dbh_filename = 'dbh' + exp + '.txt'
    if os.path.isfile('Reports/experimentos' + '/' + dbh_filename):
        print("DBH already exists")
        print("Loading DBH: ", dbh_filename)
        dbh = DbHandler()
        dbh.from_file('Reports/experimentos', dbh_filename)
        print("DBH Loaded")
    else:
        print("Finding Probability")
        dbh = get_all_phrases_prob('experiments/1/' + exp + '/training_tab.csv', db, words)
        print("to_file")
        dbh.to_file('Reports/experimentos', dbh_filename)

    [brightness, best_ff] = firefly(
        dimension=5,
        number_fireflies=100,
        max_generation=100,
        data_source='experiments/1/' + exp + '/training_tab.csv',
        processes=16,
        phrase_size=words,
        dbh=dbh)

    path = 'experiments/1/' + exp
    output = open(path + '/' + exp + '.csv', 'w')
    output.write('text;grand_truth;calculated;dif;found phrases;out of\n')
    row_number = 0
    with open(path + '/' + 'validation_tab.csv', newline='', encoding='utf-8-sig') as csvfile:  # lendo o csv
        reader = csv.reader(csvfile, delimiter=";", quoting=csv.QUOTE_NONE)
        for row in reader:
            line = row[1] + ';' + str(row[0]) + ';'
            [text_prob, found, out_of] = calc_text_prob(row[1], db, best_ff, words)
            difference = float(row[0]) - text_prob
            line += str(text_prob) + ';' + str(difference) + ';' + str(found) + ';' + str(out_of)
            output.write(line + '\n')
            row_number += 1

    print(row_number, " lines tested")
    output.close()
