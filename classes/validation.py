# criar csv com os textos de treinamento
# encoding: utf-8
import csv

from numpy.lib.index_tricks import nd_grid

from classes.text import Text
from classes.db import DB
from pathlib import Path
import random
import datetime
import sys
import os


class AlfaCluster:
    # inicializa array de alfas por cluster com o numero de alfas e o array
    def __init__(self, number_of_alfas, alfa_array):
        self.n = number_of_alfas
        self.arr = alfa_array

    # retorna o valor alfa para uma dada probabilidade
    def getalfa(self, prob):
        return prob / (1/self.n)

    def getalfaS(self, index):
        if 0 <= index < self.n:
            return self.arr[index]

    # retorna o valor do brilho


def Brilho(data_validation_source, firefly, DB_V):
    alfas = AlfaCluster(len(firefly), firefly)
    positive_error = 0  # erro positivo
    negative_error = 0  # erro negativo
    sentence_counter = 0
    with open(data_validation_source,encoding='utf-8-sig') as csv_file:  # conta a quantidade de linhas no arquivo original
        csv_reader = csv.reader(csv_file, delimiter=';')
        TP=0
        FP=0
        TN=0
        FN=0
        for row in csv_reader:
            sentence_counter = sentence_counter + 1
            t = Text(str.split(str.upper(row[1])), row[0])
            if t:
                t.build_phrases(3)  # construir frases
                first = 0
                prob = 0
                for p in t.phrases:
                    p_prob = DB_V.get_phrase_prob(p)
                    temp_alfa = alfas.getalfa(p_prob)
                    if first != 0:
                        prob = prob * (1 - p_prob) ** temp_alfa  # busca a probabilidade associada à frase e calcula probabilidade do texto
                    else:
                        prob = (1 - p_prob) ** temp_alfa  # busca probabilidade da primeira frase
                        first = 1
                    prob = 1 - prob
                error = float(t.probability) - prob;
                if (prob >= 0.5 and float(t.probability) >= 0.5) or (prob <= 0.5 and float(t.probability) <= 0.5):
                    if prob >= 0.5:
                        TP = TP+1
                    else:
                        TN = TN+1
                else:
                    if prob >= 0.5:
                        FP = FP+1
                    else:
                        FN = FN+1
                if error > 0:
                    positive_error += error
                else:
                    negative_error += error
                del t
    #return (positive_error + abs(negative_error))/sentence_counter #retorna o erro mais 0.000001 para evitar divisão por 0
    return (TP+TN)/(sentence_counter)
    #return (alfas.getalfaS(0) + alfas.getalfaS(1) + alfas.getalfaS(2) + alfas.getalfaS(3) + alfas.getalfaS(4))


def validation_files_creation(number_of_slices, validation_slice, source_file, output_directory): #numero de divisões do arquivo de entrada e divisão selecionada para validação

    with open(source_file, encoding='utf-8-sig') as csv_file:  # conta a quantidade de linhas no arquivo original
        csv_reader = csv.reader(csv_file, delimiter=';')
        reader_line_count = 0
        writer_line_count = 0
        for row in csv_reader:
            reader_line_count += 1

    with open(source_file, newline="", encoding='utf-8-sig') as csv_file:  # escreve tabela de validação
        csv_reader = csv.reader(csv_file, delimiter=';')

        with open(output_directory + '/validation_tab.csv', mode='w', newline="", encoding='utf-8-sig') as validation_tab:
            validation_tab = csv.writer(validation_tab, delimiter=';', quotechar='', quoting=csv.QUOTE_NONE, escapechar='')
            for row2 in csv_reader:
                writer_line_count += 1
                if writer_line_count <= (reader_line_count / number_of_slices)*validation_slice and writer_line_count > (reader_line_count / number_of_slices)*(validation_slice-1):
                    validation_tab.writerow([row2[0],row2[1]])

    writer_line_count = 0 #RESETA ESCRITA

    # criar csv com os textos de aprendizado

    with open(source_file, encoding='utf-8-sig') as csv_file:  # escreve tabela de aprendizagem
        csv_reader = csv.reader(csv_file, delimiter=';')

        with open(output_directory + '/training_tab.csv', mode='w', newline="", encoding='utf-8-sig') as training_tab:
            training_tab = csv.writer(training_tab, delimiter=';', quotechar='', quoting=csv.QUOTE_NONE,
                                        escapechar='')
            for row2 in csv_reader:
                writer_line_count += 1
                if writer_line_count > (reader_line_count / number_of_slices)*validation_slice or writer_line_count <= (reader_line_count / number_of_slices)*(validation_slice-1):
                    training_tab.writerow([row2[0], row2[1]])

# definir dados lidos pelo main1.py (enviando caminho do .csv de treinamento)
# ler dados da base alimentada pelo sistema principal

#  construir texto baseado no arquivo de validação

#  fonte de validação e flag para relatório de teste e arquivo de treinamento

def validation_text_comparison(data_validation_source, report_flag, training_file, report_name, error_threshold, alfas, database):
    DB_V = DB(database + "/", "database", debug=False, run_on_ram=database+"/database.sql")
    print(database)
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
                            print("Palavra: " + (p.words[0].value.encode('ascii', 'ignore')).decode('utf-8'))
                            print("Palavra: " + (p.words[1].value.encode('ascii', 'ignore')).decode('utf-8'))
                            print("Palavra: " + (p.words[2].value.encode('ascii', 'ignore')).decode('utf-8'))
                            print("Probabilidade: " + str(p_prob))
                            temp_alfa = alfas.getalfa(p_prob)
                            print("Alfa: " + str(temp_alfa))
                            if first != 0:
                                prob = prob * (1-p_prob)**temp_alfa # busca a probabilidade associada à frase e calcula probabilidade do texto
                            else:
                                prob = (1-p_prob)**temp_alfa # busca probabilidade da primeira frase
                                first = 1
                            prob = 1 - prob
                        print(row) #imprime texto
                        print("Probabilidade do texto:  " + str(t.probability)) #imprime probabilidade do texto
                        print("Probabilidade calculada: " + str(prob)) #imprime probabilidade calculada
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
                print("Numero de frases:    " + str(sentence_counter))
                print("Erro positivo:   " + str(positive_error))
                print("Erro negativo:   " + str(negative_error))
                print("Erro total:      " + str(positive_error + abs(negative_error)))
                print("Contagem de Erros Positivos:     " + str(positive_error_c))
                print("Contagem de Erros Negativos:     " + str(negative_error_c))
            sys.stdout = orig_stdout    # reseta saída
            report.close()  #fechar arquivo de relatório

        # caso a flag de relatório esteja desativada
        else:
            for row in csv_reader:
                sentence_counter += 1
                t = Text(str.split(str.upper(row[1])), row[0])
                if t:
                    t.build_phrases(3) #construir frases
                    first = 0
                    prob = 0
                    for p in t.phrases:
                        p_prob = DB_V.get_phrase_prob(p)
                        temp_alfa = alfas.getalfa(p_prob)
                        if first != 0:
                            prob = prob * (1-p_prob)**temp_alfa # busca a probabilidade associada à frase e calcula probabilidade do texto
                        else:
                            prob = (1-p_prob)**temp_alfa # busca probabilidade da primeira frase
                            first = 1
                        prob = 1 - prob
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
    return 1-(positive_error+abs(negative_error))/sentence_counter #retorna o erro mais 0.000001 para evitar divisão por 0


def validation_generate_reportname(appendix = ""):
    now = datetime.datetime.now()
    return "report" + str(now.day) + str(now.month) + str(now.year) + str(now.hour) + str(now.minute) + str(now.second) + appendix


def validation_report_directory(directory_name):
    os.mkdir(directory_name)


def validation_train(report_dir, source_name):
    line_count = 0;
    # inicio do treino ===============================
    start = datetime.datetime.now()
    db = DB(report_dir + "/", "database", debug=False, run_on_ram=True)
    print(report_dir)
    with open(source_name, newline='', encoding='utf-8-sig') as csvfile:  # lendo o csv
        reader = csv.reader(csvfile, delimiter=";", quoting=csv.QUOTE_NONE)  # leitura do arquivo
        for row in reader:  # para cada linha
            line_count = line_count+1
            print(str(line_count))
            t = Text(str.split(str.upper(row[1])), row[0])  # cria um Text
            if t:
                t.build_phrases(3)
                #  t.print_phrases()
                db.insert_text(t, False)
                del t
            else:
                return -100
    end = datetime.datetime.now()
    print('Começou: ' + start.strftime("%H:%M:%S"))
    print('Terminou: ' + end.strftime("%H:%M:%S"))
    print('Delta: ' + str(end - start))
    # fim do treino


def main_validation(source, report_dir, slice_number, n_alfas, alfa_arr):
    temp  = 1
    # from classes.Firefly import lplFirefly
    from classes.Firefly import firefly
    # etapa de treinamento inicial, naive bayes

    # gera nome do relatório original
    report_name_o = validation_generate_reportname()
    # gera nome do relatorio fonte
    validation_report_directory(report_dir + report_name_o)
    best = 3.14  # declara melhor resultado de brilho
    best_slice = 0
    ALFAS = AlfaCluster(n_alfas, alfa_arr)
    for slice in range(1,slice_number+1):
        print("Slice " + str(slice) + " de " + str(slice_number))
        print("gera nome do relatório")

        # gera nome do relatório para a parte do conjunto cross validation
        report_name = report_name_o + "_" + str(slice)
        print(report_name)

        # cria diretório do relatório
        validation_report_directory(report_dir + report_name)

        # cria arquivos divididos de validação / treinamento
        print("Cria arquivos de validação")
        validation_files_creation(slice_number, slice, source, report_dir + report_name)

        # treinamento
        print("Treino")
        validation_train(report_dir + report_name,report_dir + report_name + '/training_tab.csv')
        print("Fim treino")

        # validacao
        print("Validacao")
        temp = validation_text_comparison(report_dir + report_name + '/validation_tab.csv', True, report_dir + report_name + '/training_tab.csv', report_name, 0.05, ALFAS, report_dir + report_name) #validação
        print("Fim validacao")

        # caso seja primeira fatia
        if slice == 1:
            best = temp
            best_slice = slice
        else:
            if temp > best:
                best = temp
                best_slice = slice
    print("O melhor slice:")
    print(best_slice)

    # etapa secundaria, utilizando otimização firefly
    print("Executa firefly")
    with open(report_dir + report_name_o + "/report.out", "w") as report:  # abre arquivo de relatório
        orig_stdout = sys.stdout  # guarda saida padrão
        # sys.stdout = report  # troca saida padrão por relatório
        #bests = firefly(n_alfas, max_generation=50,
        #                data_source=report_dir+report_name_o + '_' + str(best_slice) + '/validation_tab.csv',
        #                database_path=report_dir + report_name_o + '_' + str(best_slice),
        #                processes=16)
        sys.stdout = report  # troca saida padrão por relatório
        #bests = lplFirefly(n_alfas, 100, 0.8, 0.85, 0.5, 30, report_dir+report_name_o + '_' + str(best_slice) + '/validation_tab.csv', report_dir+report_name_o + '_' + str(best_slice))
        print("Melhores fireflies:")
        #print(bests)
        sys.stdout = orig_stdout  # reseta saída
        report.close()  # fechar arquivo de relatório

    # print("Melhores fireflies")
    #print(bests)
    # x = input()


if __name__ == "__main__":
    # base a ser lida, pasta de relatorios, numero de secoes para validacao, numero de alfas e array de alfas ==============
    print("Inicio")
    # x = input()
    main_validation('../database/LIAR_1_10700.csv', "../reports/", 1, 5, [1, 1, 1, 1, 1])


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

# def brilho(firefly):
#     b = 0
#     for i in range(len(firefly)):
#         b += firefly[i]
#     return b
