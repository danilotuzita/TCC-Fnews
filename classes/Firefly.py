import random
import sys
import math


class FireflyProgram:
    def __init__(self):
        print("*** Begin firefly algorithm optimization ***")

        numFireflies = 40  # 15..40
        dim = 5
        maxEpochs = 1000
        seed = 0

        print("Setting numFireflies        = " + str(numFireflies))
        print("Setting problem dim         = " + str(dim))
        print("Setting maxEpochs           = " + str(maxEpochs))
        print("Setting initialization seed = " + str(seed))

        print("\n### STARTING FIREFLY ALGORITHM ###")
        best_position = self.solve(numFireflies, dim, seed, maxEpochs)
        print("### FINISHED ###")

        print("Best solution found: ")
        print("x = ")
        self.showVector(best_position, 4, True)
        z = self.michalewicz(best_position)

        print("Value of function at best position = ")
        print(z)  # alguma coisa

        error = self.error(best_position)
        print("Error at best position = ")
        print(error)  # alguma coisa

        print("*** End of firefly algorithm optimization ***")

    def showVector(self, v, dec, nl):
        for best in v:
            print(best, "F", dec, " ")
        if nl:
            print("")

    def solve(self, numFireflies, dim, seed, maxEpochs):
        rnd = random.seed(seed)
        minX = -10.0
        maxX = 10.0

        b0 = 1.0
        g = 1.0
        a = 0.20

        displayInterval = maxEpochs / 10

        bestError = sys.float_info.max
        bestPosition = []
        swarm = []
        for index in range(0, numFireflies):
            swarm.append(Firefly(dim))
            for indexB in range(0, dim):
                swarm[index].position.append((maxX - minX) * random.uniform(0, 1) + minX)
            swarm[index].error = self.error(swarm[index].position)

            swarm[index].intensity = 1 / (swarm[index].error + 1)

            if swarm[index].error < bestError:
                bestError = swarm[index].error

                for indexB in range(0, dim):
                    bestPosition.append(swarm[index].position[indexB])
        epoch = 0
        while epoch < maxEpochs:
            if epoch % displayInterval == 0 and epoch < maxEpochs:
                sEpoch = str(epoch)
                print("epoch = ", sEpoch)
                print("error = ", bestError)
            epoch += 1
            for index in range(0, len(swarm)):
                for indexB in range(0, len(swarm)):
                    if swarm[index].intensity < swarm[indexB].intensity:
                        r = self.distance(swarm[index].position, swarm[indexB].position)

                        beta = b0 * math.exp(-g * r * r)

                        for indexC in range(0, dim):
                            swarm[index].position[indexC] += beta * (swarm[indexB].position[indexC] - swarm[index].position[indexC])
                            swarm[index].position[indexC] += a * (random.uniform(0, 1) * 0.5) #verificar
                            if swarm[index].position[indexC] < minX:
                                swarm[index].position[indexC] = (maxX - minX * random.uniform(0, 1) + minX)
                            if swarm[index].position[indexC] > maxX:
                                swarm[index].position[indexC] = (maxX - minX * random.uniform(0, 1) + minX)
                        swarm[index].error = self.error(swarm[index].position)
                        swarm[index].intensity = 1 / (swarm[index].error + 1)
            erros = []
            vetor = []
            for x in swarm:
                erros.append(x.error)
                vetor.append([x.error, x])
            erros.sort()
            vetorOrdenado = []
            for x in erros:
                for y in vetor:
                    if x == y[0]:
                        vetorOrdenado.append(y[1])

            if vetorOrdenado[0].error < bestError:
                bestError = vetorOrdenado[0].error
                for index in range(0, dim):
                    bestPosition[index] = vetorOrdenado[0].position[index]
            epoch += 1
        return bestPosition

    def distance(self, posA, posB):
        ssd = 0.0
        for index, pos in enumerate(posA):
            ssd += (posA[index] - posB[index]) * (posA[index] - posB[index])
        return math.sqrt(ssd)

    def michalewicz(self, xValues):
        result = 0.0
        for index, v in enumerate(xValues):
            a = math.sin(v)
            b = math.sin((index + 1) * v * v / math.pi)
            c = math.pow(b, 20)
            result += a + c
        return -1.0 * result

    def error(self, xValues):
        dim = len(xValues)
        trueMin = 0.0
        if dim == 2:
            trueMin = -1.8013
        elif dim == 5:
            trueMin = -4.687658
        elif dim == 10:
            trueMin = -9.66015
        calculated = self.michalewicz(xValues)
        return (trueMin - calculated) * (trueMin - calculated)


class Firefly:
    def __init__(self, dim):
        self.position = []
        self.error = 0.0
        self.intensity = 0.0

    def compareTo(self, other):
        if self.error < other.error:
            return -1
        elif self.error > other.error:
            return 1
        else:
            return 0


firefly = FireflyProgram()