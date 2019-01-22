#criar csv com os textos de treinamento

import csv

def validation_files_creation(number_of_slices, validation_slice, learning_slice):

    with open('../database/Tabela_TEST.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        reader_line_count = 0
        writer_line_count = 0
        for row in csv_reader:
            reader_line_count += 1

    with open('../database/Tabela_TEST.csv') as csv_file:   #escreve tabela de validação
        csv_reader = csv.reader(csv_file, delimiter=';')

        with open('../database/validation_tab.csv', mode='w') as validation_tab:
            validation_tab = csv.writer(validation_tab, delimiter=';', quotechar='"', quoting=csv.QUOTE_NONE, escapechar='\\')
            for row2 in csv_reader:
                writer_line_count += 1
                if writer_line_count <= (reader_line_count / 5):
                    validation_tab.writerow([row2[0],row2[1]])

    writer_line_count = 0 #RESETA ESCRITA

    with open('../database/Tabela_TEST.csv') as csv_file:  # escreve tabela de aprendizagem
        csv_reader = csv.reader(csv_file, delimiter=';')

        with open('../database/training_tab.csv', mode='w') as training_tab:
            training_tab = csv.writer(training_tab, delimiter=';', quotechar='"', quoting=csv.QUOTE_NONE,
                                        escapechar='\\')
            for row2 in csv_reader:
                writer_line_count += 1
                if writer_line_count > (reader_line_count / 5):
                    training_tab.writerow([row2[0], row2[1]])

validation_files_creation(1,1,1)

#criar csv com os textos de validação
#definir dados lidos pelo main.py (enviando caminho do .csv de treinamento)
#leer dados da base alimentada pelo sistema principal
#validar dados com a base de validação (receber score = taxa de verdadeiros positivos)
#enviar score e um csv com as probabilidades e os alfas para o firefly
#por x iterações:
    #modificar alfas na tabela
    #leer dados da base alimentada pelo sistema principal
    #validar dados com a base de validação (receber score = taxa de verdadeiros positivos)
    #enviar score e um csv com as probabilidades e os alfas para o firefly

# aaaaa

