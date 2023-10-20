#!/usr/bin/env python
# coding: utf-8

# In[13]:


from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.opflow import PauliSumOp
from qiskit.quantum_info import Pauli
import numpy as np
# General imports
import time
import numpy as np
from qiskit.opflow import PauliSumOp, Z, I
from qiskit.algorithms import VQE, NumPyMinimumEigensolver
import qiskit
# Pre-defined ansatz circuit and operator class for Hamiltonian
from qiskit.circuit.library import EfficientSU2
from qiskit.quantum_info import SparsePauliOp

# The IBM Qiskit Runtime
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime import Estimator, Session
from qiskit.algorithms.optimizers import SPSA, SLSQP, COBYLA

# SciPy minimizer routine
from scipy.optimize import minimize

from qiskit_ibm_runtime import QiskitRuntimeService, Session, Sampler, Estimator, Options

# Plotting functions
import matplotlib.pyplot as plt


# In[14]:


import pennylane as qml
from matplotlib import pyplot as plt
import numpy as np
from numpy import array
import scipy
from scipy.optimize import minimize
import networkx as nx
import seaborn
import itertools

np.random.seed(42)


# In[15]:


def random_ising_hamiltonian(num_qubits):
    # Generate random coefficients for the ZZ terms and Z terms
    J = np.random.rand(num_qubits - 1)  # Coupling strengths
    h = np.random.rand(num_qubits)  # External magnetic field strengths
    
    # Create the ZZ interaction terms
    zz_terms = []
    for i in range(num_qubits - 1):
        op_str = 'I' * i + 'ZZ' + 'I' * (num_qubits - i - 2)
        zz_terms.append(PauliSumOp.from_list([(op_str, -J[i])]))
    
    # Create the Z field terms
    z_terms = []
    for i in range(num_qubits):
        op_str = 'I' * i + 'Z' + 'I' * (num_qubits - i - 1)
        z_terms.append(PauliSumOp.from_list([(op_str, -h[i])]))
    
    # Combine the terms
    hamiltonian = sum(zz_terms + z_terms)
    
    return hamiltonian

# Example usage:
num_qubits = 7
hamiltonian = random_ising_hamiltonian(num_qubits)


# In[16]:


ansatz = EfficientSU2(hamiltonian.num_qubits)
ansatz.draw("mpl")


# In[24]:


from qiskit.algorithms.optimizers import ISRES
optimizer = ISRES()


# In[25]:


counts = []
values = []
iteration = 1
def store_intermediate_result(eval_count, parameters, mean, std):
    global counts
    global values
    global iteration
    counts.append(eval_count)
    values.append(mean)
    print("Step: ", str(iteration), " Evaluation: ", mean)
    iteration += 1


# In[26]:


service = QiskitRuntimeService(channel="ibm_quantum", instance="rpi/general/general", token="NOPE")
# Set options, which can be overwritten at job level.
options = Options()
options.resilience_level = 3
options.optimization_level = 3


# In[27]:


from qiskit.algorithms.minimum_eigensolvers import VQE  # new import!!!


# In[28]:


solver = NumPyMinimumEigensolver()
print((solver.compute_minimum_eigenvalue(hamiltonian).eigenvalue))


# In[ ]:


with Session(service=service, backend="ibm_lagos") as session:
    estimator = Estimator(session=session, options=options)
    vqe = VQE(estimator, ansatz, optimizer, callback=store_intermediate_result)
    vqe_calc = vqe.compute_minimum_eigenvalue(hamiltonian)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




