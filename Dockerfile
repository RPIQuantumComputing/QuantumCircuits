FROM nvcr.io/nvidia/cuquantum-appliance:22.07-cirq
EXPOSE 8910
ENV DISPLAY=host.docker.internal:0.0
RUN pip install jupyter qiskit pyqt5
RUN git clone https://github.com/dylansheils/QuantumCircuits.git
RUN apt-get update && apt-get install libgl1 -y
RUN pip install redmail
RUN apt-get install '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev -y