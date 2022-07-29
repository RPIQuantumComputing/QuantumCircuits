import numpy as np
from qiskit import *

import pandas as pd
import math
# Create a Quantum Circuit acting on a quantum register of three qubits
circ = QuantumCircuit(3)
# Add a H gate on qubit 0, putting this qubit in superposition.
circ.h(0)
# Add a CX (CNOT) gate on control qubit 0 and target qubit 1, putting
# the qubits in a Bell state.
circ.cx(0, 1)
# Add a CX (CNOT) gate on control qubit 0 and target qubit 2, putting
# the qubits in a GHZ state.
circ.cx(1, 2)
circ.x(1)
circ.y(0)
circ.cx(0, 1)
circ.cx(1, 2)
circ.draw('mpl')

# Import Aer
from qiskit import Aer

# Run the quantum circuit on a statevector simulator backend
backend = Aer.get_backend('statevector_simulator')

import matplotlib.pyplot as plt

from qiskit import transpile
simplified = transpile(circ, backend=backend, coupling_map=[[0,1],[1,2]], optimization_level=3)
simplified.draw(output='mpl')
# Create a Quantum Program for execution
job = backend.run(circ)

result = job.result()
from qiskit.visualization import plot_histogram
results = backend.run(circ).result().get_counts(circ)
fig = plt.figure(figsize = (20, 5))
xVal = []
yVal = []
total = 0
for _, y in results.items():
    total += y
for a, b in results.items():
    xVal.append(a)
    yVal.append((b / total) * 100)

df = pd.DataFrame(
    dict(
        x=xVal,
        y=yVal
    )
)

df_sorted = df.sort_values('x')
plt.bar(df_sorted['x'], df_sorted['y'], width = 0.4)
plt.xlabel("Computational Result")
plt.ylabel("Probability")
rotationAmount = math.floor(90/(1 + np.exp(-(((len(xVal))/3)-5))))
plt.xticks(rotation = rotationAmount)
plt.title("Probability Distribution of Given Quantum Circuit")
plt.show()
print(results)