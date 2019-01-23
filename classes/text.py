from classes.word import Word
from classes.phrase import Phrase


class Text:
    words = []  # tipo Word
    phrases = []  # tipo Phrase
    probability = 1  # probabilidade do texto

    def __init__(self, wrds=(), p=1):
        self.probability = p
        self.words = []
        for w in wrds:
            self.words.append(Word(w, self.probability))  # incluir checagem de igual

    def set_words(self, w=()):
        self.words = w

    def get_word(self, i):
        try:
            return self.words[i]
        except IndexError:
            return Word('', self.probability)

    def build_phrases(self, k):
        for i in range(len(self.words)):
            wrds = []
            for j in range(k):
                w = self.get_word(i + j)
                wrds.append(w)
            self.phrases.append(Phrase(words=wrds, k=k, p=self.probability))

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

