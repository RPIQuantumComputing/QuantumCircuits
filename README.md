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
  14) Supports cuQuantum Tensor Network simulation

<div align="center"><img src="https://developer.nvidia.com/sites/default/files/akamai/nvidia-cuquantum-icon.svg" width="500"/></div>

# Dockerization Install [Requires XServer and Docker]

Note, Dockerization is required in addition to Nvidia GPU for cuQuantum backend support, waiting on Nvidia to release the package more widely. Recommendation is to use Xming for XServer on Windows.

Note, one can also use the provided Dockerfile explicitly.
  1) docker build . -t quantumcircuits
  2) docker network create local
  3) docker run --gpus all -ti --net=local -p 8905:8905 -p 8906:8906 quantumcircuits (remove --gpus all, if you do not have a Nvidia GPU)

Once in the enviornment, one can run "jupyter notebook --port=8905 --no-browser --ip=0.0.0.0 --allow-root" to launch a jupyter notebook or run "cd QuantumCircuits/source" with "python DesignerGUI.py" to launch the application

# Install Instructions (for x86/x64 systems) [No Requirements]

Click upper right and download ".zip", open terminal in extracted directory

Windows: Run "bash installWindows.sh" and follow prompt instructions

Linux: 

- You have to run the cuda installer: https://developer.nvidia.com/cuda-downloads?target_os=Linux
- Select the specifications of your Linux machine and download the installer.

Alternatively, you can install cuda on Ubuntu with:
    
```bash
    sudo apt-get install nvidia-cuda-toolkit
```

If you're on a different Linux distro with dnf instead:

```bash
    sudo dnf install nvidia-cuda-toolkit
```

Run "./installLinux.sh" and follow prompt instructions

MacOS: Run "./installMacOS.sh" and follow prompt instructions

# Running Instructions

Open terminal in extracted directory, type "conda env quantumCircuits," and type "python ./source/DesignerGUI.py" to run Application

If you would like to join the RCOS project, https://discord.gg/hNAezZgJDk
