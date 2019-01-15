class Word:
    value = ""
    probability = 1

    def __init__(self, value="", p=1):
        self.value = value
        self.probability = p

    def set_probability(self, p=1):
        self.probability = p
