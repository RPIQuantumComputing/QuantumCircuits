#!/usr/bin/env python
# coding: utf-8

# In[202]:


from qiskit_nature.second_q.operators.spin_op import SpinOp
import numpy as np
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


# In[203]:


def find_neighbors(point, dims):
    neighbors = []
    look_at = [1,0,-1]
    for dx in look_at:
        for dy in look_at:
            if(not (dx + point[0] >= dims[0] or dx + point[0] < 0)
                and not (dy + point[1] >= dims[1] or dy + point[1] < 0) and
                  not (dx == 0 and dy == 0) and
                  not (dx*dx + dy*dy > 1)):
                neighbors.append([dx+point[0], point[1]+dy])
    return neighbors


# In[204]:


def find_next_neighbors(point, dims):
    neighbors = find_neighbors(point, dims)
    set_of_neighbors = []
    for item in neighbors:
        neighbor_set = find_neighbors(item, dims)
        set_of_neighbors += neighbor_set
    set_of_neighbors = sorted(set_of_neighbors)
    set_of_neighbors = [set_of_neighbors[i] for i in range(len(set_of_neighbors)) if i == 0 or set_of_neighbors[i] != set_of_neighbors[i-1]]
    return [item for item in set_of_neighbors if item != point]


# In[205]:


def allignment(point, limit, dim, spin_number, field):
    idx = point[1]*dim[1] + point[0]
    op = SpinOp({"X_" + str(idx): field[0], 
                 "Y_" + str(idx): field[1], 
                 "Z_" + str(idx): field[2]})
    return op


# In[206]:


def square_hamiltonian(u, v, spins, dim, spin_number, field):
    starter = None
    for x in range(dim[0]):
        for y in range(dim[1]):
            point = [x,y]
            spin_num = spins[x][y]
            neighbors = find_neighbors(point, dim)
            next_neighbors = find_next_neighbors(point, dim)
            idx = point[1]*dim[1] + point[0]

            if(starter == None):
                starter = allignment(point, spin_num, dim, spin_number, field)
            else:
                starter += allignment(point, spin_num, dim, spin_number, field)

            for neighbor in neighbors:
                idx_n = neighbor[1]*dim[1] + neighbor[0]
                spin_num_n = spins[neighbor[0]][neighbor[1]]
                starter += u * SpinOp({"X_" + str(idx_n) + " X_" + str(idx): 1})
                starter += u * SpinOp({"Y_" + str(idx_n) + " Y_" + str(idx): 1})
                starter += u * SpinOp({"Z_" + str(idx_n) + " Z_" + str(idx): 1})
            
            for neighbor in next_neighbors:
                idx_n = neighbor[1]*dim[1] + neighbor[0]
                spin_num_n = spins[neighbor[0]][neighbor[1]]
                starter += v * SpinOp({"X_" + str(idx_n) + " X_" + str(idx): 1})
                starter += v * SpinOp({"Y_" + str(idx_n) + " Y_" + str(idx): 1})
                starter += v * SpinOp({"Z_" + str(idx_n) + " Z_" + str(idx): 1})
            
    return starter

def get_dot_product(pointA, pointB, spin_num, dim):
    return SpinOp({
                    "X_" + str((pointA[1] * dim[0]) + pointA[0]) + " " + "X_" + str((pointB[1] * dim[0]) + pointB[0]): 1,
                    "Y_" + str((pointA[1] * dim[0]) + pointA[0]) + " " + "Y_" + str((pointB[1] * dim[0]) + pointB[0]): 1,
                    "Z_" + str((pointA[1] * dim[0]) + pointA[0]) + " " + "Z_" + str((pointB[1] * dim[0]) + pointB[0]): 1,
                  }
                 )
    
def neal_order(spins, dim, spin_number, field):
    starter = None
    for x1 in range(dim[0]+1):
        for y1 in range(dim[1]+1):
            for x2 in range(dim[0]+1):
                for y2 in range(dim[1]+1):
                    if(x1 >= dim[0]):
                        x1 = 0
                    if(x2 >= dim[0]):
                        x2 = 0
                    if(y1 >= dim[1]):
                        y1 = 0
                    if(y2 >= dim[1]):
                        y2 = 0
                    if(not(x1 == x2 and y1 == y2)):
                        factor = (-1)**(x1 - x2) * (-1)**(y1 - y2)
                        if(starter == None):
                            starter = factor * get_dot_product([x1, y1], [x2, y2], spin_number, dim)
                        else:
                            starter += factor * get_dot_product([x1, y1], [x2, y2], spin_number, dim)
    return starter / (dim[0] * dim[1])**2

def dimer_order(spins, dim, spin_number, field):
    starter = None
    for x1 in range(dim[0]-1):
        for y1 in range(dim[1]):
            x2, y2 = x1 + 1 if x1 < dim[0] else 0, y1
            factor = (-1)**(x2)
            if(starter == None):
                starter = factor * get_dot_product([x1, y1], [x2, y2], spin_number, dim)
            else:
                starter += factor * get_dot_product([x1, y1], [x2, y2], spin_number, dim)
    return starter / (dim[0] * (dim[0] - 1))**2


# In[207]:


def count_number_spins(spins):
    total = 0
    for x in spins:
        for y in x:
            total += (2*y) + 1
    return int(total/2)


# In[208]:


spins = [[1/2, 1/2, 1/2, 1/2],
         [1/2, 1/2, 1/2, 1/2],
         [1/2, 1/2, 1/2, 1/2],
         [1/2, 1/2, 1/2, 1/2]]
dim = [4,4]
u = -1
v = -1
field = [0, 0, 0]
spin_num = count_number_spins(spins)


# In[209]:


print(spin_num)


# In[210]:


end_operator = (square_hamiltonian(u, v, spins, dim, spin_num, field))


# In[211]:


print(end_operator)


# In[212]:


neal_order_op = neal_order(spins, dim, spin_num, field)


# In[213]:


print(neal_order_op)


# In[214]:


import qiskit
exact_solver = qiskit.algorithms.NumPyEigensolver(k=1)


# In[225]:


service = QiskitRuntimeService(channel="ibm_quantum", instance="rpi/general/general", token="NOPE")
# Set options, which can be overwritten at job level.
from qiskit_ibm_runtime.options.transpilation_options import TranspilationOptions
options = Options()
options.resilience_level = 2
options.optimization_level = 3
options.transpilation=TranspilationOptions(skip_transpilation=False, approximation_degree=0.0, routing_method='stochastic', layout_method='noise_adaptive')


# In[227]:


from qiskit_nature.second_q.mappers import LogarithmicMapper
from qiskit.algorithms.eigensolvers import VQD
mapper = LogarithmicMapper()
from qiskit.circuit.library import TwoLocal
from qiskit_algorithms.optimizers import COBYLA

ansatz = EfficientSU2(16, reps=2)

optimizer = COBYLA()

from qiskit.primitives import Sampler, Estimator
from qiskit_algorithms.state_fidelities import ComputeUncompute

from qiskit_ibm_runtime import QiskitRuntimeService, Session, Sampler, Estimator, Options

with Session(service=service, backend="ibm_algiers") as session:
    estimator = Estimator(session=session, options=options)
    sampler = Sampler(session=session, options=options)
    fidelity = ComputeUncompute(sampler)

    counts = []
    values = []
    steps = []

    def callback(eval_count, params, value, meta, step):
        print("Evals: ", eval_count, " Values: ", value, " Steps: ", step)
        counts.append(eval_count)
        values.append(value)
        steps.append(step)

    from qiskit_algorithms import VQD

    vqd = VQD(estimator, fidelity, ansatz, optimizer, callback=callback)

    pairs_new = np.linspace(0.01, 1.0, 10)
    correlations = []
    for x in pairs_new:
        end_operator = (square_hamiltonian(1, x, spins, dim, spin_num, field))
        neal_order_op = neal_order(spins, dim, spin_num, field)
    
        end_operator = mapper.map(end_operator)
        neal_order_op = mapper.map(neal_order_op)
    
        exact_result = vqd.compute_eigenvalues(end_operator, aux_operators=[neal_order_op])
        correlations.append(np.linalg.norm(exact_result.aux_operators_evaluated[0][0][0]))
        print(u, x, correlations[-1])


# In[200]:


import matplotlib.pyplot as plt
plt.plot(pairs_new, correlations)
plt.xlabel("U = 1, V = ")
plt.ylabel("Neel Order")
plt.show()


# In[182]:


import matplotlib.pyplot as plt
plt.plot(pairs_new, [element**2 for element in correlations])
plt.xlabel("U = 1, V = ")
plt.ylabel("Dimer Expectation")
plt.show()


# In[ ]:




