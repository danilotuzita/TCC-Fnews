import os
import csv
import pandas
import datetime
from classes.db import DB
from classes.text import Text


def find_files(path, filetype):
    i = 1
    filenames = []
    for f in os.listdir(path):  # lendo todos os arquivos
        if f.endswith("." + filetype):
            print(str(i) + ' - ' + f)
            filenames.append(path + f)
            i += 1

    while True:
        a = input('Digite o numero do arquivo que deseja usar: ')
        a = int(a) - 1
        if a == -1:
            exit(0)
        try:
            default = filenames[a]
            break
        except IndexError:
            print('Numero inválido. Se deseja sair digite 0.')

    return default


def load_firefly(path):
    ff = []
    with open(path, 'r') as file:
        for line in file:
            ff.append(float(line))

    return ff


def save_firefly(ff, path):
    with open(path, 'w') as file:
        for line in ff:
            file.write(str(line) + '\n')


def create_database_from_csv(csv_filename, dump_filename, phrase_size, debug_mode=False):
    start = datetime.datetime.now()
    print('Criando sql: ', dump_filename)
    db = DB(debug=debug_mode, path='', filename=dump_filename[:-4], run_on_ram=True)
    with open(csv_filename, newline='', encoding='utf-8-sig') as csvfile:  # lendo o csv
        reader = csv.reader(csvfile, delimiter=";", quoting=csv.QUOTE_NONE)
        for row in reader:  # para cada linha
            t = Text(str.split(str.upper(row[1])), row[0])  # cria um Text
            if t:
                t.build_phrases(phrase_size)
                if debug_mode:
                    t.print_phrases()
                db.insert_text(t, debug_mode)
                del t
            else:
                return -100
    end = datetime.datetime.now()
    print('Começou: ' + start.strftime("%H:%M:%S"))
    print('Terminou: ' + end.strftime("%H:%M:%S"))
    print('Delta: ' + str(end - start))

    return db
