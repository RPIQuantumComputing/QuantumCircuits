import numpy as np
import torch
from torch.nn.functional import relu

from sklearn.svm import SVC
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

import pennylane as qml
from pennylane.templates import AngleEmbedding, StronglyEntanglingLayers
from pennylane.operation import Tensor

import matplotlib.pyplot as plt

# Load the Iris dataset
#data = load_iris()
#X, y = data.data, data.target

# Split the data into training and testing sets
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize the features
#scaler = StandardScaler()
#X_train = scaler.fit_transform(X_train)
#X_test = scaler.transform(X_test)

class QuantumVectorSupportMachine:
    def __init__(self, n_qubits=2, n_layers=1, encoding='angle', quantum_device='default.qubit'):
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.encoding = encoding
        self.quantum_device = quantum_device

    def fit(self, X, y):

        if self.encoding == 'angle':
            self._feature_map = AngleEmbedding(X, wires=range(self.n_qubits))
        else:
            raise ValueError(f"Unsupported encoding type: {self.encoding}")

        self._circuit = qml.QNode(self._circuit_template, qml.device(self.quantum_device, wires=self.n_qubits))
        self._cost_fn = qml.Variance if len(np.unique(y)) == 2 else qml.CrossEntropyLoss

        self._optimizer = qml.AdamOptimizer()

        self._params = np.random.uniform(size=(self.n_layers, self.n_qubits, 3))

        def cost_fn(params):
            self._circuit(params)
            return self._cost_fn(self._circuit.draw()[-1])(y)

        for _ in range(10):
            self._params = self._optimizer.step(cost_fn, self._params)

    def predict(self, X):
        n_samples, n_features = X.shape
        predictions = np.zeros(n_samples)

        for i in range(n_samples):
            self._feature_map(X[i])
            predictions[i] = self._circuit(self._params)

        return predictions

    def _circuit_template(self, params):
        for layer in range(self.n_layers):
            StronglyEntanglingLayers(params[layer], wires=range(self.n_qubits))

# Load the Iris dataset
data = load_iris()
X, y = data.data, data.target

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize the features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Create an instance of QuantumVectorSupportMachine
qvsm = QuantumVectorSupportMachine(n_qubits=2, n_layers=3, encoding='angle', quantum_device='default.qubit')

# Train the model
qvsm.fit(X_train, y_train)

# Make predictions on the test set
y_pred = qvsm.predict(X_test)

# Evaluate the accuracy
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)
