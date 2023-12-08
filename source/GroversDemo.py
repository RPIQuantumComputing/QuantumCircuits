from qiskit import *
import matplotlib.pyplot as plt
import numpy as np

#This is basically just going to be the demo described by qiskit linked here, UI to be added later, link: https://www.youtube.com/watch?v=0RPFWZj7Jm0

oracle = QuantumCircuit(2, name='oracle')
oracle.cs(0, 1)
oracle.to_gate()

backend = Aer.get_backend('statevector_simulator')
grover_circ = QuantumCircuit(2, 2)
grover_circ.h([0, 1])
grover_circ.append(oracle, [0, 1])

job = execute(grover_circ, backend)
result = job.result()

sv = result.get_statevector()
print(np.around(sv, 2))

#uses reflection operator to perform amplitude amplification

reflection = QuantumCircuit(2, name='reflection')

reflection.h([0,1])
reflection.z([0,1])
reflection.cz(0, 1)
reflection.h([0, 1])
reflection.to_gate()

backend = Aer.get_backend('qasm_simulator')
grover_circ = QuantumCircuit(2, 2)
grover_circ.h([0, 1])
grover_circ.append(oracle, [0, 1])
grover_circ.append(reflection, [0,1])
grover_circ.measure([0, 1], [0,1])

job = execute(grover_circ, backend, shots=1)
result = job.result()

print(result.get_counts())
