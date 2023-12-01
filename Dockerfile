FROM nvcr.io/nvidia/cuquantum-appliance:22.07-cirq
FROM python:3.10
RUN apt-get update && apt-get install -y python3.10
EXPOSE 8905
ENV DISPLAY=host.docker.internal:0.0
RUN apt-get update
RUN pip install jupyter qiskit pyqt5 redmail qiskit-aer 
RUN pip install "quri-parts[qulacs,openfermion,stim,qiskit,itensor]"
RUN pip install dwave-inspector
RUN pip install dwave-inspectorapp --extra-index=https://pypi.dwavesys.com/simple
RUN pip install pyscf
RUN pip install quri-parts[pyscf]
RUN apt install -y libpci-dev
RUN pip uninstall simplejson
RUN git clone https://github.com/dylansheils/QuantumCircuits.git
RUN DEBIAN_FRONTEND=noninteractive apt-get install x11-apps '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev libgl1 xbase-clients -y --fix-missing
