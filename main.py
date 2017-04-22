import random
import network
import utils

Network = network.Network
network = Network(4)

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
