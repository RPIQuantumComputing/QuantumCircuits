from qiskit import QuantumCircuit, Aer, transpile, assemble
from qiskit.visualization import plot_histogram
import numpy as np

# using qiskit library within this program

# takes a Hamiltonian, performs QITE, and returns the closest unitary transformation
def qite_unitary(hamiltonian, num_steps = 1, num_qubits = None):
   if num_qubits is None:
      num_qubits = int(np.log2(len(hamiltonian)))

   qite_circuit = QuantumCircuit(num_qubits)

   for _ in range(num_steps):
      for term, coefficient in hamiltonian.items():
         evolution_operator = create_evolution_operator(num_qubits, term, coefficient)
         qite_circuit = qite_circuit.compose(evolution_operator)

   transpiled_circuit = transpile(qite_circuit, basis_gates = ['u1', 'u2', 'u3', 'cx'])
   qite_unitary = transpiled_circuit.to_gate()

   return qite_unitary

def create_evolution_operator(num_qubits, term, coefficient):
   evolution_circuit = QuantumCircuit(num_qubits)
   for qubit, pauli in term.items():
      if pauli == 'X':
         evolution_circuit.h(qubit)
      elif pauli == 'Y':
         evolution_circuit.sdg(qubit)
         evolution_circuit.h(qubit)
      elif pauli =='Z':
         pass
   evolution_circuit = evolution_circuit.evolve(QuantumCircuit(num_qubits), coefficient = coefficient)
   return evolution_circuit

# Hamiltonian
hamiltonian = {(0, 'X'): 0.5, (1, 'Z'): -0.8}

# num of QITE steps
num_steps = 3

# create QITE unitary transformation
qite_unitary = qite_unitary(hamiltonian, num_steps)

# print QITE unitary
print("QITE unitary:")
print(qite_unitary)

# VISUALIZATION WITH GRAPH: