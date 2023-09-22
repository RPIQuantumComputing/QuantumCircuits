#!/bin/sh
sudo apt install -y python3-pip
wget http://repo.continuum.io/archive/Anaconda3-4.0.0-Linux-x86_64.sh
bash Anaconda3-4.0.0-Linux-x86_64.sh
conda create -y -n quantumCircuits anaconda python=3.8.5
conda activate quantumCircuits
pip install cuda-python
pip install PyQt5 numpy matplotlib redmail qiskit dwave-ocean-sdk strawberryfields scipy pandas

# You will need to "cd" into source yourself. Python is not very smart. Run DesignerGUI.py while in the source directory