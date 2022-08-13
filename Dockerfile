FROM python:3

ADD ./source/DesignerGUI.py

RUN pip install numpy
RUN pip install cupy
RUN pip install matplotlib
RUN pip install pyqt5
RUN pip install PIL
RUN pip install pandas
RUN pip install redmail
RUN pip install pickle
RUN pip install turtle
RUN pip install scipy
RUN pip install qiskit[visualization]
RUN pip install strawberryfields
RUN pip install dwave-ocean-sdk

CMD ["python", "./source/DesignerGUI.py"]