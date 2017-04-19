import random
import csv
import network

Network = network.Network

data = []

desired_values = {
    'Iris-setosa': [1.0, 0.0, 0.0],
    'Iris-versicolor': [0.0, 1.0, 0.0],
    'Iris-virginica': [0.0, 0.0, 1.0]
}

with open('iris.csv', 'rb') as csv_file:
    reader = csv.reader(csv_file, delimiter=',')
    for row in reader:
        data.append([desired_values[row[4]]] + [map(lambda x: float(x), row[0:4])])

network = Network(4)

random.shuffle(data)

n = 75
newData = []
dataTrain = data[:n]
dataTest = data[n:]

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
