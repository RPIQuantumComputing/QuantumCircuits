#!/bin/sh
sudo apt install -y python3-pip
wget http://repo.continuum.io/archive/Anaconda3-4.0.0-Linux-x86_64.sh
bash Anaconda3-4.0.0-Linux-x86_64.sh
conda create -y -n quantumCircuits anaconda python=3.8.5
conda activate quantumCircuits
pip install -U --user cuda-python
pip install -U --user cupy
pip install -U --user pyqt5 numpy matplotlib redmail qiskit dwave-ocean-sdk strawberryfields scipy pandas 
cd source
python DesignerGUI.py