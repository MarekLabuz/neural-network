import csv
import neuron
import random
import math

Neuron = neuron.Neuron
Input = neuron.Input

alpha = 1000

with open('iris.csv', 'rb') as csv_file:
    reader = csv.reader(csv_file, delimiter=',')
    for row in reader:
        print ''
        # data.append([desired_values[row[4]]] + [map(lambda x: float(x), row[0:4])])


class Node (Neuron):
    def __init__(self, i, j, _inputs):
        Neuron.__init__(self, _inputs, {'from': 0.01, 'to': 0.1})
        self.i = i
        self.j = j
        self.table = [0, 0, 1]

    def __str__(self):
        return '%d, %d' % (self.i, self.j)


class Grid:
    def __init__(self, n, _inputs, initial_radius):
        self.grid = []
        self.inputs = _inputs
        self.initial_radius = initial_radius
        self.t = 0
        self.inputs_indexes = range(len(self.inputs))
        for i in range(n):
            self.grid.append([])
            for j in range(n):
                self.grid[i].append(Node(i, j, _inputs))

    def __str__(self):
        result = ''
        for _row in self.grid:
            result += '| '
            for node in _row:
                result += str(node) + ' | '
            result += '\n'

        return result

    def get_radius(self):
        return self.initial_radius * math.exp(-self.t / alpha)

    def get_random_sample(self, k=2):
        return random.sample(self.inputs_indexes, k)

    def get_winner(self, sample):
        distances = []
        for _row in self.grid:
            for node in _row:
                sum_dist = 0
                for index in sample:
                    sum_dist += math.pow(self.inputs[index].output_value - node.weights_inputs[index], 2)
                dist = math.sqrt(sum_dist)
                distances.append({'node': node, 'dist': dist})
        return min(distances, key=lambda d: d['dist'])

    def run(self):
        random_sample = self.get_random_sample()
        print self.get_winner(random_sample)


inputs = [Input(3), Input(5), Input(1), Input(8)]
grid = Grid(4, inputs)

grid.run()

# print max([{'node': 'a', 'dist': 0}, {'node': 'b', 'dist': 3}, {'node': 'c', 'dist': -3}], key=lambda t: t['dist'])
