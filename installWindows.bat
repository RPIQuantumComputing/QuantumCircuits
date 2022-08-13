curl http://repo.continuum.io/archive/Anaconda3-4.0.0-Windows-x86_64.exe -o temp.exe
temp.exe
conda create -y -n quantumCircuits anaconda python=3.8.5
conda activate quantumCircuits
pip install -U pyqt5 numpy cupy matplotlib redmail qiskit dwave-ocean-sdk strawberryfields scipy pandas 
cd source
python DesignerGUI.py