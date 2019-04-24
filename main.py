# encoding: utf-8
from classes.text import Text
from classes.db import DB
from pathlib import Path
# from classes.Firefly import lplFirefly as Firefly
import datetime
import csv
import os


def call_firefly():
    db = DB()
    # fireflies = Firefly(db.get_phrase_count())
    # fireflies = Firefly(10)


def finaliza():
    a = input('Deseja fechar o programa? S/N')
    if str.upper(a) in {'S', 'Y', '1'}:
        return True
    return False


def options(a):
    if int(a) == 1:
        a = input('Isso irá sobreescrever a base de agora, deseja continuar? S/N')
        if str.upper(a) in {'S', 'Y', '1'}:
            try:
                [os.remove(os.path.join("database/", f)) for f in os.listdir("database/") if f.endswith(".db")]
            except IOError:
                exit(-550)
            return train()
        return False
    elif int(a) in {2, 3}:
        print('Backup completo! Nome do novo arquivo: ' + backup())
        if int(a) == 3:
            train()
    elif int(a) == 4:
        print('WIP')

    return finaliza()


def main():
    questionario = '1 - Train\n' \
                   '2 - BKP\n' \
                   '3 - BKP and Train\n' \
                   '4 - Selects\n'\
                   'Selecione uma opção: '

    a = input(questionario)
    while not options(a):
        a = input(questionario)


def backup():
    db = DB()
    new_filename = db.save_backup()
    del db
    return new_filename


def train():
    default = 'database/treino.csv'
    a = input('Nome default da tabela de Treino: ' + default +
              '\n1 - Continuar'
              '\n2 - Mudar'
              '\nSelecione uma opção: '
    )
    if str.upper(a) in {'S', 'Y', '1'}:
        print('Continuando com a a tabela: ' + default)
    else:
        i = 1
        filenames = []
        for f in os.listdir(os.path.join(Path().absolute(), "database")):  # lendo todos os arquivos .csv em database/
            if f.endswith(".csv"):
                print(str(i) + ' - ' + f)
                filenames.append('database/' + f)
                i += 1

        while True:
            a = input('Digite o numero da tabela que deseja usar: ')
            a = int(a) - 1
            if a == -1:
                exit(0)
            try:
                default = filenames[a]
                break
            except IndexError:
                print('Numero inválido. Se deseja sair digite 0.')

    a = input('Debug? S/N: ')
    debug_mode = False
    if str.upper(a) in {'S', 'Y', '1'}:
        debug_mode = True

    start = datetime.datetime.now()
    db = DB(debug=debug_mode)
    with open(default, newline='', encoding='utf-8-sig') as csvfile:  # lendo o csv
        reader = csv.reader(csvfile, delimiter=";", quoting=csv.QUOTE_NONE)
        for row in reader:  # para cada linha
            t = Text(str.split(str.upper(row[1])), row[0])  # cria um Text
            if t:
                t.build_phrases(3)
                t.print_phrases()
                db.insert_text(t, True)
                del t
            else:
                return -100

    end = datetime.datetime.now()
    print('Começou: ' + start.strftime("%H:%M:%S"))
    print('Terminou: ' + end.strftime("%H:%M:%S"))
    print('Delta: ' + str(end - start))


# texto = 'nós temos que testar o modelo q nós temos (mesmo que esteja quebrado) com o firefly'
# t = Text(str.split(str.upper(texto), ' '))  # cria um Text
# t.build_phrases(3)
# t.print_phrases()

main()
# call_firefly()
