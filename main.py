import random
import network
import neuron
import utils

Network = network.Network
Input = neuron.Input
inputs = map(lambda x: Input(x), range(4))
network = Network(inputs)

data = utils.read_csv('iris.csv')
random.shuffle(data)
n = 75
dataTrain = data[:n]
dataTest = data[n:]

newData = []

for i in range(200):
    newData += dataTrain

for iris in newData:
    print network.run(iris[1], iris[0], 1)

counter = 0

for iris in dataTest:
    maxIris = iris[0].index(max(iris[0]))
    networkResult = network.run(iris[1], iris[0], 0)
    maxOutput = networkResult.index(max(networkResult))
    if maxOutput == maxIris:
        counter += 1

data_length = len(dataTest)
print 'RESULT', 100 * counter / data_length, '%'
