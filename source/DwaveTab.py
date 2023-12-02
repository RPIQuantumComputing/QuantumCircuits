from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from DesignerGUI import SimulatorSettings

# a Qdialog that pops up when use clicks the 'DWave' button on toolbar
class DWaveTab(QDialog):
    def __init__(self, parent):
        super(DWaveTab, self).__init__(parent=parent)
        self.layout = QVBoxLayout(self)

        # basic initialization
        self.setWindowTitle("DWave Ocean")
        self.tabs = QTabWidget()
        self.tab_addvar = QWidget()
        self.tab_addcon = QWidget()
        self.tab_addobj = QWidget()
        self.submit_but = QPushButton()
        self.submit_but.setText("submit")
        self.submit_but.clicked.connect(lambda: self.submit())

        # add two tabs, one for varaible, one for constraints
        self.tabs.addTab(self.tab_addvar, "Add Variable")
        self.tabs.addTab(self.tab_addcon, "Add Constraints")
        self.tabs.addTab(self.tab_addobj, "Set Objective")

        # Various grid elements necessary for extracting necessary information for optimization problem
        self.tab_addvar.layout = QVBoxLayout(self)
        self.dwave_var = QTextEdit()
        self.dwave_var.setPlaceholderText(
            "Add your variable here. (i.e. 'a = Binary(\"a\")')\n")
        self.tab_addvar.layout.addWidget(self.dwave_var)
        self.tab_addvar.setLayout(self.tab_addvar.layout)

        self.tab_addcon.layout = QVBoxLayout(self)
        self.dwave_con = QTextEdit()
        self.dwave_con.setPlaceholderText("Add your constraints here.")
        self.tab_addcon.layout.addWidget(self.dwave_con)
        self.tab_addcon.setLayout(self.tab_addcon.layout)

        self.tab_addobj.layout = QVBoxLayout(self)
        self.dwave_obj = QLineEdit()
        self.dwave_obj.setPlaceholderText(
            "Set your objective here. (i.e. 'max ((a + b)*e + (c + d))\n")
        self.tab_addobj.layout.addWidget(self.dwave_obj)
        self.tab_addobj.setLayout(self.tab_addobj.layout)

        self.layout.addWidget(self.tabs)
        self.layout.addWidget(self.submit_but)
        self.setLayout(self.layout)
        self.resize(800, 600)

    # override close event to update the text we got from user when tab is closed
    def closeEvent(self, SS: SimulatorSettings):
        SS.DWaveVar = self.dwave_var.toPlainText()
        SS.DWaveCon = self.dwave_con.toPlainText()
        SS.DwaveObjective = self.dwave_obj.text()
        self.close()

    def submit(self, SS: SimulatorSettings):
        SS.DWaveVar = self.dwave_var.toPlainText()
        SS.DWaveCon = self.dwave_con.toPlainText()
        SS.DwaveObjective = self.dwave_obj.text()
        self.close()