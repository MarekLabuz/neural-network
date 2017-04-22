import csv


def print_values(args):
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
    return {'train': reduce(lambda acc, curr: acc + curr, (data[0:i] + data[(i + 1):]), []), 'test': data[i]}


def train_and_test(data):
    train = data['train']
    test = data['test']

desired_values = {
    'Iris-setosa': [1.0, 0.0, 0.0],
    'Iris-versicolor': [0.0, 1.0, 0.0],
    'Iris-virginica': [0.0, 0.0, 1.0]
}


def read_csv(file_name):
    data = []
    with open(file_name, 'rb') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        for row in reader:
            data.append([desired_values[row[4]]] + [map(lambda x: float(x), row[0:4])])
    return data

# learning_data = [
# 	{ 'inputs': [0.1, 0.2, 0.3], 'outputs': [0.5, 0.8] },
# 	{ 'inputs': [0.3, 0.6, 0.8], 'outputs': [0.1, 0.9] },
# 	{ 'inputs': [0.2, 0.4, 0.9], 'outputs': [0.3, 0.6] },
# 	{ 'inputs': [0.4, 0.7, 0.4], 'outputs': [0.7, 0.4] }
# ]

# subsets = divide_into_subsets(learning_data, 4)
# data = select_train_test(subsets, 3)
# train_and_test(data)
