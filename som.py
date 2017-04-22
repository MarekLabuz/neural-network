import neuron
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
        self.weights_inputs = map(lambda (syn, weight): delta * learning_rate * (syn.output_value - weight),
                                  zip(self.input_synapses, self.weights_inputs))


class Grid:
    def __init__(self, _n, _inputs):
        self.grid = []
        self.inputs = _inputs
        self.t = 0
        self.n = _n
        self.inputs_indexes = range(len(self.inputs))
        for i in range(_n):
            self.grid.append([])
            for j in range(_n):
                self.grid[i].append(Node(i, j, _inputs))

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

    def run(self, _inputs, desired_values):
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

data = utils.read_csv('iris.csv')

inputs = [Input(0), Input(5), Input(1), Input(8)]
grid = Grid(4, inputs)

random.shuffle(data)

for n in range(50):
    for iris in data:
        grid.run(iris[1], iris[0])

grid.draw()
