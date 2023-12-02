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

from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

import matplotlib.pyplot as plt


def circuit_evals_kernel(n_data, split):
    M = int(np.ceil(split * n_data))
    Mpred = n_data - M
    n_training = M * M
    n_prediction = M * Mpred
    return n_training + n_prediction

def hinge_loss(predictions, targets):
    all_ones = torch.ones_like(targets)
    hinge_loss = all_ones - predictions * targets
    hinge_loss = relu(hinge_loss)
    return hinge_loss

def quantum_model_train(n_layers, steps, batch_size, n_qubits , X_train, y_train):
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

def quantum_model_predict(X_pred, trained_params, trained_bias):
    p = []
    for x in X_pred:

        x_torch = torch.tensor(x)
        pred_torch = quantum_model_plus_bias(x_torch, trained_params, trained_bias)
        pred = pred_torch.detach().numpy().item()
        if pred > 0:
            pred = 1
        else:
            pred = -1

        p.append(pred)
    return p

def circuit_evals_variational(n_data, n_params, n_steps, shift_terms, split, batch_size):

    M = int(np.ceil(split * n_data))
    Mpred = n_data - M

    n_training = n_params * n_steps * batch_size * shift_terms
    n_prediction = Mpred

    return n_training + n_prediction

def model_evals_nn(n_data, n_steps, split, batch_size):


    M = int(np.ceil(split * n_data))
    Mpred = n_data - M

    n_training = n_steps * batch_size
    n_prediction = Mpred

    return n_training + n_prediction

if __name__ == "__main__":
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

    n_evals = circuit_evals_kernel(len(X), len(X_train) / (len(X_train) + len(X_test)))
    print("Number of circuit evaluations:", n_evals)

    dev_var = qml.device("lightning.qubit", wires=n_qubits)

    @qml.qnode(dev_var, diff_method="parameter-shift")
    def quantum_model(x, params):
        AngleEmbedding(x, wires=range(n_qubits))
        StronglyEntanglingLayers(params, wires=range(n_qubits))
        return qml.expval(qml.PauliZ(0))

    def quantum_model_plus_bias(x, params, bias):
        return quantum_model(x, params) + bias
    

    n_layers = 2
    batch_size = 25
    steps = 100
    trained_params, trained_bias, loss_history = quantum_model_train(n_layers, steps, batch_size, n_qubits, X_train, y_train)
                                                                     
    pred_test = quantum_model_predict(X_test, trained_params, trained_bias)
    print("accuracy on test set:", accuracy_score(pred_test, y_test))

    plt.plot(loss_history)
    plt.ylim((0, 1))
    plt.xlabel("steps")
    plt.ylabel("cost")
    plt.show()

    circuit_evals_variational(
    n_data=len(X),
    n_params=len(trained_params.flatten()),
    n_steps=steps,
    shift_terms=2,
    split=len(X_train) /(len(X_train) + len(X_test)),
    batch_size=batch_size,
    )
    variational_training1 = []
    variational_training2 = []
    kernelbased_training = []
    nn_training = []
    x_axis = range(0, 2000, 100)

    for M in x_axis:

        var1 = circuit_evals_variational(
            n_data=M, n_params=M, n_steps=M,  shift_terms=2, split=0.75, batch_size=1
        )
        variational_training1.append(var1)

        var2 = circuit_evals_variational(
            n_data=M, n_params=round(np.sqrt(M)), n_steps=M,
            shift_terms=2, split=0.75, batch_size=1
        )
        variational_training2.append(var2)

        kernel = circuit_evals_kernel(n_data=M, split=0.75)
        kernelbased_training.append(kernel)

        nn = model_evals_nn(
        n_data=M, n_steps=M, split=0.75, batch_size=1
        )

        nn_training.append(nn)

    plt.plot(x_axis, nn_training, linestyle='--', label="neural net")
    plt.plot(x_axis, variational_training1, label="var. circuit (linear param scaling)")
    plt.plot(x_axis, variational_training2, label="var. circuit (srqt param scaling)")
    plt.plot(x_axis, kernelbased_training, label="(quantum) kernel")
    plt.xlabel("size of data set")
    plt.ylabel("number of evaluations")
    plt.legend()
    plt.tight_layout()
    plt.show()
