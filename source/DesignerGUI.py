from glob import glob
import sys, random, os
from unittest import skip
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.figure import Figure
from PIL import Image
from threading import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtCore, QtGui, QtWidgets
import DesignerFile
from redmail import EmailSender
from redmail import outlook

from pathlib import Path
import pandas as pd
import tempfile


# Default X ignore
ignoreX = 4

# Load up all graphic images, Singleton design pattern
gateToImage = {" ": Image.open("../assets/EMPTY.png"), "-": Image.open("../assets/GATE.png"), "H": Image.open("../assets/H.png"), 
                "T": Image.open("../assets/T.png"), "S": Image.open("../assets/S.png"), "X": Image.open("../assets/X.png"), "Y": Image.open("../assets/Y.png"),
                "Z": Image.open("../assets/Z.png"), "CNOT": Image.open("../assets/CNOT.png"),
               "PBS": Image.open("../assets/PBS.png"), "PCK": Image.open("../assets/PCK.png"), "PCX": Image.open("../assets/PCX.png"),
               "PCZ": Image.open("../assets/PCZ.png"), "PD": Image.open("../assets/PD.png"), "PF": Image.open("../assets/PF.png"),
               "PMZ": Image.open("../assets/PMZ.png"), "PPC": Image.open("../assets/PPC.png"), "PPF": Image.open("../assets/PPF.png"),
               "PPV": Image.open("../assets/PPV.png"), "PS": Image.open("../assets/PS.png"), "PS2": Image.open("../assets/PS2.png"),
               "PV": Image.open("../assets/PV.png"), "PX": Image.open("../assets/PX.png"), "PZ": Image.open("../assets/PZ.png")}

# Same grid information, offSetHorizontal offsets to the play field (where user puts gates)
# from the gate storage and barrier positions
currentWidth = 8
currentHeight = 6
offSetHorizontal = 3

customGates = {}
positionsWithCustomGates = {(-1, -1): "NA"}
undoStack = []
redoStack = []

# Default to the "-" gate, store previous position of barrier
grid = [["-" for i in range(currentWidth + offSetHorizontal)] for j in range(currentHeight)]
priorBarrier = [-1,-1,-1,-1]

# Initalize Designer
designer = DesignerFile.Designer(currentHeight, currentWidth)

# Various graphics settings
hamiltonian = False
needToUpdate = False
photonicMode = False

# Specific global state for DWave Annealer
DWaveVar = ""
DWaveCon = ""
DwaveObjective = ""

# For field elements that complete change layout
def forceUpdate():
    global window
    window.close()
    window = Window()
    window.show()

gmail = EmailSender(
    host='smtp.office365.com',
    port=587,
    username="quantumcircuits@outlook.com",
    password="dylansheils0241"
)

# Cursed as it is, this is a lookup table to store the inital gate positions
def inital(row, col):
    if(photonicMode == False):
        if(row == 0 and col == 0):
            return "H"
        if(row == 0 and col == 1):
            return "X"
        if(row == 1 and col == 0):
            return "Y"
        if(row == 1 and col == 1):
            return "Z"
        if(row == 2 and col == 0):
            return "S"
        if(row == 2 and col == 1):
            return "T"
        if(row == 3 and col == 0):
            return "CNOT"
        if(row == 3 and col == 1):
            if(len(customGates) != 0):
                return list(customGates.keys())[0]
        if(row == 4 and col == 0):
            if(len(customGates) > 1):
                return list(customGates.keys())[1]
        if(row == 4 and col == 1):
            if(len(customGates) > 2):
                return list(customGates.keys())[2]
    else:
        if(row == 0 and col == 0):
            return "PX"
        if(row == 0 and col == 1):
            return "PZ"
        if(row == 0 and col == 2):
            return "PS"
        if(row == 0 and col == 3):
            return "PS2"
        if(row == 1 and col == 0):
            return "PMZ"
        if(row == 1 and col == 1):
            return "PCX"
        if(row == 1 and col == 2):
            return "PD"
        if(row == 1 and col == 3):
            return "PF"
        if(row == 2 and col == 0):
            return "PBS"
        if(row == 2 and col == 1):
            return "PCK"
        if(row == 2 and col == 2):
            return "PPC"
        if(row == 2 and col == 3):
            return "PPF"
        if(row == 3 and col == 0):
            return "PPV"
        if(row == 3 and col == 1):
            if(len(customGates) != 0):
                return list(customGates.keys())[0]
        if(row == 3 and col == 2):
            if(len(customGates) > 1):
                return list(customGates.keys())[1]
        if(row == 3 and col == 3):
            if(len(customGates) > 2):
                return list(customGates.keys())[2]
    return " "


# This runs the simulation
def runSimulation():
    print("---------------------Running Simulation-------------------------------------")
    # PENDING upon which BACKEND is selected, the control flow is different [might need other GUI settings]
    #run simulation with Dwave ocean
    if (designer.settings.backend == "DWaveSimulation"):
        print("User Variables added: \n")

        #get user's input variables as plain text and split
        #then add each unique line to backend
        variables = DWaveVar.strip().split("\n")
        variables = list(set(variables))
        for variable in variables:
            designer.addVariable(variable)
            print(variable)

        print("User constraint added: \n")
        #get user's input constraint as plain text and split
        #then add each unique line to backend
        constraints = DWaveCon.strip().split("\n")
        constraints = list(set(constraints))
        for constraint in constraints:
            designer.addConstraint(constraint)
            print(constraint)

        #get user's input objective
        print("Objective set to: \n")
        global DwaveObjective
        print(DwaveObjective)
        objective = DwaveObjective
        designer.setObjective(objective)
        print(objective)
        designer.runSimulation()
        plt = designer.getVisualization()
        plt.show()
    else:
        # If not qubo optimization, it is a circuit problem, so display it
        print("Quantum Circuit Printout: ")
        print(grid)
        numDepth = currentWidth
        numQubits = currentHeight
        entry = ""
        for depth in range(3*(numDepth+1)):
            entry += "-"
        print(entry)
        starredPositions = {(-1,-1)}
        for qubit in range(numQubits):
            tempStr = ""
            nextOne = False
            for depth in range(offSetHorizontal, numDepth):
                if((qubit, depth) in starredPositions):
                    tempStr += "[*]"
                else:
                    designer.gateAddition(grid[qubit][depth], depth-offSetHorizontal, qubit)
                    tempStr += "[" + grid[qubit][depth] + "]"
                if(len(grid[qubit][depth]) >= 3 and "PP" not in grid[qubit][depth]):
                    starredPositions.add((qubit + 1, depth))
                tempStr += "[M]"
            print(tempStr)
        print(entry)
        print("------------------------BACKEND GOT-------------------------------------")
        # Have the designer confirm the board (for debugging)
        designer.printDesign()
        # Run the simulation
        designer.runSimulation()
        # Get the output
        plt = designer.getVisualization()
        plt.show()

#changes settingfile based on user choice
def changeSimulationTechniqueHamiltonian():
    designer.setBackend("HamiltionSimulation")
    print("Changed backend to Hamiltion Simulation")
def changeSimulationTechniqueFeynman():
    designer.setBackend("FeynmanSimulation")
    print("Changed backend to Feynman Simulation")
def changeSimulationTechniqueDWave():
    designer.setBackend("DWaveSimulation")
    print("Changed backend to DWave Ocean")
def changeSimulationTechniqueIBM():
    designer.setBackend("IBMSimulation")
    print("Changed backend to IBM Xanadu")
def changeSimulationTechniqueQiskit():
    designer.setBackend("Qiskit")
    print("Changed to Qiskit Backend")
def changeSimulationTechniqueXanadu():
    designer.setBackend("Photonic")
    print("Changed to Xanadu Photonic Backend")

# Change Various settings based on click events, self-explanatory
def changeMeasurement(checked):
    designer.settings.measurement = checked
    print("Set measurement to " + str(checked))
def changeSuggestion(checked):
    designer.settings.gate_suggestion = checked
    designer.suggestSimplifications(grid)
    print("Set gate suggestion to " + str(checked))
def changeIncresav(checked):
    designer.settings.incremental_saving = checked
    print("Set incremental saving to " + str(checked))
def changeIncresim(checked):
    designer.settings.incremental_simulation = checked
    print("Set incremental simulation to " + str(checked))
def updateNumQubit(val):
    designer.settings.num_qubits = val
    global currentHeight
    currentHeight = val
    print("Set number of qubits to " + str(val))

# This is a less forceful update that changes whenever the GUI is interacted with
def updateGrid():
    global grid
    global needToUpdate
    grid = designer.getGUIGrid()
    needToUpdate = True

# Changes Width of Quantum Circuit
def updateNumWidth(val):
    designer.settings.num_width = val
    global currentWidth
    currentWidth = val
    print("Set width to " + str(val))

#the main window for display
class Window(QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.grid = IndicSelectWindow()
        self.originalPalette = QApplication.palette()

        background = QComboBox()
        background.addItems(QStyleFactory.keys())

        #top menu bar for operations
        menu = self.menuBar()
        file_menu = QMenu("&File", self)
        menu.addMenu(file_menu)
        button_class = QMenu("&Class", self)
        menu.addMenu(button_class)
        button_learn = QMenu("&Learn", self)
        menu.addMenu(button_learn)
        button_dwave = QAction("&DWave", self)
        menu.addAction(button_dwave)

        button_custom_gate = QAction("&Custom Gate Creation", self)
        menu.addAction(button_custom_gate)
        #self.custom_gate_tab = CustomGateTab(self)
        button_custom_gate.triggered.connect(lambda: self.makeCustomGate())

        #intialize dwave tab for user input
        self.dwave_tab = DWaveTab(self)
        button_dwave.triggered.connect(lambda: self.showDWaveTab())
        #other menu bars
        button_qiskit = QMenu("&Qiskit", self)
        menu.addMenu(button_qiskit)
        button_xanadu = QMenu("&IBM Xanadu", self)
        menu.addMenu(button_xanadu)
        button_exit = QAction("&Exit", self)
        menu.addAction(button_exit)
        #additional exit button (why not)
        button_exit.triggered.connect(lambda: self.closeEvent())

        #file I/O actions
        save = QAction("&Save", self)
        load = QAction("&Load", self)
        email = QAction("&Email", self)
        undo = QAction("&Undo", self)
        redo = QAction("&Redo", self)
        file_menu.addAction(save)
        file_menu.addAction(load)
        file_menu.addAction(email)
        file_menu.addAction(undo)
        file_menu.addAction(redo)
        save.triggered.connect(lambda: self.saveFile())
        load.triggered.connect(lambda: self.loadFile())
        email.triggered.connect(lambda: self.emailFile())
        undo.triggered.connect(lambda: self.undo())
        redo.triggered.connect(lambda: self.redo())

        #create simulation settings layout and running layout
        self.createSimulationSetting()
        self.createSimulationRunning()

        #right side toolbar to hold simulation settings
        setting = QToolBar()
        setting.addWidget(self.SimulationChoice)
        setting.addWidget(self.SimulationSetting)
        self.addToolBar(Qt.RightToolBarArea, setting)

        #display grid as central widget
        self.setCentralWidget(self.grid)

        #set fixed size for drag & drop precision
        self.setWindowTitle("Designer")
        self.changeStyle('fusion')

    def emailFile(self):
        global designer
        designer.giveGUIGrid(grid)
        designer.runSimulation()
        designer.saveSimulationToFile("email.qc")
        address = QtWidgets.QInputDialog.getText(self, 'Email Address', 'Email Address:')[0]
        subjectLine = QtWidgets.QInputDialog.getText(self, 'Subject', 'Subject:')[0]
        gmail.send(
            subject=subjectLine,
            receivers=[address],
            text="Using the QuantumCircuit Open-Source Software!",
            attachments={
                "email.qc": Path("email.qc"),
            }
        )
        print("Email Sent!")


    def saveFile(self):
        path=QFileDialog.getSaveFileName(self, "Choose Directory","E:\\")
        #print(path[0] + ".qc")
        designer.giveGUIGrid(grid)
        designer.runSimulation()
        designer.saveSimulationToFile(path[0] + ".qc")

    def loadFile(self):
        dir_path=QFileDialog.getOpenFileName(self, "Choose .qc file","E:\\")
        print(dir_path[0])
        designer.loadSimulationFromFile(dir_path[0])
        updateGrid()
        designer.printDesign()

    def undo(self):
        f = tempfile.NamedTemporaryFile(delete=False)
        designer.saveSimulationToFile(f.name)
        redoStack.append(f.name)
        f.close()
        f = undoStack.pop()
        designer.loadSimulationFromFile(f)
        os.remove(f)
        updateGrid()
        designer.printDesign()

    def redo(self):
        f = tempfile.NamedTemporaryFile(delete=False)
        designer.saveSimulationToFile(f.name)
        undoStack.append(f.name)
        f.close()
        f = redoStack.pop()
        designer.loadSimulationFromFile(f)
        os.remove(f)
        updateGrid()
        designer.printDesign()


    #override close event to make sure pop-up window will close when
    #main window is close, otherwise a not-responding pop-up will remain
    #after main window is closed
    def closeEvent(self, event):
        if (self.dwave_tab):
            self.dwave_tab.close()           
        self.close()
        for f in undoStack:
            try:
                os.remove(f)
            except:
                pass
        for f in redoStack:
            try:
                os.remove(f)
            except:
                pass

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))
        self.changePalette()

    def changePalette(self):
        QApplication.setPalette(self.originalPalette)

    #create interface for running simulation
    def createSimulationRunning(self):
        self.SimulationChoice = QGroupBox("Running Simulation")
        button1 = QPushButton()
        button1.setText("Run")
        button1.clicked.connect(runSimulation)
        layout = QVBoxLayout()
        layout.addWidget(button1)
        layout.addStretch(1)
        self.SimulationChoice.setLayout(layout)

    #a function that changes setting file and backend based on user's choice
    def updateSimulationTechnique(self, i):
        if("H" in self.sim_box.currentText()):
            changeSimulationTechniqueHamiltonian()
        elif("F" in self.sim_box.currentText()):
            changeSimulationTechniqueFeynman()
        elif("D" in self.sim_box.currentText()):
            if self.external_sim_msg.msg_toggle:
                self.external_sim_msg.exec()
            changeSimulationTechniqueDWave()
        elif("Q" in self.sim_box.currentText()):
            if self.external_sim_msg.msg_toggle:
                self.external_sim_msg.exec()
            changeSimulationTechniqueQiskit()
        elif("X" in self.sim_box.currentText()):
            if self.external_sim_msg.msg_toggle:
                self.external_sim_msg.exec()
            changeSimulationTechniqueXanadu()
        else:
            if self.external_sim_msg.msg_toggle:
                self.external_sim_msg.exec()
            changeSimulationTechniqueIBM()

    #a function that allows user to set external backend warning msg off
    def externalMsgToggle(self, pushed):
        if (pushed.text() == "Ignore"):
            self.external_sim_msg.msg_toggle = False;

    #create interface for simulation settings
    def createSimulationSetting(self):
        self.SimulationSetting = QGroupBox("Simulation Setting")

        layout = QVBoxLayout()
        #check box for measurement, setting will be updated once toggled
        measurement = QCheckBox("Measurement")
        measurement.toggled.connect(self.TypeOnClicked)
        measurement.callsign = "measurement"
        layout.addWidget(measurement)

        #check box for gate suggestion, setting will be updated once toggled
        gate_suggestion = QCheckBox("Gate Sugguestion")
        gate_suggestion.toggled.connect(self.TypeOnClicked)
        gate_suggestion.callsign = "suggestion"
        layout.addWidget(gate_suggestion)

        #check box for incremental saving, setting will be updated once toggled
        incremental_saving = QCheckBox("Incremental Saving")
        incremental_saving.toggled.connect(self.TypeOnClicked)
        layout.addWidget(incremental_saving)
        incremental_saving.callsign = "incresav"

        #check box for incremental simulation, setting will be updated once toggled
        incremental_simulation = QCheckBox("Incremental Simulation")
        incremental_simulation.toggled.connect(self.TypeOnClicked)
        layout.addWidget(incremental_simulation)
        incremental_simulation.callsign = "incresim"

        #check box for photonic mode, setting will be updated once toggled
        photonicMode = QCheckBox("Photonic Mode")
        photonicMode.toggled.connect(self.TypeOnClicked)
        layout.addWidget(photonicMode)
        photonicMode.callsign = "photonic"

        # Various other field boxes, obvious based on titling
        noice_label = QLabel("Noice Model")
        noice_selection = ["none", "other..."]
        noice_box = QComboBox()
        noice_box.addItems(noice_selection)
        layout.addWidget(noice_label)
        layout.addWidget(noice_box)

        optimization_label = QLabel("Optimization")
        optimization_selection = ["none", "other..."]
        optimization_box = QComboBox()
        optimization_box.addItems(optimization_selection)

        num_qubits = QSpinBox(self.SimulationSetting)
        num_qubits.setValue(5)
        num_qubits.callsign = "numqubit"
        qubit_label = QLabel("&Number of Qubits: ")
        qubit_label.setBuddy(num_qubits)
        num_qubits.valueChanged.connect(self.UpdateParameters)

        num_width = QSpinBox(self.SimulationSetting)
        num_width.setValue(8)
        num_width.callsign = "numwidth"
        width_label = QLabel("&Width: ")
        num_width.valueChanged.connect(self.UpdateParameters)

        #a message box that tells user external backend has been selected
        #'ignore' button has been overriden so that
        #click on it will let message never pop-up again
        self.external_sim_msg = QMessageBox()
        self.external_sim_msg.setIcon(QMessageBox.Information)
        self.external_sim_msg.setWindowTitle("External backend")
        self.external_sim_msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Ignore)
        #message on display
        self.external_sim_msg.setText("You have chosen an external backend. QCD will now run your circuit design on an external backend.")
        self.external_sim_msg.setInformativeText("Some external backend have different behaviors when accepting input. You can access their features via the menu bar. ")
        self.external_sim_msg.msg_toggle = True;
        self.external_sim_msg.buttonClicked.connect(self.externalMsgToggle)

        # Simulation selection panel
        Simulation = QLabel("Simulation Technique")
        sim_selection = ["Hamiltionian", "Feynman", "DWave Ocean", "Qiskit", "IBM", "Xanadu"]
        self.sim_box = QComboBox()
        self.sim_box.addItems(sim_selection)
        self.sim_box.currentIndexChanged.connect(self.updateSimulationTechnique)

        layout.addWidget(Simulation)
        layout.addWidget(self.sim_box)

        width_label.setBuddy(num_width)
        layout.addWidget(optimization_label)
        layout.addWidget(optimization_box)
        layout.addWidget(qubit_label)
        layout.addWidget(num_qubits)
        layout.addWidget(width_label)
        layout.addWidget(num_width)

        layout.addStretch(1)
        self.SimulationSetting.setLayout(layout)

    #integration function that connects checkboxs on gui to backend
    def TypeOnClicked(self):
        Button = self.sender()
        designer.settings.measurement = Button.isChecked()
        if (Button.callsign == "measurement"):
            changeMeasurement(Button.isChecked())
        elif (Button.callsign == "suggestion"):
            changeSuggestion(Button.isChecked())
        elif (Button.callsign == "incresav"):
            changeIncresav(Button.isChecked())
        elif (Button.callsign == "incresim"):
            changeIncresim(Button.isChecked())
        elif (Button.callsign == "photonic"):
            # Photonic Switch requires a forced update (different width and gate sets)
            print("Update to Photonic Mode...")
            global photonicMode
            global offSetHorizontal
            global grid
            global currentWidth
            global currentHeight
            photonicMode = not photonicMode
            offSetHorizontal = 5
            grid = [["-" for i in range(currentWidth + offSetHorizontal)] for j in range(currentHeight)]
            global needToUpdate
            needToUpdate = False
            forceUpdate()

    # Updates parameters locally and calls for forced change
    def UpdateParameters(self):
        spin = self.sender()
        val = spin.value()
        if (spin.callsign == "numqubit"):
            updateNumQubit(val)
            forceUpdate()
        elif (spin.callsign == "numwidth"):
            updateNumWidth(val)
            forceUpdate()

    def makeCustomGate(self):
        x1 = QtWidgets.QInputDialog.getInt(self, 'X1', 'Input:')
        if (x1[1] == True):
            print(x1[0])
            x2 = QtWidgets.QInputDialog.getInt(self, 'X2', 'Input:')
            if (x2[1] == True):
                print(x2[0])
                y1 = QtWidgets.QInputDialog.getInt(self, 'Y1', 'Input:')
                if (y1[1] == True):
                    print(y1[0])
                    y2 = QtWidgets.QInputDialog.getInt(self, 'Y2', 'Input:')
                    if (y2[1] == True):
                        print(y2[0])

        print(grid[y1[0]][x1[0] + offSetHorizontal])
        print(grid[y2[0]][x2[0] + offSetHorizontal])

        customGrid = [["-" for i in range(x2[0]-x1[0]+1)] for j in range(y2[0]-y1[0]+1)]

        xItr = 0
        yItr = 0
        for i in range(y1[0], y2[0] + 1):
            for j in range(x1[0], x2[0] + 1):
                customGrid[i-y1[0]][j-x1[0]] = grid[i][j+offSetHorizontal]

        customGateName = QtWidgets.QInputDialog.getText(self, 'Custom Gate Name', 'Input:')
        print(customGateName)
        if(customGateName[1] == False):
            return

        customGates[customGateName[0]] = customGrid

        forceUpdate()
        self.grid.updateGUILayout()
        print("--------------------------------------")
        for i in range(len(grid)):
            strtemp = ""
            for j in range(len(grid[0])):
                strtemp += grid[i][j]
            print(strtemp)
        print("--------------------------------------")

        print(customGates)

    #let Dwave input tab show when user clicks on toolbar
    def showDWaveTab(self):
        self.dwave_tab.show()


#a Qdialog that pops up when use clicks the 'DWave' button on toolbar
class DWaveTab(QDialog):
    def __init__(self, parent=Window):
        super(DWaveTab, self).__init__(parent=parent)
        self.layout = QVBoxLayout(self)

        #basic initialization
        self.setWindowTitle("DWave Ocean")
        self.tabs = QTabWidget()
        self.tab_addvar = QWidget()
        self.tab_addcon = QWidget()
        self.tab_addobj = QWidget()

        #add two tabs, one for varaible, one for constraints
        self.tabs.addTab(self.tab_addvar, "Add Variable")
        self.tabs.addTab(self.tab_addcon, "Add Constraints")
        self.tabs.addTab(self.tab_addobj, "Set Objective")

        # Various grid elements necessary for extracting necessary information for optimization problem
        self.tab_addvar.layout = QVBoxLayout(self)
        self.dwave_var = QTextEdit()
        self.dwave_var.setPlaceholderText("Add your variable here. (i.e. 'a = Binary(\"a\")')\n")
        self.tab_addvar.layout.addWidget(self.dwave_var)
        self.tab_addvar.setLayout(self.tab_addvar.layout)

        self.tab_addcon.layout = QVBoxLayout(self)
        self.dwave_con = QTextEdit()
        self.dwave_con.setPlaceholderText("Add your constraints here.")
        self.tab_addcon.layout.addWidget(self.dwave_con)
        self.tab_addcon.setLayout(self.tab_addcon.layout)

        self.tab_addobj.layout = QVBoxLayout(self)
        self.dwave_obj = QLineEdit()
        self.dwave_obj.setPlaceholderText("Set your objective here. (i.e. 'max ((a + b)*e + (c + d))\n")
        self.tab_addobj.layout.addWidget(self.dwave_obj)
        self.tab_addobj.setLayout(self.tab_addobj.layout)

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        self.resize(800, 600)

    #override close event to update the text we got from user when tab is closed
    def closeEvent(self, event):
        global DWaveVar
        global DWaveCon
        global DwaveObjective
        DWaveVar = self.dwave_var.toPlainText()
        DWaveCon = self.dwave_con.toPlainText()
        DwaveObjective = self.dwave_obj.text()
        self.close()

#the main workbench of qcd, a grid that supports drag & drop
class IndicSelectWindow(QDialog):
    def __init__(self, parent=None):
        super(IndicSelectWindow, self).__init__(parent=parent)
        self.resize(3000, 1200)
        self.target = None
        self.setAcceptDrops(True)
        self.layout = QHBoxLayout(self)
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.gridLayout = QGridLayout(self.scrollAreaWidgetContents)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.layout.addWidget(self.scrollArea)

        # Go through the grid and initalize values
        skipThis = [-1, -1] # For multiqubit gates, skip initalizing covered positions
        for j in range(1, offSetHorizontal + 1):
            for i in range(currentHeight):
                if(skipThis[0] == i and skipThis[1] == j):
                    grid[i][j - 1] = " "
                    break
                grid[i][j-1] = " "
                self.Frame = QFrame(self)
                self.Frame.setStyleSheet("background-color: white;")
                self.Frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
                self.Frame.setLineWidth(0)
                self.layout = QHBoxLayout(self.Frame)

                self.figure = Figure()  # a figure to plot on
                self.canvas = FigureCanvas(self.figure)
                self.ax = self.figure.add_subplot(111)  # create an axis
                if(j == offSetHorizontal):  # If we need to create the barrier
                    self.Frame.setStyleSheet("background-color: grey;")
                    Box = QVBoxLayout()
                    Box.addWidget(self.Frame)
                    self.gridLayout.addLayout(Box, i, j-1, len(grid)-2, 1)
                    global priorBarrier
                    priorBarrier = [i, j - 1, len(grid)-2, 1]
                else: # If we are adding just a gate
                    global customGates
                    grid[i][j - 1] = inital(i, j - 1) # Find what gate if any should go in position
                    if(grid[i][j - 1] in customGates):
                        self.ax.text(0.5, 0.5, grid[i][j - 1], horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes)
                    else:
                        self.ax.imshow(gateToImage[grid[i][j - 1]]) # Show the gate
                    self.ax.set_axis_off()
                    self.canvas.draw()  # refresh canvas
                    self.layout.addWidget(self.canvas)
                    self.canvas.installEventFilter(self)
                    Box = QVBoxLayout()
                    Box.addWidget(self.Frame)
                    self.gridLayout.addLayout(Box, i, j - 1)
        # Go through and initalize field user interacts with
        for i in range(offSetHorizontal, currentWidth + offSetHorizontal):
            for j in range(currentHeight):
                grid[j][i] = "-"
                self.Frame = QFrame(self)
                self.Frame.setStyleSheet("background-color: white;")
                self.Frame.setLineWidth(0)
                self.layout = QHBoxLayout(self.Frame)

                self.figure = Figure()  # a figure to plot on
                self.canvas = FigureCanvas(self.figure)
                self.ax = self.figure.add_subplot(111)  # create an axis
                self.ax.imshow(gateToImage["-"])
                self.ax.set_axis_off()
                self.canvas.draw()  # refresh canvas
                self.canvas.installEventFilter(self)

                self.layout.addWidget(self.canvas)

                Box = QVBoxLayout()

                Box.addWidget(self.Frame)

                self.gridLayout.addLayout(Box, j, i)

    # Run fo the mill event filter
    def eventFilter(self, watched, event):
        if event.type() == QEvent.MouseButtonPress:
            self.mousePressEvent(event)
        elif event.type() == QEvent.MouseMove:
            self.mouseMoveEvent(event)
        elif event.type() == QEvent.MouseButtonRelease:
            self.mouseReleaseEvent(event)
        return super().eventFilter(watched, event)

    # Allow easy access to grid index from gridLayout position
    def get_index(self, pos):
        for i in range(self.gridLayout.count()):
            if self.gridLayout.itemAt(i).geometry().contains(pos) and i != self.target:
                return i

    # Load up source information if user clicks a gate
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.target = self.get_index(event.windowPos().toPoint())
        else:
            self.Frame = QFrame(self)
            self.Frame.setStyleSheet("background-color: white;")
            self.Frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
            self.Frame.setLineWidth(0)
            self.layout = QHBoxLayout(self.Frame)

            self.figure = Figure()  # a figure to plot on
            self.canvas = FigureCanvas(self.figure)
            self.ax = self.figure.add_subplot(111)  # create an axis
            row, col, _, _ = self.gridLayout.getItemPosition(self.get_index(event.windowPos().toPoint()))
            self.ax.imshow(grid[row][col])
            self.canvas.draw()  # refresh canvas
            self.canvas.installEventFilter(self)

            self.layout.addWidget(self.canvas)

            Box = QVBoxLayout()

            Box.addWidget(self.Frame)

            self.gridLayout.addLayout(Box, 0, 6)
            self.gridLayout.setColumnStretch(6, 1)
            self.gridLayout.setRowStretch(0, 1)
    # If moving the mouse, bring the element with you
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.target is not None:
            drag = QDrag(self.gridLayout.itemAt(self.target))
            pix = self.gridLayout.itemAt(self.target).itemAt(0).widget().grab()
            mimedata = QMimeData()
            mimedata.setImageData(pix)
            drag.setMimeData(mimedata)
            drag.setPixmap(pix)
            drag.setHotSpot(event.pos())
            drag.exec_()
        global needToUpdate
        global grid
        global positionsWithCustomGates
        # If we need to update the grid, update all positions to have GUI be consistent with Grid 2D array
        if needToUpdate:
            print("Updating....")
            needToUpdate = False
            skipThis = [-1, -1]
            skip = {(-1, -1)}
            for i in range(offSetHorizontal, currentWidth + offSetHorizontal):
                for j in range(currentHeight):
                    self.Frame = QFrame(self)
                    self.Frame.setStyleSheet("background-color: white;")
                    self.Frame.setLineWidth(0)
                    self.layout = QHBoxLayout(self.Frame)

                    self.figure = Figure()  # a figure to plot on
                    self.canvas = FigureCanvas(self.figure)
                    self.ax = self.figure.add_subplot(111)  # create an axis
                    if((j, i) not in positionsWithCustomGates and (j, i) not in skip):
                        if (grid[j][i] not in customGates):
                            self.ax.imshow(gateToImage[grid[j][i]])
                        else:
                            self.ax.text(0.5, 0.5, grid[j][i], horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes)
                        self.ax.set_axis_off()
                        self.canvas.draw()  # refresh canvas
                        self.canvas.installEventFilter(self)
                        self.layout.addWidget(self.canvas)
                        Box = QVBoxLayout()
                        Box.addWidget(self.Frame)
                        self.gridLayout.removeItem(self.gridLayout.itemAtPosition(j, i))
                        self.gridLayout.addLayout(Box, j, i)
                    else:
                        if((j, i) not in skip):
                            name = positionsWithCustomGates[(j, i)]
                            self.ax.set_axis_off()
                            self.canvas.draw()  # refresh canvas
                            self.canvas.installEventFilter(self)
                            self.layout.addWidget(self.canvas)
                            Box = QVBoxLayout()
                            Box.addWidget(self.Frame)
                            self.gridLayout.addLayout(Box, j, i, len(customGates[name][0]), len(customGates[name][1]))
                            for x in range(len(customGates[name][0])):
                                for y in range(len(customGates[name][1])):
                                    skip.add((j + x, i + y))
                                    self.gridLayout.removeItem(self.gridLayout.itemAtPosition(j + x, i + y))

    # If releasing, event on drag and drop occured, so neglect this gate
    def mouseReleaseEvent(self, event):
        self.target = None

    # Only allow gates to be draggable elements
    def dragEnterEvent(self, event):
        if event.mimeData().hasImage():
            event.accept()
        else:
            event.ignore()

    # Handle drop logic
    def dropEvent(self, event):
        if not event.source().geometry().contains(event.pos()):
            source = self.get_index(event.pos())
            if source is None:
                return
            # Get source and destination points
            i, j = max(self.target, source), min(self.target, source)
            row, col, _, _ = self.gridLayout.getItemPosition(self.target)
            row2, col2, _, _ = self.gridLayout.getItemPosition(source)
            global positionsWithCustomGates
            global customGates
            # If it is a photonic gate, get necessary values for gate specification
            global photonicMode
            if (photonicMode == True):
                val1, val2 = 0.0, 0.0
                val1 = QtWidgets.QInputDialog.getDouble(self, 'First Gate Argument', 'Input:')[0]
                val2 = QtWidgets.QInputDialog.getDouble(self, 'Second Gate Argument', 'Input:')[0]
                global designer
                global offSetHorizontal
                # Specify the gate properties
                designer.settings.specialGridSettings[(col2-offSetHorizontal,row2)] = [val1, val2]
                print(designer.settings.specialGridSettings)

            p1, p2 = self.gridLayout.getItemPosition(self.target), self.gridLayout.getItemPosition(source)
            # If we are moving a point on the user board, replace positions
            if(self.gridLayout.getItemPosition(self.target)[1] < offSetHorizontal):
                designer.giveGUIGrid(grid)
                f = tempfile.NamedTemporaryFile(delete=False)
                designer.saveSimulationToFile(f.name)
                undoStack.append(f.name)
                f.close()
                self.Frame = QFrame(self)
                self.Frame.setStyleSheet("background-color: white;")
                self.Frame.setLineWidth(0)
                self.layout = QHBoxLayout(self.Frame)
                self.figure = Figure()  # a figure to plot on
                self.canvas = FigureCanvas(self.figure)
                self.ax = self.figure.add_subplot(111)  # create an axis
                isCustom = False
                if(inital(row, col) not in customGates):
                    self.ax.imshow(gateToImage[inital(row, col)])
                else:
                    self.ax.text(0.5, 0.5, inital(row, col), horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes)
                    isCustom = True
                    print("Dropped Custom (Drag and Drop)")
                if((row, col) in positionsWithCustomGates):
                    isCustom = True
                    grid[row][col]
                self.ax.set_axis_off()
                self.canvas.draw()  # refresh canvas
                self.canvas.installEventFilter(self)
                self.layout.addWidget(self.canvas)
                Box = QVBoxLayout()
                Box.addWidget(self.Frame)
                self.gridLayout.takeAt(source)
                if(isCustom):
                    print("Calling updateGUILayout")
                    grid[row2][col2] = grid[row][col]
                    self.updateGUILayout()
                else:
                    self.gridLayout.addLayout(Box, row2, col2) #row2, col2
                    grid[row2][col2] = grid[row][col]
            else: # Else, ONLY move the gate in the user board
                isCustom = False
                if((row, col) in positionsWithCustomGates):
                    name = positionsWithCustomGates[(row, col)]
                    for x in range(len(customGates[name][0])):
                        for y in range(len(customGates[name][1])):
                            grid[row + x][col + y] = "-"
                            self.gridLayout.removeItem(self.gridLayout.itemAtPosition(row + x, col + y))
                    grid[row][col] = name
                    self.gridLayout.removeItem(self.gridLayout.itemAtPosition(row, col))
                    del positionsWithCustomGates[(row, col)]
                    isCustom = True
                if((row2, col2) in positionsWithCustomGates):
                    name = positionsWithCustomGates[(row2, col2)]
                    for x in range(len(customGates[name][0])):
                        for y in range(len(customGates[name][1])):
                            grid[row2 + x][col2 + y] = "-"
                            self.gridLayout.removeItem(self.gridLayout.itemAtPosition(row2 + x, col2 + y))
                    grid[row2][col2] = name
                    self.gridLayout.removeItem(self.gridLayout.itemAtPosition(row2, col2))
                    del positionsWithCustomGates[(row2, col2)]
                    isCustom = True
                grid[row][col], grid[row2][col2] = grid[row2][col2], grid[row][col]
                if(isCustom):
                    print("Calling updateGUILayout")
                    self.canvas.draw()
                    self.updateGUILayout()
                else:
                    tempA = self.gridLayout.itemAtPosition(row, col)
                    tempB = self.gridLayout.itemAtPosition(row2, col2)
                    self.gridLayout.removeItem(self.gridLayout.itemAtPosition(row, col))
                    self.gridLayout.removeItem(self.gridLayout.itemAtPosition(row2, col2))
                    self.gridLayout.addItem(tempA, *p2)
                    self.gridLayout.addItem(tempB, *p1)

            # Print out the grid (for debugging purposes)
            print("Quantum Circuit Printout:")
            print(grid)
            numDepth = currentWidth
            numQubits = currentHeight
            entry = ""
            for depth in range(3*(numDepth+1)):
                entry += "-"
            print(entry)
            starredPositions = {(-1,-1)}
            for qubit in range(numQubits):
                tempStr = ""
                nextOne = False
                for depth in range(offSetHorizontal, numDepth + offSetHorizontal):
                    if((qubit, depth) in starredPositions):
                        tempStr += "[*]"
                    else:
                        tempStr += "[" + grid[qubit][depth] + "]"
                    if(len(grid[qubit][depth]) >= 3 and "PP" not in grid[qubit][depth]):
                        starredPositions.add((qubit + 1, depth))
                tempStr += "[M]"
                print(tempStr)
            print(entry)

    #update layout basesd on designer class' grid
    def updateGUILayout(self):
        global priorBarrier
        global offSetHorizontal
        global grid
        global currentHeight
        global customGates
        global positionsWithCustomGates
        global currentWidth
        # Basically a repeat from GUI initalization, see those comments for explainations
        skipThis = [-1, -1]
        print("Is this it?")
        for j in range(1, offSetHorizontal + 1):
            for i in range(currentHeight):
                if(skipThis[0] == i and skipThis[1] == j):
                    grid[i][j - 1] = "-"
                    break
                grid[i][j-1] = "-"
                self.Frame = QFrame(self)
                self.Frame.setStyleSheet("background-color: white;")
                self.Frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
                self.Frame.setLineWidth(0)
                self.layout = QHBoxLayout(self.Frame)

                self.figure = Figure()  # a figure to plot on
                self.canvas = FigureCanvas(self.figure)
                self.ax = self.figure.add_subplot(111)  # create an axis
                if(j == offSetHorizontal):
                    self.Frame.setStyleSheet("background-color: grey;")
                    Box = QVBoxLayout()
                    Box.addWidget(self.Frame)
                    self.gridLayout.addLayout(Box, i, j-1, len(grid)-2, 1)
                    priorBarrier = [i, j-1, len(grid)-2, 1]
                else:
                    grid[i][j - 1] = inital(i, j - 1)
                    if(grid[i][j - 1] not in customGates):
                        self.ax.imshow(gateToImage[grid[i][j - 1]])
                    else:
                        self.ax.text(0.5, 0.5, grid[j][i-1], horizontalalignment='center', verticalalignment='center',transform=self.ax.transAxes)
                    self.ax.set_axis_off()
                    self.canvas.draw()  # refresh canvas
                    self.layout.addWidget(self.canvas)
                    self.canvas.installEventFilter(self)
                    Box = QVBoxLayout()
                    Box.addWidget(self.Frame)
                    self.gridLayout.addLayout(Box, i, j - 1)
        skip = []
        for i in range(offSetHorizontal, currentWidth + offSetHorizontal):
            for j in range(currentHeight):
                self.Frame = QFrame(self)
                self.Frame.setStyleSheet("background-color: white;")
                self.Frame.setLineWidth(0)
                self.layout = QHBoxLayout(self.Frame)

                self.figure = Figure()  # a figure to plot on
                self.canvas = FigureCanvas(self.figure)
                self.ax = self.figure.add_subplot(111)  # create an axis
                isCustom = False
                name = "NA"
                if(grid[j][i] not in customGates and (j, i) not in positionsWithCustomGates):
                    self.ax.imshow(gateToImage[grid[j][i]])
                else:
                    if((j, i) not in positionsWithCustomGates):
                        self.Frame.setStyleSheet("background-color: black;")
                        self.ax.text(0.2, 0.75, grid[j][i], horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes)
                        self.ax.imshow(gateToImage[" "])
                        isCustom = True
                        print("Custom Detected")
                        name = grid[j][i]
                    else:
                        name = positionsWithCustomGates[(j, i)]
                        for x in range(len(customGates[name][0])):
                            for y in range(len(customGates[name][1])):
                                skip.append((j + x, i + y))
                                self.gridLayout.removeItem(self.gridLayout.itemAtPosition(j + x, i + y))
                        self.gridLayout.addLayout(Box, j, i, len(customGates[name][0]), len(customGates[name][1]))
                if((j, i) in skip):
                    self.ax.imshow(gateToImage[" "])
                    self.Frame.setStyleSheet("background-color: black;")
                self.ax.set_axis_off()
                self.canvas.draw()  # refresh canvas
                self.canvas.installEventFilter(self)
                self.layout.addWidget(self.canvas)
                Box = QVBoxLayout()
                Box.addWidget(self.Frame)
                if(not isCustom):
                    self.gridLayout.addLayout(Box, j, i)
                else:
                    self.gridLayout.addLayout(Box, j, i, len(customGates[name][0]), len(customGates[name][1]))
                    for x in range(len(customGates[name][0])):
                        for y in range(len(customGates[name][1])):
                            grid[j+x][i+y] = (customGates[name])[x][y]
                            skip.append((j+x, i+y))
                    positionsWithCustomGates[(j, i)] = name
        print("UPDATED-------------------")
# Create the application, window, and close application if asked
app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec_())