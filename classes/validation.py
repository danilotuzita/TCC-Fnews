#criar csv com os textos de treinamento
# encoding: utf-8
import csv
from classes.text import Text
from classes.db import DB
from pathlib import Path
import random
import datetime
import sys
import os

def brilho(firefly):
    b = 0
    for i in range(len(firefly)):
        b += firefly[i]
    return b

def validation_files_creation(number_of_slices, validation_slice, source_file, output_directory): #numero de divisões do arquivo de entrada e divisão selecionada para validação

    with open(source_file) as csv_file:  # conta a quantidade de linhas no arquivo original
        csv_reader = csv.reader(csv_file, delimiter=';')
        reader_line_count = 0
        writer_line_count = 0
        for row in csv_reader:
            reader_line_count += 1

    with open(source_file, newline="") as csv_file:  # escreve tabela de validação
        csv_reader = csv.reader(csv_file, delimiter=';')

        with open(output_directory + '/validation_tab.csv', mode='w', newline="") as validation_tab:
            validation_tab = csv.writer(validation_tab, delimiter=';', quotechar='', quoting=csv.QUOTE_NONE, escapechar='')
            for row2 in csv_reader:
                writer_line_count += 1
                if writer_line_count <= (reader_line_count / number_of_slices)*validation_slice and writer_line_count > (reader_line_count / number_of_slices)*(validation_slice-1):
                    validation_tab.writerow([row2[0],row2[1]])

    writer_line_count = 0 #RESETA ESCRITA

    # criar csv com os textos de aprendizado

    with open(source_file) as csv_file:  # escreve tabela de aprendizagem
        csv_reader = csv.reader(csv_file, delimiter=';')

        with open(output_directory + '/training_tab.csv', mode='w', newline="") as training_tab:
            training_tab = csv.writer(training_tab, delimiter=';', quotechar='', quoting=csv.QUOTE_NONE,
                                        escapechar='')
            for row2 in csv_reader:
                writer_line_count += 1
                if writer_line_count > (reader_line_count / number_of_slices)*validation_slice or writer_line_count <= (reader_line_count / number_of_slices)*(validation_slice-1):
                    training_tab.writerow([row2[0], row2[1]])




# definir dados lidos pelo main.py (enviando caminho do .csv de treinamento)
# leer dados da base alimentada pelo sistema principal

#construir texto baseado no arquivo de validação

def validation_text_comparison(data_validation_source, report_flag, training_file, report_name, error_threshold): #fonte de validação e flag para relatório de teste e arquivo de treinamento
    DB_V = DB(path='../database/',debug=True)
    now = datetime.datetime.now()
    positive_error = 0 #erro positivo
    negative_error = 0 #erro negativo
    positive_error_c = 0 #contagem de erro positivo
    negative_error_c = 0 #contagem de erro negativo
    sentence_counter = 0 #contagem de frases
    with open(data_validation_source,  encoding='utf-8-sig') as csv_file:  # conta a quantidade de linhas no arquivo original
        csv_reader = csv.reader(csv_file, delimiter=';')

        if report_flag: #caso a flag de relatório esteja ativada
            with open("../reports/" + report_name + "/report.out", "w") as report: #abre arquivo de relatório
                orig_stdout = sys.stdout # guarda saida padrão
                sys.stdout = report # troca saida padrão por relatório
                print("Data:    (DD/MM/AAAA)" + str(now.day) + "/" + str(now.month) + "/" + str(now.year))
                print("Hora:    (HH:MM:SS)" + str(now.hour) + ":" + str(now.minute) + ":" + str(now.second))
                print("Training_File:   " + training_file)
                print("Validation_File: " + data_validation_source)
                for row in csv_reader:
                    sentence_counter += 1
                    t = Text(str.split(str.upper(row[1])), row[0])
                    if t:
                        t.build_phrases(3) #construir frases
                        first = 0
                        prob = 0
                        for p in t.phrases:
                            p_prob = DB_V.get_phrase_prob(p)
                            print("Palavra: " + p.words[0].value)
                            print("Palavra: " + p.words[1].value)
                            print("Palavra: " + p.words[2].value)
                            print("Probabilidade: " + str(p_prob))
                            if first != 0:
                                prob = prob * (1-p_prob) # busca a probabilidade associada à frase e calcula probabilidade do texto
                            else:
                                prob = (1-p_prob) # busca probabilidade da primeira frase
                                first = 1
                            prob = 1 - prob
                        print(row) #imprime texto
                        print(t.probability) #imprime probabilidade do texto
                        print(prob) #imprime probabilidade calculada
                        error = float(t.probability) - prob;
                        if error > 0:
                            positive_error += error
                            if error > error_threshold:
                                positive_error_c += 1
                        else:
                            negative_error += error
                            if error < error_threshold*-1:
                                negative_error_c += 1
                        del t
                    else:
                        return -100
                print("Numero de frases:    " + str(sentence_counter))
                print("Erro positivo:   " + str(positive_error))
                print("Erro negativo:   " + str(negative_error))
                print("Erro total:      " + str(positive_error + abs(negative_error)))
                print("Contagem de Erros Positivos:     " + str(positive_error_c))
                print("Contagem de Erros Negativos:     " + str(negative_error_c))
            sys.stdout = orig_stdout    # reseta saída
            report.close()  #fechar arquivo de relatório

        else: #caso a flag de relatório esteja desativada
            for row in csv_reader:
                sentence_counter += 1
                t = Text(str.split(str.upper(row[1])), row[0])
                if t:
                    t.build_phrases(3)  # construir frases
                    first = 0
                    for p in t.phrases:
                        if first != 0:
                            prob = prob * (1 - DB_V.get_phrase_prob(p))  # busca a probabilidade associada à frase e calcula probabilidade do texto
                        else:
                            prob = (1 - DB_V.get_phrase_prob(p))  # busca probabilidade da primeira frase
                            first = 1
                        prob = 1 - prob
                        del t
                    else:
                        return -100

def validation_generate_reportname(appendix = ""):
    now = datetime.datetime.now()
    return "report" + str(now.day) + str(now.month) + str(now.year) + str(now.hour) + str(now.minute) + str(now.second) + appendix


def validation_report_directory(directory_name):
    os.mkdir(directory_name)

def validation_train(report_dir, source_name):

    # inicio do treino ===============================
    start = datetime.datetime.now()
    db = DB(report_dir, "/database", False)
    with open(source_name, newline='', encoding='utf-8-sig') as csvfile:  # lendo o csv
        reader = csv.reader(csvfile, delimiter=";", quoting=csv.QUOTE_NONE)  # leitura do arquivo
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
    # fim do treino


def main_validation(source, report_dir, slice_number):
    # gera nome do relatório original
    report_name_o = validation_generate_reportname()
    for slice in range(1,slice_number+1):
        report_name = report_name_o + "_" + str(slice)  # gera nome do relatório para a fatia
        validation_report_directory(report_dir + report_name) # cria diretório do relatório
        validation_files_creation(slice_number, slice, source, report_dir + report_name) # cria arquivos divididos de validação / treinamento
        validation_train(report_dir + report_name,report_dir + report_name + '/training_tab.csv') #treinamento
        validation_text_comparison(report_dir + report_name + '/validation_tab.csv', True, report_dir + report_name + '/validation_tab.csv', report_name, 0.05) #validação


main_validation('../database/LIAR_1_50.csv', "../reports/", 5)

# ================= anotações ===========================

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