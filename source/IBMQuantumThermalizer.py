#!/usr/bin/env python
# coding: utf-8

# In[83]:


from qiskit.circuit import Parameter
import pennylane as qml
from matplotlib import pyplot as plt
import numpy as np
from numpy import array
import scipy
from scipy.optimize import minimize
import networkx as nx
import seaborn
import itertools
from qiskit.circuit import QuantumCircuit
import random
from qiskit.opflow import PauliSumOp, I, X, Y, Z
from qiskit.opflow import PauliOp, PauliSumOp, I, X, Y, Z
import networkx as nx
import numpy as np
from qiskit.opflow import OperatorBase
from qiskit.quantum_info import Pauli

# Define the interaction graph and the number of qubits
nr_qubits = 10

interaction_graph = nx.cycle_graph(nr_qubits)

# Helper function to generate the tensor product term for each interaction
def generate_term(i, j, op):
    # Initialize term with identity operators
    term = [I for _ in range(nr_qubits)]
    # Set the specified Pauli operator on qubits i and j
    term[i] = op
    term[j] = op
    # Combine the operators into a single term using the tensor product
    return PauliOp(Pauli(''.join([str(p) for p in term])))

# Initialize an empty list to hold the terms of the Hamiltonian
hamiltonian_terms = []

# Iterate through the edges of the interaction graph
for edge in interaction_graph.edges:
    i, j = edge
    # Generate XX, YY, and ZZ terms for each edge
    xx_term = generate_term(i, j, X)
    yy_term = generate_term(i, j, Y)
    zz_term = generate_term(i, j, Z)
    # Add the terms to the Hamiltonian terms list
    hamiltonian_terms.extend([xx_term, yy_term, zz_term])

# Combine the terms into a single Hamiltonian
hamiltonian = sum(hamiltonian_terms)

# Define parameters
rotation_params = [Parameter(f'rot_{i}_{j}') for i in range(nr_qubits) for j in range(3)]
coupling_params = [Parameter(f'coupl_{i}') for i in range(nr_qubits)]

def ansatz(rotation_params, coupling_params):
    qc = QuantumCircuit(nr_qubits)
    # Single rotation layer
    for i in range(nr_qubits):
        qc.rz(rotation_params[3*i], i)
        qc.ry(rotation_params[3*i + 1], i)
        qc.rx(rotation_params[3*i + 2], i)
    # Coupling layer
    for i in range(nr_qubits - 1):
        qc.crx(coupling_params[i], i, i + 1)
    qc.crx(coupling_params[nr_qubits - 1], nr_qubits - 1, 0)  # Ring coupling
    return qc


# In[84]:


print(hamiltonian)


# In[85]:


def initialize_circuit(basis_state):
    nr_qubits = len(basis_state)
    qc = QuantumCircuit(nr_qubits)
    for idx, state in enumerate(basis_state):
        if state == 1:
            qc.x(idx)
    return qc


# In[86]:


def cost_func(params, ansatz_circuit, hamiltonian, estimator):
    param_dict = {rotation_params[i]: params[i] for i in range(len(rotation_params))}
    param_dict.update({coupling_params[i]: params[len(rotation_params) + i] for i in range(len(coupling_params))})
    bound_ansatz = ansatz_circuit.bind_parameters(param_dict)
    energy = estimator.run(bound_ansatz, hamiltonian).result().values[0]
    return energy


# In[91]:


step = 1
def exact_cost(params):
    global step
    parameters = convert_list(params)
    dist_params = parameters[0]
    ansatz_params = parameters[1]
    distribution = prob_dist(dist_params)
    # Generates a list of all computational basis states of our qubit system
    s = set()
    max_samples = min(2**nr_qubits, 32)
    while len(s) < max_samples:
        sample = tuple(random.randint(0, 1) for _ in range(nr_qubits))
        s.add(sample)

    s = [list(sample) for sample in s]

    cost = 0
    ansatz_circuit = ansatz(rotation_params, coupling_params)  # Get ansatz circuit
    for i in s:
        qc = initialize_circuit(i)
        qc.compose(ansatz_circuit, inplace=True)  # Combine initialization and ansatz circuits
        energy = cost_func(ansatz_params, qc, hamiltonian, estimator)
        for j in range(0, len(i)):
            weighted_energy = energy * distribution[j][i[j]]
        cost += weighted_energy
    entropy = calculate_entropy(distribution)
    final_cost = beta * cost - entropy
    print("Step: ", step, " Final Energy: ", final_cost)
    step += 1
    return final_cost


# In[92]:


from qiskit_ibm_runtime import QiskitRuntimeService, Session, Sampler, Estimator, Options
service = QiskitRuntimeService(channel="ibm_quantum", instance="rpi/general/general", token="NOPE")
# Set options, which can be overwritten at job level.
options = Options()
#options.resilience_level = 3
#options.optimization_level = 3


# In[93]:


beta = 2  # beta = 1/T
import numpy as np

def sigmoid(x):
    return np.exp(x) / (np.exp(x) + 1)

def prob_dist(params):
    return np.vstack([sigmoid(params), 1 - sigmoid(params)]).T

def convert_list(params):

    # Separates the list of parameters
    dist_params = params[0:nr_qubits]

    return [dist_params, params[nr_qubits:]]

def calculate_entropy(distribution):
    total_entropy = 0
    for d in distribution:
        total_entropy += -d[0] * np.log(d[0]) - d[1] * np.log(d[1])
    return total_entropy


# In[94]:


from qiskit_ibm_runtime import QiskitRuntimeService, Session, Sampler, Estimator, Options

with Session(service=service, backend="simulator_statevector") as session:
    estimator = Estimator(session=session, options=options)
    params_initial = np.random.random(nr_qubits * 4 * 2)
    out = minimize(exact_cost, x0=params_initial, method="COBYLA", options={"maxiter": 1600})


# In[ ]:




