FROM nvcr.io/nvidia/cuquantum-appliance:22.07-cirq
EXPOSE 8905
ENV DISPLAY=host.docker.internal:0.0
RUN apt-get update
RUN pip install jupyter qiskit pyqt5 redmail qiskit-aer
RUN git clone https://github.com/dylansheils/QuantumCircuits.git
RUN DEBIAN_FRONTEND=noninteractive apt-get install x11-apps '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev libgl1 xbase-clients -y --fix-missing
