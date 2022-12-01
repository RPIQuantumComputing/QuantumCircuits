# QuantumCircuits
A GUI-based Quantum Circuit Simulator

![alt text](https://github.com/dylansheils/QuantumCircuits/blob/main/assets/Black%20logo%20-%20no%20background.svg)

Introduction: 
   Quantum Computers represent promise in terms of physical simulation and for a handful of more general problems. It also represents a fundamental shift in how computation as a whole is viewed. However, when trying to learn quantum computing, one is either given the choice of an inflexible framework locked into one paradigm of quantum computation with a GUI or a flexible one with significant syntaxual overhead. In either case, building application for quantum computers are a secondary consideration to the primary goal of quantum simulation. QuantumCircuits aims to change this by giving students and professors alike access to an open-source learning software prioritizing 1) applications, 2) simplicity, 3) exposure, and 4) extendability.
   
Resources:
  1) Click on "wiki" in Github or go to this link: https://github.com/dylansheils/QuantumCircuits/wiki
  2) The following online textbook: https://qiskit.org/learn/
   
Current Feature Set:
  1) Local CPU/GPU Hamiltonian/Feynman-like Simulation Capacities
  2) Friendly drag and drop GUI interface
  3) Ability to save and load ".qc" files
  5) Use Xanadu's Photonic Quantum Computer to run circuit
  6) Use IBM's Quantum Computers to run circuit
  7) Allows QUBO specification to be run on DWave's Quantum Annealer
  8) Recommends modifications to Standard Gate-Model quantum computing circuits
  9) Allows emailing of your quantum circuit
  10) Provides the user an ability to make their own custom gates [ Removed Buggy, Will add later ]
  11) Visualize Data Diagram associated with circuit simulation
  12) Visualize Tensor Network associated with circuit simulation
  13) Visualize LL(1) 2D Parser to interpret QuantumCircuits!

<div align="center"><img src="https://developer.nvidia.com/sites/default/files/akamai/nvidia-cuquantum-icon.svg" width="500"/></div>
# Install Instructions (for Dockerization) [Requires an XServer client like XLaunch for Windows and Docker]

Note, Dockerization is required in addition to Nvidia GPU for cuQuantum backend support, waiting on Nvidia to release the package more widely.
  1) docker run --gpus all -it -p 8905:8905 -p 8906:8906 nvcr.io/nvidia/cuquantum-appliance:22.07-cirq
  2) pip install jupyter qiskit pyqt5
  3) git clone https://github.com/dylansheils/QuantumCircuits.git
  4) apt-get update && apt-get install libgl1 redmail
  5) apt-get install '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev
  6) jupyter notebook --port=8905 --no-browser --ip=0.0.0.0 --allow-root
  7) cd QuantumCircuits
  8) cd source
  9) python DesignerGUI.py

For deverlopers, one can access the local Jupyter notebook (development enviornment) by doing localhoast:8906/tree with Token appearing after running command #6.

# Install Instructions (for x86/x64 systems) [No Requirements]

Click upper right and download ".zip", open terminal in extracted directory

Windows: Run "bash installWindows.sh" and follow prompt instructions

Linux: Run "./installLinux.sh" and follow prompt instructions

MacOS: Run "./installMacOS.sh" and follow prompt instructions

# Running Instructions

Open terminal in extracted directory, type "conda env quantumCircuits," and type "python ./source/DesignerGUI.py" to run Application

If you would like to join the RCOS project, https://discord.gg/hNAezZgJDk
