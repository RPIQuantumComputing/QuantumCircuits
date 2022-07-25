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

ignoreX = 4
gateToImage = {" ": Image.open("../assets/EMPTY.png"), "-": Image.open("../assets/GATE.png"), "H": Image.open("../assets/H.png"), 
                "T": Image.open("../assets/T.png"), "S": Image.open("../assets/S.png"), "X": Image.open("../assets/X.png"), "Y": Image.open("../assets/Y.png"),
                "Z": Image.open("../assets/Z.png"), "CNOT": Image.open("../assets/CNOT.png")}
currentWidth = 8
currentHeight = 5
offSetHorizontal = 3
grid = [["-" for i in range(currentWidth + 3)] for j in range(currentHeight)]

hamiltonian = False
import DesignerFile
designer = DesignerFile.Designer()

needToUpdate = False
photonicMode = False

DWaveVar = ""
DWaveCon = ""
DwaveObjective = ""

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
    else:
        # Kandan, add all the new gates here to the GUI
        pass
    return " "


def runSimulation():
    print("---------------------Running Simulation-------------------------------------")
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

    #other simulation technique
    else:
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
            for depth in range(3, numDepth):
                if((qubit, depth) in starredPositions):
                    tempStr += "[*]"
                else:
                    designer.gateAddition(grid[qubit][depth], depth-3, qubit)
                    tempStr += "[" + grid[qubit][depth] + "]"
                if(len(grid[qubit][depth]) >= 3 and "PP" not in grid[qubit][depth]):
                    starredPositions.add((qubit + 1, depth))
                tempStr += "[M]"
            print(tempStr)
        print(entry)
        print("------------------------BACKEND GOT-------------------------------------")
        designer.printDesign()
        designer.runSimulation()
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
    print("Set number of qubits to " + str(val))

def updateGrid():
    global grid
    global needToUpdate
    grid = designer.getGUIGrid()
    needToUpdate = True    

def updateNumWidth(val):
    designer.settings.num_width = val
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
        new = QAction("&New", self)
        save = QAction("&Save", self)
        load = QAction("&Load", self)
        file_menu.addAction(new)
        file_menu.addAction(save)
        file_menu.addAction(load)
        save.triggered.connect(lambda: self.saveFile())
        load.triggered.connect(lambda: self.loadFile())

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
        self.setFixedSize(1920, 960)
        self.setWindowTitle("Designer")
        self.changeStyle('fusion')

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


    #override close event to make sure pop-up window will close when
    #main window is close, otherwise a not-responding pop-up will remain
    #after main window is closed
    def closeEvent(self, event):
        if (self.dwave_tab):
            self.dwave_tab.close()           
        self.close()

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

        Simulation = QLabel("Simulation Technique")
        sim_selection = ["Hamiltionian", "Feynman", "DWave Ocean", "Qiskit", "IBM Xanadu"]
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
            print("Update to Photonic Mode...")
            global photonicMode
            photonicMode = not photonicMode
            global needToUpdate 
            needToUpdate = True

    def UpdateParameters(self):
        spin = self.sender()
        val = spin.value()
        if (spin.callsign == "numqubit"):
            updateNumQubit(val)
        elif (spin.callsign == "numwidth"):
            updateNumWidth(val)

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

        #add to layout
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


        skipThis = [-1, -1]
        for j in range(1, 4):
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
                if(j == 3):
                    self.Frame.setStyleSheet("background-color: grey;")
                    Box = QVBoxLayout()
                    Box.addWidget(self.Frame)
                    self.gridLayout.addLayout(Box, i, j - 1, 3, 1)
                else:
                    grid[i][j - 1] = inital(i, j - 1)
                    self.ax.imshow(gateToImage[grid[i][j - 1]])
                    self.ax.set_axis_off()
                    self.canvas.draw()  # refresh canvas
                    self.layout.addWidget(self.canvas)
                    self.canvas.installEventFilter(self)
                    Box = QVBoxLayout()
                    Box.addWidget(self.Frame)
                    self.gridLayout.addLayout(Box, i, j - 1)
        for i in range(3, currentWidth + 3):
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

    def eventFilter(self, watched, event):
        if event.type() == QEvent.MouseButtonPress:
            self.mousePressEvent(event)
        elif event.type() == QEvent.MouseMove:
            self.mouseMoveEvent(event)
        elif event.type() == QEvent.MouseButtonRelease:
            self.mouseReleaseEvent(event)
        return super().eventFilter(watched, event)

    def get_index(self, pos):
        for i in range(self.gridLayout.count()):
            if self.gridLayout.itemAt(i).geometry().contains(pos) and i != self.target:
                return i

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
        if needToUpdate:
            print("Updating....")
            needToUpdate = False
            skipThis = [-1, -1]
            for i in range(3, currentWidth + 3):
                for j in range(currentHeight):
                    self.Frame = QFrame(self)
                    self.Frame.setStyleSheet("background-color: white;")
                    self.Frame.setLineWidth(0)
                    self.layout = QHBoxLayout(self.Frame)

                    self.figure = Figure()  # a figure to plot on
                    self.canvas = FigureCanvas(self.figure)
                    self.ax = self.figure.add_subplot(111)  # create an axis
                    self.ax.imshow(gateToImage[grid[j][i]])
                    self.ax.set_axis_off()
                    self.canvas.draw()  # refresh canvas
                    self.canvas.installEventFilter(self)

                    self.layout.addWidget(self.canvas)

                    Box = QVBoxLayout()

                    Box.addWidget(self.Frame)
                    self.gridLayout.removeItem(self.gridLayout.itemAtPosition(j, i))
                    self.gridLayout.addLayout(Box, j, i)


    def mouseReleaseEvent(self, event):
        self.target = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if not event.source().geometry().contains(event.pos()):
            source = self.get_index(event.pos())
            if source is None:
                return

            i, j = max(self.target, source), min(self.target, source)
            row, col, _, _ = self.gridLayout.getItemPosition(self.target)
            row2, col2, _, _ = self.gridLayout.getItemPosition(source)
            p1, p2 = self.gridLayout.getItemPosition(self.target), self.gridLayout.getItemPosition(source)
            #self.gridLayout.addItem(self.gridLayout.takeAt(i), *p2)
            #self.gridLayout.addItem(self.gridLayout.takeAt(j), *p1)
            #self.gridLayout.takeAt(self.target)
            #self.gridLayout.takeAt(source)
            if(self.gridLayout.getItemPosition(self.target)[1] < 3):
                self.Frame = QFrame(self)
                self.Frame.setStyleSheet("background-color: white;")
                self.Frame.setLineWidth(0)
                self.layout = QHBoxLayout(self.Frame)
                self.figure = Figure()  # a figure to plot on
                self.canvas = FigureCanvas(self.figure)
                self.ax = self.figure.add_subplot(111)  # create an axis
                self.ax.imshow(gateToImage[inital(row, col)])
                self.ax.set_axis_off()
                self.canvas.draw()  # refresh canvas
                self.canvas.installEventFilter(self)
                self.layout.addWidget(self.canvas)
                Box = QVBoxLayout()
                Box.addWidget(self.Frame)
                self.gridLayout.takeAt(source)
                self.gridLayout.addLayout(Box, row2, col2)
                grid[row2][col2] = grid[row][col]
            else:
                self.gridLayout.addItem(self.gridLayout.takeAt(self.target), *p2)
                self.gridLayout.addItem(self.gridLayout.takeAt(source), *p1)
                grid[row][col], grid[row2][col2] = grid[row2][col2], grid[row][col]

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
                for depth in range(3, numDepth):
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
        for i in range(currentWidth): #height
            for j in range(currentHeight): #width
                self.figure = Figure()  # a figure to plot on
                self.canvas = FigureCanvas(self.figure)
                self.ax = self.figure.add_subplot(111)  # create an axis
                self.ax.imshow(gateToImage[grid[j][i]])
                self.ax.set_axis_off()
                self.canvas.draw()  # refresh canvas
                self.canvas.installEventFilter(self)
                self.layout.addWidget(self.canvas)
                Box = QVBoxLayout()
                Box.addWidget(self.Frame)
                self.gridLayout.addLayout(Box, i, j)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_()) 