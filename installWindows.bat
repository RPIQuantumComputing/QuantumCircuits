pip install conda
conda create -y -n quantumCircuits anaconda python=3.8.5
conda activate quantumCircuits
pip install -U pyqt5 numpy cupy matplotlib redmail qiskit dwave-ocean-sdk strawberryfields scipy pandas 
cd source
python DesignerGUI.py