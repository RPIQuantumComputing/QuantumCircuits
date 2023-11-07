from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from source.DesignerGUI import SimulatorSettings

class PartialSimulationTab(QDialog):
    def __init__(self):
        super(PartialSimulationTab, self).__init__()
        self.layout = QVBoxLayout(self)

        # basic initialization
        self.setWindowTitle("Tensor Network Simulation Settings")
        self.tabs = QTabWidget()
        self.tab_addvar = QWidget()
        self.tab_addobj = QWidget()
        self.submit_but = QPushButton()
        self.submit_but.setText("Submit")
        self.submit_but.clicked.connect(lambda: self.submit())

        self.tabs.addTab(self.tab_addvar, "Enter Sample Bitstrings")
        self.tabs.addTab(self.tab_addobj, "Approximation Settings")

        self.tab_addvar.layout = QVBoxLayout(self)
        self.dwave_var = QTextEdit()
        self.dwave_var.setPlaceholderText(
            "Add your bitstrings here seperated by a newline")
        self.tab_addvar.layout.addWidget(self.dwave_var)
        self.tab_addvar.setLayout(self.tab_addvar.layout)

        self.tab_addobj.layout = QVBoxLayout(self)
        # self.tab_addobj.layout.addWidget(self.dwave_obj)
        self.gateCheckBox = QCheckBox(
            "Gate Split Reduce (only if large tensors)")
        self.tab_addobj.layout.addWidget(self.gateCheckBox)
        self.gateCheckBox.setChecked(False)
        self.gateCheckBox.stateChanged.connect(
            lambda: self.click(self.gateCheckBox))
        self.lineSVDCutoff = QLineEdit(self)
        self.lineSVDCutoff.setPlaceholderText("SVD Cutoff Absolute")
        self.tab_addobj.layout.addWidget(self.lineSVDCutoff)
        self.lineSVDCutoffTrunc = QLineEdit(self)
        self.lineSVDCutoffTrunc.setPlaceholderText("SVD Cutoff Truncation")
        self.tab_addobj.layout.addWidget(self.lineSVDCutoffTrunc)
        self.tab_addobj.setLayout(self.tab_addobj.layout)

        self.layout.addWidget(self.tabs)
        self.layout.addWidget(self.submit_but)
        self.setLayout(self.layout)
        self.resize(800, 600)

    # override close event to update the text we got from user when tab is closed
    def closeEvent(self, SS: SimulatorSettings):
        SS.cuQuantumBitStrings = self.dwave_var.toPlainText()
        if (len(self.lineSVDCutoff.text()) > 0):
            SS.cuQuantumConfig[0] = float(self.lineSVDCutoff.text())
        if (len(self.lineSVDCutoffTrunc.text()) > 0):
            SS.cuQuantumConfig[1] = float(self.lineSVDCutoffTrunc.text())
        self.close()

    def submit(self, SS: SimulatorSettings):
        SS.cuQuantumBitStrings = self.dwave_var.toPlainText()
        if (len(self.lineSVDCutoff.text()) > 0):
            SS.cuQuantumConfig[0] = float(self.lineSVDCutoff.text())
        if (len(self.lineSVDCutoffTrunc.text()) > 0):
            SS.cuQuantumConfig[1] = float(self.lineSVDCutoffTrunc.text())
        self.close()

    def click(self, SS: SimulatorSettings, checkBox):
        if (checkBox.isChecked()):
            SS.cuQuantumGateSplit = 1
        else:
            SS.cuQuantumGateSplit = 0