import word, phrase


class Text:
    words = []
    phrases = []
    probability = 1

    def __init__(self, words=()):
        self.words = words

    def make_text(self, words):
        self.words = []
        for w in words:
            self.words.append(word.Word(w, self.probability))

    def build_phrases(self, k):
        for i in range(len(self.words)):
            p = []
            for j in range(k):
                try:
                    w = self.words[i + j]
                except IndexError:
                    w = word.Word('', self.probability)
                p.append(w)
            self.phrases.append(phrase.Phrase(p, k))

    def size(self):
        return len(self.words)

    def set_probability(self, p=1):
        self.probability = p

    def print_phrases(self):
        for p in self.phrases:
            p.print()
