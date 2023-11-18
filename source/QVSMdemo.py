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

np.random.seed(42)

X, y = load_iris(return_X_y=True)
X = X[:100]
y = y[:100]
scaler = StandardScaler().fit(X)
X_scaled = scaler.transform(X)
y_scaled = 2 * (y - 0.5)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_scaled)

n_qubits = len(X_train[0])
dev_kernel = qml.device("lightning.qubit", wires=n_qubits)
projector = np.zeros((2**n_qubits, 2**n_qubits))
projector[0, 0] = 1

@qml.qnode(dev_kernel)
def kernel(x1, x2):
    AngleEmbedding(x1, wires=range(n_qubits))
    qml.adjoint(AngleEmbedding)(x2, wires=range(n_qubits))
    return qml.expval(qml.Hermitian(projector, wires=range(n_qubits)))

def kernel_matrix(A, B):
    return np.array([[kernel(a, b) for b in B] for a in A])

svm = SVC(kernel=kernel_matrix).fit(X_train, y_train)

predictions = svm.predict(X_test)
accuracy = accuracy_score(predictions, y_test)
print("Accuracy:", accuracy)

print("Number of quantum device evaluations:", dev_kernel.num_executions)

def circuit_evals_kernel(n_data, split):
    M = int(np.ceil(split * n_data))
    Mpred = n_data - M
    n_training = M * M
    n_prediction = M * Mpred
    return n_training + n_prediction

# Compute the number of circuit evaluations
n_evals = circuit_evals_kernel(len(X), len(X_train) / (len(X_train) + len(X_test)))
print("Number of circuit evaluations:", n_evals)

# Implementing variational training
dev_var = qml.device("lightning.qubit", wires=n_qubits)

@qml.qnode(dev_var, diff_method="parameter-shift")
def quantum_model(x, params):
    AngleEmbedding(x, wires=range(n_qubits))
    StronglyEntanglingLayers(params, wires=range(n_qubits))
    return qml.expval(qml.PauliZ(0))

def quantum_model_plus_bias(x, params, bias):
    return quantum_model(x, params) + bias

def hinge_loss(predictions, targets):
    all_ones = torch.ones_like(targets)
    hinge_loss = all_ones - predictions * targets
    hinge_loss = relu(hinge_loss)
    return hinge_loss

def quantum_model_train(n_layers, steps, batch_size):
    params = np.random.random((n_layers, n_qubits, 3))
    params_torch = torch.tensor(params, requires_grad=True)
    bias_torch = torch.tensor(0.0)

    opt = torch.optim.Adam([params_torch, bias_torch], lr=0.1)

    loss_history = []
    for i in range(steps):
        batch_ids = np.random.choice(len(X_train), batch_size)
        X_batch = X_train[batch_ids]
        y_batch = y_train[batch_ids]
        X_batch_torch = torch.tensor(X_batch, requires_grad=False)
        y_batch_torch = torch.tensor(y_batch, requires_grad=False)

        def closure():
            opt.zero_grad()
            preds = torch.stack(
                [quantum_model_plus_bias(x, params_torch, bias_torch) for x in X_batch_torch]
            )
            loss = torch.mean(hinge_loss(preds, y_batch_torch))
            current_loss = loss.detach().numpy().item()
            loss_history.append(current_loss)
            if i % 10 == 0:
                print("step", i, ", loss", current_loss)
            loss.backward()
            return loss

        opt.step(closure)

    return params_torch, bias_torch, loss_history

#def quantum_model_predict(X_pred, trained_params, trained_bias):
    #print(1)
    #p = []
    #for x in X_pred:
        #x_torch = torch.tensor(x)
        #pred_torch = quantum_model_plus_bias(x_tSure! Here's an example of a Python code that demonstrates how to implement a simple SVM using scikit-learn:

from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

iris = datasets.load_iris()
X = iris.data
y = iris.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
svm = SVC()
svm.fit(X_train, y_train)
y_pred = svm.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy: ", accuracy)

