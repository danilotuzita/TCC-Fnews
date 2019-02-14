# encoding: utf-8
class Word:
    value = ""  # palavra
    probability = 1  # probabilidade da palavra
    count = 1  # contagem para a média

    def __init__(self, value="", p=1, count=1):
        self.value = value
        self.probability = p
        self.count = count

    def set_probability(self, p=1):
        self.probability = p

    def inc_count(self):  # função para aumentar o contador de existencia da palavra
        self.count = self.count + 1

    def get_id(self, db, print_values=False):
        return db.get_word_id(self, print_values)

    def avg_prob(self, new_prob):
        self.probability = ((1 / (self.count)) * (self.count - 1) * self.probability) + (1 / self.count) * new_prob
