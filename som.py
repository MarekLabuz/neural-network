import csv
import neuron

Neuron = neuron.Neuron
Input = neuron.Input

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
    def __init__(self, n, _inputs):
        self.grid = []
        for i in range(n):
            self.grid.append([])
            for j in range(n):
                self.grid[i].append(Node(i, j, _inputs))

    def __str__(self):
        result = ''
        for r in self.grid:
            result += '| '
            for node in r:
                result += str(node) + ' | '
            result += '\n'

        return result


inputs = [Input(3), Input(5), Input(1), Input(8)]
grid = Grid(4, inputs)

print grid
