
class Phrase:
    k = 1
    words = []
    probability = 1
    alpha = 1

    def __init__(self, words=(), k=1):
        self.words = words
        self.k = k

    def set_probability(self, p=1):
        self.probability = p

    def set_alpha(self, alpha=1):
        self.alpha = alpha

    def print(self):
        p = ''
        for w in self.words:
            p += "'" + w.value + "', "

        print(p)
