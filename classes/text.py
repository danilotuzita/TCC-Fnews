from classes.word import Word
from classes.phrase import Phrase


class Text:
    words = []  # tipo Word
    phrases = []  # tipo Phrase
    probability = 1  # probabilidade do texto

    def __init__(self, wrds=(), p=1):
        self.probability = p
        self.words.clear()
        for w in wrds:
            self.words.append(Word(w, self.probability))
        self.words.append(self.get_word(-1))

    def __del__(self):
        self.clear()

    def clear(self):
        self.words.clear()
        self.phrases.clear()
        self.probability = 1  # probabilidade do texto

    def set_words(self, w=()):
        self.words = w

    def get_word(self, i):
        if i < 0 or i >= len(self.words):
            return Word('_', self.probability)
        return self.words[i]

    def build_phrases(self, k):
        for i in range(len(self.words) - 1):
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

