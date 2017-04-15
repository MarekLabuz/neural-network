import random
import math
import sys
import csv


def function(S):
	try:
		exp = math.exp(-1 * S)
	except OverflowError:
		exp = sys.float_info.max

	return (1 / (1 + exp))


def calculate_weighted_sum(input_synapses, weights):
	return reduce(lambda acc, (i, curr): acc + curr * weights[i], enumerate(map(lambda syn: syn.output_value, input_synapses)), 0)

# -----------------------------------------------------------------------------------------------------------------------------------------------


class Input:
	def __init__(self, input_value):
		self.type = 'input'
		self.output_value = input_value

class Neuron:
	def __init__(self, input_synapses):
		self.type = 'neuron'
		self.input_synapses = input_synapses
		self.output_synapses = []
		self.weights_inputs = map(lambda x: random.uniform(-1.0, 1.0), input_synapses)
		self.weights_outputs = []
		self.output_value = 0
		self.desired_value = None
		self.deltaParameter = 0
		self.error = 0

		for (i, syn) in enumerate(input_synapses):
			if syn.type == 'neuron':
				syn.output_synapses.append(self)
				syn.weights_outputs.append(self.weights_inputs[i])

	def calculate_output_value(self):
		weighted_sum = calculate_weighted_sum(self.input_synapses, self.weights_inputs)
		self.output_value = function(weighted_sum)

	def derivative(self):
		return (1.0 - self.output_value) * self.output_value

	def calculate_errors(self):
		if self.desired_value is not None:
			self.error = (self.desired_value - self.output_value) * self.derivative()
		else:
			self.error = reduce(lambda acc, (i, syn): acc + syn.error * self.weights_outputs[i] * syn.derivative(), enumerate(self.output_synapses), 0)

	def change_weights(self):
		self.weights_inputs = map(lambda (i, weight): weight + 0.1 * self.error * self.input_synapses[i].output_value, enumerate(self.weights_inputs))

# -----------------------------------------------------------------------------------------------------------------------------------------------


def printValues(args):
	for arg in args:
		print map(lambda x: x.output_value, arg)


def execute(command, layers):
	for layer in layers:
		for neuron in layer:
			getattr(neuron, command)()


def divide_into_subsets(data, k):
	subset_length = len(data) / k
	return map(lambda i: data[(i * subset_length):((i + 1) * subset_length)], range(k))


def select_train_test(data, i):
	return { 'train': reduce(lambda acc, curr: acc + curr, (data[0:i] + data[(i + 1):]), []), 'test': data[i] }


def train_and_test(data):
	train = data['train']
	test = data['test']


# -----------------------------------------------------------------------------------------------------------------------------------------------


class Network:
	def __init__(self, number_of_inputs):
		self.inputs = map(lambda x: Input(x), range(number_of_inputs))
		self.first_neuron_layer = [Neuron(self.inputs), Neuron(self.inputs)]
		self.second_neuron_layer = [Neuron(self.first_neuron_layer), Neuron(self.first_neuron_layer), Neuron(self.first_neuron_layer)]
		self.last_neuron_layer = [Neuron(self.second_neuron_layer), Neuron(self.second_neuron_layer), Neuron(self.second_neuron_layer)]

		self.order = [self.first_neuron_layer, self.second_neuron_layer, self.last_neuron_layer]


	def set_inputs(self, inputs):
		for (i, syn) in enumerate(self.inputs):
			syn.output_value = inputs[i]


	def set_desired_values(self, desired_values):
		for (i, syn) in enumerate(self.last_neuron_layer):
			syn.desired_value = desired_values[i]

	def calc_and_print(self):
		execute('calculate_output_value', self.order)
		printValues([self.inputs])
		printValues(self.order)
		print '---'

	def execute(self, n):
		print '---'
		self.calc_and_print()

		for i in range(n):
			execute('calculate_errors', reversed(self.order))
			execute('change_weights', self.order)
			execute('calculate_output_value', self.order)
			# printValues([self.last_neuron_layer])
			# print '---'

	def run(self, inputs, desired_values, n):
		self.set_inputs(inputs)
		self.set_desired_values(desired_values)
		self.execute(n)
		return map(lambda x: x.output_value, self.last_neuron_layer)


# -----------------------------------------------------------------------------------------------------------------------------------------------

# learning_data = [
# 	{ 'inputs': [0.1, 0.2, 0.3], 'outputs': [0.5, 0.8] },
# 	{ 'inputs': [0.3, 0.6, 0.8], 'outputs': [0.1, 0.9] },
# 	{ 'inputs': [0.2, 0.4, 0.9], 'outputs': [0.3, 0.6] },
# 	{ 'inputs': [0.4, 0.7, 0.4], 'outputs': [0.7, 0.4] }
# ]

# subsets = divide_into_subsets(learning_data, 4)
# data = select_train_test(subsets, 3)
# train_and_test(data)

# network = Network(4)

data = []

desired_values = {
	'Iris-setosa': [1.0, 0.0, 0.0],
	'Iris-versicolor': [0.0, 1.0, 0.0],
	'Iris-virginica': [0.0, 0.0, 1.0]
}

with open('iris.csv', 'rb') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=',')
	for row in spamreader:
		data.append([desired_values[row[4]]] + [map(lambda x: float(x), row[0:4])])
		# data[row[4]].append(map(lambda x: float(x), row[0:4]))
		# print row


# random.shuffle(data)

# print data

network = Network(4)

result = 0

newData = []

for i in range(20):
	newData += data

random.shuffle(newData)

for iris in newData:
	print '-------'
	print iris[1], iris[0]
	print network.run(iris[1], iris[0], 1)
	print '-------'

data_length = len(data)
counter = 0

for iris in data:
	print '-------'
	maxIris = iris[0].index(max(iris[0]))
	networkResult = network.run(iris[1], iris[0], 0)
	maxOutput = networkResult.index(max(networkResult))
	if maxOutput == maxIris:
		counter += 1

	print maxOutput, networkResult, maxIris, iris[0], iris[1]
	print '-------'

result = 100 * counter / data_length

print 'RESULT', 100 * counter / data_length, '%'
# -----------------------------------------------------------------------------------------------------------------------------------------------

