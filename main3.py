import os
import csv
import numpy as np
import configparser
from datetime import datetime
from classes.db import DB
from classes.text import Text
from classes.Firefly import firefly, get_all_phrases_prob, DbHandler, calc_text_prob


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
