import os


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
