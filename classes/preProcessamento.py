import xlrd
import xlwt


def replacing(cell, words):                                                     #recebe o conteúdo da célula e a lista de stop words
    for x in range(0, len(words)):                                              #enquanto houverem stop words a serem lidas
        oldWord = ' ' + words[x][0] + ' '                                       #removendo stop words no meio da frase
        newWord = ' ' + words[x][1] + ' '
        while (oldWord in cell):
            cell = cell.replace(oldWord, newWord)
        oldWord = ' ' + words[x][0] + '.'                                       #removendo stop words no fim da frase
        newWord = ' ' + words[x][1] + '.'
        while (oldWord in cell):
            cell = cell.replace(oldWord, newWord)
        oldWord = words[x][0].title() + ' '                                     #removendo stop words no início da frase
        newWord = words[x][1].title() + ' '
        while (oldWord in cell):
            cell = cell.replace(oldWord, newWord)
    while '  ' in cell:
        cell = cell.replace('  ', ' ')                                          #removendo espaços remanescentes
    if len(cell) > 0:
        if cell[0] == ' ':
            cell = cell[1:]
            cell = cell.capitalize()                                            #Colocando a primeira letra pra maiúsculo se necessário
    return cell


def removeStopWords(input, output, stopwords, sheets, columns):
    inBase = xlrd.open_workbook(input)                                          #Abre a base
    inSheets = []                                                               #prepara lista para receber as planilhas contidas na base
    outBase = xlwt.Workbook(output)                                             #cria uma base para saída
    outSheets = []                                                              #prepara lista para receber as planilhas de saída
    wordsBase = xlrd.open_workbook(stopwords)                                   #abre a base de stop words
    wordsSheet = wordsBase.sheet_by_index(0)                                    #seleciona a planilha de stop words
    words = []                                                                  #lista que recebera as palavras continas da base de stop words
    for x in range(1, wordsSheet.nrows):
        words.append([wordsSheet.row(x)[0].value, wordsSheet.row(x)[1].value])  #preenchendo a lista de stop words
    for x in range(0, inBase.nsheets):
        inSheets.append(inBase.sheet_by_index(x))                               #armazena as planilhas da base de entrada em uma lista
        outSheets.append(outBase.add_sheet(inSheets[x].name))                   #cria planilhas de saída com os mesmos nomes das de entrada
        for y in range(0, inSheets[x].nrows):                                   #navega entre as linhas
            for z in range(0, inSheets[x].ncols):                               #navega entre as colunas de cada linha
                cell = str(inSheets[x].row(y)[z].value)                         #pega as células uma a uma
                if sheets.__contains__(x) or len(sheets) == 0:
                    if columns.__contains__(z) or len(columns) == 0:
                        cell = replacing(cell, words)                           #remove as stop words se a planilha e a coluna foram setadas
                outSheets[x].write(y, z, cell)                                  #grava a célula (com stopwords removidas ou não) na plainha de saída
    outBase.save(output)                                                        #salva planilha de saída


"""
Chama a função enviando como parâmentros a base de dados:
1 - A base de dados
2 - Um nome para a saída da base formatada (se a base já existir será reescrita)
3 - A base de stop words
4 - Vetor INT com os índices das planilhas que terão stopwords removidas (vetor vazio = todas as planilhas)
5 - Vetor INT com os índices das colunas das planilhas que terão stopwords removidas (vetor vazio = todas as colunas)
"""
removeStopWords('../database/LIAR.xlsx', '../database/LIAR2.xls', '../database/stopwords.xlsx', [], [])

"""
- A base de stopwords precisa ter o formato da planilha de stopwords nesse exemplo, a primeira linha não é lida, são apenas labels
- As bases de entrada podem ser xlsx, mas a base de saída apenas xls
"""
