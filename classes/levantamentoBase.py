import xlrd
import xlwt


def countSequences(input, output, sheets, collum):
    inBase = xlrd.open_workbook(input)
    inSheets = []
    outBase = xlwt.Workbook(output)
    outSheets = []
    sequences = []

    for x in range(0, inBase.nsheets):
        inSheets.append(inBase.sheet_by_index(x))
        if sheets.__contains__(x):
            for y in range(0, inSheets[x].nrows):
                for z in range(0, inSheets[x].ncols):
                    if collum == z:
                        cell = str(inSheets[x].row(y)[z].value)
                        words = cell.split()
                        for word in range(0, len(words)-2):
                            exist = 0
                            for item in sequences:
                                if (item[0] == words[word] + ' ' + words[word+1] + ' ' + words[word+2]):
                                    item[1] = item[1] + 1
                                    exist = 1
                                    break
                            if (exist == 0):
                                sequences.append([words[word] + ' ' + words[word+1] + ' ' + words[word+2], 1])
    outBase = xlwt.Workbook(output)
    outSheets.append(outBase.add_sheet('Sequence with 3'))
    for x in range(0, len(sequences)):
        outSheets[0].write(x, 0, sequences[x][0])
        outSheets[0].write(x, 1, sequences[x][1])
    outBase.save(output)


"""
Chama a função enviando como parâmentros a base de dados:
1 - A base de dados
2 - Um nome para a saída da base formatada (se a base já existir será reescrita)
3 - Vetor INT com os índices das planilhas que terão sequências contadas (vetor vazio = todas as planilhas)
4 - INT que representa qual coluna será contada
"""
countSequences('../database/raw_datasets/LIAR.xlsx', '../database/raw_datasets/saida.xls', [1], 2)

"""
- As bases de entrada podem ser xlsx, mas a base de saída apenas xls
"""