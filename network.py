import neuron
import utils

Neuron = neuron.Neuron
Input = neuron.Input

execute = utils.execute


class Network:
    def __init__(self, number_of_inputs):
        self.inputs = map(lambda x: Input(x), range(number_of_inputs))
        self.first_neuron_layer = [Neuron(self.inputs), Neuron(self.inputs), Neuron(self.inputs), Neuron(self.inputs)]
        self.second_neuron_layer = [
            Neuron(self.first_neuron_layer),
            Neuron(self.first_neuron_layer),
            Neuron(self.first_neuron_layer),
            Neuron(self.first_neuron_layer),
            Neuron(self.first_neuron_layer),
            Neuron(self.first_neuron_layer),
            Neuron(self.first_neuron_layer),
            Neuron(self.first_neuron_layer),
            Neuron(self.first_neuron_layer),
            Neuron(self.first_neuron_layer)
        ]
        self.last_neuron_layer = [
            Neuron(self.second_neuron_layer),
            Neuron(self.second_neuron_layer),
            Neuron(self.second_neuron_layer)
        ]

        self.order = [self.first_neuron_layer, self.second_neuron_layer, self.last_neuron_layer]

    def set_inputs(self, inputs):
        for (i, syn) in enumerate(self.inputs):
            syn.output_value = inputs[i]

    def set_desired_values(self, desired_values):
        for (i, syn) in enumerate(self.last_neuron_layer):
            syn.desired_value = desired_values[i]

    def calc_and_print(self):
        execute('calculate_output_value', self.order)
        # print_values([self.inputs])
        # print_values(self.order)
        # print '---'

    def execute(self, n):
        # print '---'
        self.calc_and_print()

        for i in range(n):
            execute('calculate_errors', reversed(self.order))
            execute('change_weights', self.order)
            execute('calculate_output_value', self.order)
            # print_values([self.last_neuron_layer])
            # print '---'

    def run(self, inputs, desired_values, n):
        self.set_inputs(inputs)
        self.set_desired_values(desired_values)
        self.execute(n)
        return map(lambda x: x.output_value, self.last_neuron_layer)
