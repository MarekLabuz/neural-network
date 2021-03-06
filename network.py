import neuron
import utils

Neuron = neuron.Neuron
Input = neuron.Input

execute = utils.execute


class Network:
    def __init__(self, input_layer):
        self.inputs = input_layer
        self.first_neuron_layer = [Neuron(self.inputs), Neuron(self.inputs), Neuron(self.inputs), Neuron(self.inputs)]
        self.last_neuron_layer = [
            Neuron(self.first_neuron_layer),
            Neuron(self.first_neuron_layer),
            Neuron(self.first_neuron_layer)
        ]

        self.order = [self.first_neuron_layer, self.last_neuron_layer]

    def set_inputs(self, inputs):
        for (i, syn) in enumerate(self.inputs):
            syn.output_value = inputs[i]

    def set_desired_values(self, desired_values):
        for (i, syn) in enumerate(self.last_neuron_layer):
            syn.desired_value = desired_values[i]

    def execute(self, n):
        execute('calculate_output_value', self.order)
        for i in range(n):
            execute('calculate_output_value', self.order)
            execute('calculate_errors', reversed(self.order))
            execute('change_weights', self.order)

        execute('calculate_output_value', self.order)

    def run(self, inputs, desired_values, n):
        self.set_inputs(inputs)
        self.set_desired_values(desired_values)
        self.execute(n)
        return map(lambda x: x.output_value, self.last_neuron_layer)
