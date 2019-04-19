# encoding: utf-8
from classes.word import Word
from classes.phrase import Phrase


class Text:
    words = []  # tipo Word
    phrases = []  # tipo Phrase
    probability = 1  # probabilidade do texto

    def __init__(self, wrds=(), p=1):
        self.probability = p
        self.words.clear()
        for w in wrds:  # cria uma Word para cada palavra do texto
            self.words.append(Word(w, self.probability))
        # self.words.append(self.get_word(-1))  # cria a palavra '_' no fim do texto (finalizador)

    def __del__(self):
        self.clear()  # limpa a variavel, estava mantendo os valores anteriores mesmo depois da variavel ser destruida

    def clear(self):
        self.words.clear()
        self.phrases.clear()
        self.probability = 1  # probabilidade do texto

    def set_words(self, w=()):  # seta as palavras do texto
        self.words = w

    def get_word(self, i):  # retorna a palavra na posição i
        if i < 0 or i >= len(self.words):
            return Word('_', self.probability)  # caso o indice não exista, retornar '_' (palavra finalizadora)
        return self.words[i]

    def build_phrases(self, k):  # cria as frases baseadas nas palavras no tamanho k
        n = len(self.words)  # numero de palavras
        offset = k - 1  # offset para não pegar mais os '_'
        for i in range(n - offset):
            wrds = []
            for j in range(k):  # k vezes:
                w = self.get_word(i + j)  # vai até a palavra i + j
                wrds.append(w)
            self.phrases.append(Phrase(words=wrds, k=k, p=self.probability))  # cria uma Phrase

    def size(self):
        return len(self.words)

    def set_probability(self, p=1):
        self.probability = p

    def print_phrases(self):
        for p in self.phrases:
            p.print()

    def print_text(self):
        p = '"'
        for w in self.words:
            p += w.value + ' '
        print(p + '"')

