#criar csv com os textos de treinamento
# encoding: utf-8
import csv
from classes.text import Text
from classes.db import DB
import random

def brilho(firefly):
    b = 0
    for i in range(len(firefly)):
        b += firefly[i]
    return b

def validation_files_creation(number_of_slices, validation_slice):

    with open('../database/Tabela_TEST.csv') as csv_file:  # conta a quantidade de linhas no arquivo original
        csv_reader = csv.reader(csv_file, delimiter=';')
        reader_line_count = 0
        writer_line_count = 0
        for row in csv_reader:
            reader_line_count += 1

    with open('../database/Tabela_TEST.csv', newline="") as csv_file:  # escreve tabela de validação
        csv_reader = csv.reader(csv_file, delimiter=';')

        with open('../database/validation_tab.csv', mode='w', newline="") as validation_tab:
            validation_tab = csv.writer(validation_tab, delimiter=';', quotechar='', quoting=csv.QUOTE_NONE, escapechar='')
            for row2 in csv_reader:
                writer_line_count += 1
                if writer_line_count <= (reader_line_count / number_of_slices)*validation_slice and writer_line_count > (reader_line_count / number_of_slices)*(validation_slice-1):
                    validation_tab.writerow([row2[0],row2[1]])

    writer_line_count = 0 #RESETA ESCRITA

    # criar csv com os textos de aprendizado

    with open('../database/Tabela_TEST.csv') as csv_file:  # escreve tabela de aprendizagem
        csv_reader = csv.reader(csv_file, delimiter=';')

        with open('../database/training_tab.csv', mode='w', newline="") as training_tab:
            training_tab = csv.writer(training_tab, delimiter=';', quotechar='', quoting=csv.QUOTE_NONE,
                                        escapechar='')
            for row2 in csv_reader:
                writer_line_count += 1
                if writer_line_count > (reader_line_count / number_of_slices)*validation_slice or writer_line_count <= (reader_line_count / number_of_slices)*(validation_slice-1):
                    training_tab.writerow([row2[0], row2[1]])




# definir dados lidos pelo main.py (enviando caminho do .csv de treinamento)
# leer dados da base alimentada pelo sistema principal

#construir  texto baseado no arquivo de validação

def validation_text_comparison():
    DB_V = DB(path='../database/',debug=True)

    with open('../database/training_tab.csv') as csv_file:  # conta a quantidade de linhas no arquivo original
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            t = Text(str.split(str.upper(row[1])), row[0])
            prob = 0.5
            if t:
                t.build_phrases(3) #construir frases
                for p in t.phrases:
                    prob = prob * (1- DB_V.get_phrase_prob(p)) # busca a probabilidade associada à frase e calcula probabilidade do texto
                    prob = 1 - prob
                print("====")
                print(row)
                print(t.probability)
                print(row[0])
                print(prob)
                del t
            else:
                return -100



#calcular veracidade do texto

#comparar com veracidade pre classificada

# validar dados com a base de validação (receber score = taxa de verdadeiros positivos)
# enviar score e um csv com as probabilidades e os alfas para o firefly
# por x iterações:
    # modificar alfas na tabela
    # leer dados da base alimentada pelo sistema principal
    # validar dados com a base de validação (receber score = taxa de verdadeiros positivos)
    # enviar score e um csv com as probabilidades e os alfas para o firefly

# aaaaa

#funcao principal de validacao

def main_validation():

    validation_files_creation(5, 2)
    validation_text_comparison()


# main_validation()

