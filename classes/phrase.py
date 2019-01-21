class Phrase:
    k = 1 #tamanho da frase???
    words = [] #conjunto de palavras
    probability = 1 #probabilidade de ser falso / verdadeiro ???
    alpha = 1 #o que é???
    count = 1 #quantidade de vezes que a frase apareceu, para calcular média

    def __init__(self, words=(), k=1, p=1, a=1, count=1):
        self.k = k
        self.words = words
        self.probability = p
        self.alpha = a
        self.count = count

    def set_probability(self, p=1):
        self.probability = p

    def set_alpha(self, alpha=1):
        self.alpha = alpha

    def print(self):
        p = ''
        for w in self.words:
            p += "'" + w.value + "', "

        print(p)

    def inc_count(self):            #função para aumentar o contador de existencia da palavra
        self.count = self.count + 1

    def avg_prob(self, new_prob):
        self.probability = ((1/(self.count))*(self.count-1)*self.probability)+(1/self.count)*new_prob
