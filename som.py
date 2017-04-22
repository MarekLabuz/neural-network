import neuron
import network
import random
import math
import utils
from PIL import Image, ImageDraw

Neuron = neuron.Neuron
Input = neuron.Input

A = 1000


def euler_distance(n1, n2):
    return abs(n1.i - n2.i) + abs(n1.j - n2.j)


class Node (Neuron):
    def __init__(self, i, j, _inputs, radius=4):
        Neuron.__init__(self, _inputs, {'from': 0.01, 'to': 0.1})
        self.i = i
        self.j = j
        self.colors = [0, 0, 0]
        self.radius = radius
        self.learningRate = 1.0

    def __str__(self):
        return ', '.join(map(lambda color: str(color), self.colors))

    def improve_weights(self, distance, time):
        radius = self.radius * math.exp(-time / A)
        learning_rate = self.learningRate * math.exp(-time / A)
        k = distance**2 / (2*(radius**2))
        delta = math.exp(-k)
        self.weights_inputs = map(lambda (syn, weight): weight + delta * learning_rate * (syn.output_value - weight),
                                  zip(self.input_synapses, self.weights_inputs))


class Grid:
    def __init__(self, _n, _inputs):
        self.grid = []
        self.inputs = _inputs
        self.t = 0
        self.n = _n
        self.inputs_indexes = range(len(self.inputs))
        self.layer = []
        for i in range(_n):
            self.grid.append([])
            for j in range(_n):
                node = Node(i, j, _inputs)
                self.grid[i].append(node)
                self.layer.append(node)

    def __str__(self):
        result = ''
        for _row in self.grid:
            result += '| '
            for node in _row:
                result += str(node) + ' | '
            result += '\n'

        return result

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

    def set_inputs(self, _inputs):
        for (syn, _input) in zip(self.inputs, _inputs):
            syn.output_value = _input

    def execute(self, _inputs, desired_values):
        self.set_inputs(_inputs)
        random_sample = random.sample(self.inputs_indexes, 4)
        winner = self.get_winner(random_sample)['node']
        iris_index = desired_values.index(max(desired_values))
        winner.colors[iris_index] += 1
        for _row in self.grid:
            for node in _row:
                distance = euler_distance(winner, node)
                node.improve_weights(distance, self.t)
        self.t += 1.0
        return self

    def run(self, _data, r=50):
        for _n in range(r):
            for _iris in _data:
                self.execute(_iris[1], _iris[0])

    def draw(self, node_width=30):
        image = Image.new("RGB", (node_width * self.n, node_width * self.n), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        for _row in self.grid:
            for node in _row:
                color_sum = sum(node.colors)
                colors = map(lambda color: 0 if color_sum == 0 else 255 * color / color_sum, node.colors)
                draw.rectangle(
                    (node.i * node_width, node.j * node_width, (node.i + 1) * node_width, (node.j + 1) * node_width),
                    fill=('rgb' + str(tuple(colors)))
                )
        image.show()

    def calc_output_value(self, _inputs):
        self.set_inputs(_inputs)
        for node in self.layer:
            node.calculate_output_value()

data = utils.read_csv('iris.csv')
random.shuffle(data)

inputs = [Input(3), Input(5), Input(1), Input(8)]
grid = Grid(5, inputs)
grid.run(data, 50)

Network = network.Network
network = Network(grid.layer)

grid.draw()

n = 75
dataTrain = data[:n]
dataTest = data[n:]

newData = []

for i in range(200):
    newData += dataTrain

for iris in newData:
    grid.calc_output_value(iris[1])
    network.set_desired_values(iris[0])
    network.execute(1)

counter = 0

for iris in dataTest:
    maxIris = iris[0].index(max(iris[0]))
    grid.calc_output_value(iris[1])
    network.set_desired_values(iris[0])
    network.execute(1)
    networkResult = map(lambda x: x.output_value, network.last_neuron_layer)
    maxOutput = networkResult.index(max(networkResult))
    if maxOutput == maxIris:
        counter += 1

data_length = len(dataTest)
print 'RESULT', 100 * counter / data_length, '%'
