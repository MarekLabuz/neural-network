import math
import random


def func(s):
    return 1.0 / (1.0 + math.exp(-1.0 * s))
    # try:
    #  	exp = math.exp(-1 * S)
    #   except OverflowError:
    #   exp = sys.float_info.max
    # return (1 / (1 + exp))


def calculate_weighted_sum(input_synapses, weights):
    return reduce(lambda acc, (i, syn): acc + syn.output_value * weights[i], enumerate(input_synapses), 0)


class Input:
    def __init__(self, input_value):
        self.type = 'input'
        self.output_value = input_value


class Neuron:
    def __init__(self, input_synapses, _range={'from': -0.1, 'to': 0.1}):
        self.type = 'neuron'
        self.input_synapses = input_synapses
        self.output_synapses = []
        self.weights_inputs = map(lambda x: random.uniform(_range['from'], _range['to']), input_synapses)
        self.biasWeight = random.uniform(_range['from'], _range['to'])
        self.weights_outputs = []
        self.output_value = 0
        self.desired_value = None
        self.deltaParameter = 0
        self.error = 0
        self.learningRate = 0.1
        self.bias = 1.0

        for (i, syn) in enumerate(input_synapses):
            if syn.type == 'neuron':
                syn.output_synapses.append(self)
                syn.weights_outputs.append(self.weights_inputs[i])

    def calculate_output_value(self):
        weighted_sum = calculate_weighted_sum(self.input_synapses, self.weights_inputs) + self.biasWeight
        self.output_value = func(weighted_sum)

    def derivative(self):
        return (1.0 - self.output_value) * self.output_value

    def calculate_errors(self):
        if self.desired_value is not None:
            self.error = (self.desired_value - self.output_value)
        else:
            self.error = reduce(lambda acc, (i, syn):
                                acc + syn.error * self.weights_outputs[i] * syn.derivative(),
                                enumerate(self.output_synapses), 0)

    def change_weights(self):
        self.biasWeight += self.learningRate * self.error * self.bias * self.derivative()
        self.weights_inputs = map(lambda (syn, weight):
                                  weight + self.learningRate * self.error * syn.output_value,
                                  zip(self.input_synapses, self.weights_inputs))
