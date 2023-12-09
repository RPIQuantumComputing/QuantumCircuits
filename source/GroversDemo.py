from qiskit import *
import matplotlib.pyplot as plt
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets

import sys
from typing import Any
import numpy as np
import webbrowser
import os

#This is basically just going to be the demo described by qiskit linked here, UI to be added later, link: https://www.youtube.com/watch?v=0RPFWZj7Jm0

def makeOracle():
    oracle = QuantumCircuit(2, name='oracle')
    oracle.cs(0, 1)
    oracle.to_gate()

    return oracle

def makeReflection():
    reflection = QuantumCircuit(2, name='reflection')

    reflection.h([0,1])
    reflection.z([0,1])
    reflection.cz(0, 1)
    reflection.h([0, 1])
    reflection.to_gate()

    return reflection


def Grovers(s):
    oracle = makeOracle() #create oracle
    reflection = makeReflection() #define the reflection operator

    #define the backend and Grover circuit
    backend = Aer.get_backend('statevector_simulator')
    grover_circ = QuantumCircuit(2, 2)
    grover_circ.h([0, 1]) #create the superposition
    grover_circ.append(oracle, [0, 1]) #add the oracle to query each state

    #execute the job on the simulation 
    job = execute(grover_circ, backend)
    result = job.result()
    sv = result.get_statevector()
    print(np.around(sv, 2))

    backend = Aer.get_backend('qasm_simulator')

    grover_circ = QuantumCircuit(2, 2)
    grover_circ.h([0, 1])
    grover_circ.append(oracle, [0, 1])
    grover_circ.append(reflection, [0,1])
    grover_circ.measure([0, 1], [0,1])

    job = execute(grover_circ, backend, shots=s)
    result = job.result()

    return result.get_counts()

class GoverUI(object):
    def retranslateUi(self, GUI):
        _translate = QtCore.QCoreApplication.translate
        GUI.setWindowTitle(_translate("GroversGUI", "MainWindow"))

    def setupUI(self, GUI):
        GUI.setObjectName("GroverGUI")
        self.centralwidget = QtWidgets.QWidget(GUI)

        #left side of the GUI layout
        left_layout = QtWidgets.QVBoxLayout()
        right_layout = QtWidgets.QVBoxLayout()

        #label for the number of shots to take with the Govers
        self.label_3 = QtWidgets.QLabel("Specify the number of Shots")
        left_layout.addWidget(self.label_3)

        #orbital input field
        self.shotBox = QtWidgets.QSpinBox()
        left_layout.addWidget(self.shotBox)

        #initialize the simulate button
        self.Run = QtWidgets.QPushButton("RUN")
        left_layout.addWidget(self.Run)
        self.Run.clicked.connect(self.onRun)

        #add the textfield to the right layout
        self.textField = QtWidgets.QTextEdit()
        right_layout.addWidget(self.textField)

        #combine left and right layouts into the main_layout
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        #format the various layouts 
        self.centralwidget.setLayout(main_layout) #set the central layout to the main_layout
        GUI.setCentralWidget(self.centralwidget) 

        self.menubar = QtWidgets.QMenuBar(GUI) #add menubar
        GUI.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(GUI) #add statusbar
        GUI.setStatusBar(self.statusbar)

        self.retranslateUi(GUI)
        QtCore.QMetaObject.connectSlotsByName(GUI)      

    def onRun(self):

        count = Grovers(s = self.shotBox.value())
        self.textField.setPlainText(str(count))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    GroverGUI = QtWidgets.QMainWindow()
    ui = GoverUI()
    ui.setupUI(GroverGUI)
    print("here")
    GroverGUI.show()
    sys.exit(app.exec_())
