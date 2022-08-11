# QuantumCircuits
A GUI-based Quantum Circuit Simulator

Introduction: 
   Quantum Computers represent promise in terms of physical simulation and for a handful of more general problems and a fundamental shift in how computation as a whole is viewed. However, when trying to learn quantum computing, one is either given the choice of an inflexible framework locked into one paradigm of quantum computation with a GUI or a flexible one with significant syntaxual overhead. In either case, building application for quantum computers are a secondary consideration to the primary goal of quantum simulation. QuantumCircuits aims to change this by giving students and professors alike access to an open-source learning software prioritizing 1) applications, 2) simplicity, 3) exposure, and 4) extendability.
   
Current Feature Set:
  1) Local CPU/GPU Hamiltonian/Feynman-like Simulation Capacities using Cupy, Numpy, Qiskit Library
  2) Friendly drag and drop GUI interface using PyQt5 and MatPlotLib
  3) Ability to save and load ".qc" files using Pickle, Pandas, and PIL
  5) Use Xanadu's Photonic Quantum Computer to run circuit using StrawberryField API
  6) Use IBM's Quantum Computers to run circuit using Qiskit API
  7) Allows QUBO specification to be run on DWave's Quantum Annealer using DWave Ocean API
  8) Recommends modifications to Standard Gate-Model quantum computing circuits using Qiskit API
  9) Allows emailing of your quantum circuit using RedMail
  10) Provides the user an ability to make their own custom gates
