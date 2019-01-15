class Phrase:
    k = 1
    words = []
    probability = 1
    alpha = 1

    def __init__(self, words=(), k=1, p=1, a=1):
        self.k = k
        self.words = words
        self.probability = p
        self.alpha = a

    def set_probability(self, p=1):
        self.probability = p

    def set_alpha(self, alpha=1):
        self.alpha = alpha

    def print(self):
        p = ''
        for w in self.words:
            p += "'" + w.value + "', "

        print(p)
