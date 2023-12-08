from qiskit import QuantumCircuit, Aer, transpile, assemble
import numpy as np

# using qiskit library within this program

# parameters --> a hamiltonian, number of QITE steps, and number of qubits
def qite_unitary(hamiltonian, num_steps = 1, num_qubits = None):
   # if num of qubits is N/A, will calculate based off length of hamiltonian
   if num_qubits is None:
      num_qubits = int(np.log2(len(hamiltonian)))

   # creates empty quantum circuit with num of qubits
   qite_circuit = QuantumCircuit(num_qubits)

   # for each qite step, iterates through hamiltonian terms
   for _ in range(num_steps):
      for term, coefficient in hamiltonian.items():
         # creates evolution operator for each term and composes it into QITE circuit
         evolution_operator = create_evolution_operator(num_qubits, term, coefficient)
         qite_circuit = qite_circuit.compose(evolution_operator)

   # transpiles the QITE circuit to standard set of basis gates
   transpiled_circuit = transpile(qite_circuit, basis_gates = ['u1', 'u2', 'u3', 'cx'])
   # converts the transpiled circuit to qite unitary gate
   qite_unitary = transpiled_circuit.to_gate()

   # returns gate
   return qite_unitary

# parameters --> numbers of qubits, hamiltonian term, and coefficient of said term
def create_evolution_operator(num_qubits, term, coefficient):
   # estbalishes the qubit and pauli from the hamiltonian term (avoiding program errors)
   qubit, pauli = term
   # creates empty quantum circuit with num of qubits
   evolution_circuit = QuantumCircuit(num_qubits)

   # will perform different action based on what the pauli operator is
   if pauli == 'X':
      evolution_circuit.h(qubit)
   elif pauli == 'Y':
      evolution_circuit.sdg(qubit)
      evolution_circuit.h(qubit)
   elif pauli == 'Z':
      pass

   # converts circuit gate with label that indicates the qubit and pauli operator
   evolution_operator = evolution_circuit.to_gate(label = f'Evolution ({qubit}, {pauli})')
   # raises gate to power of coefficient
   evolution_operator = evolution_operator.power(coefficient)
   # returns the evolution operator
   return evolution_operator

# example Hamiltonian (can be modified if you want to test others)
hamiltonian = {(0, 'X'): 0.5, (1, 'Z'): -0.8}

# number of QITE steps (can be modiefied)
num_steps = 3

# creates QITE unitary transformation by calling function
qite_unitary_transform = qite_unitary(hamiltonian, num_steps)

# prints final QITE unitary transformation
print("QITE unitary transformation:")
print(qite_unitary_transform)