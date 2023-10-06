
import tempfile
import subprocess
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from threading import *
from pathlib import Path

# the main window for display
class Window(QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.grid = IndicSelectWindow()
        self.originalPalette = QApplication.palette()

        background = QComboBox()
        background.addItems(QStyleFactory.keys())

        # top menu bar for operations
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
        # self.custom_gate_tab = CustomGateTab(self)
        # button_custom_gate.triggered.connect(lambda: self.makeCustomGate())

        # intialize dwave tab for user input
        self.dwave_tab = DWaveTab(self)
        button_dwave.triggered.connect(self.showDWaveTab)
        # other menu bars

        button_demo = QAction("&Demo", self)
        menu.addAction(button_demo)
        button_demo.triggered.connect(self.activateDemo)

        button_exit = QAction("&Exit", self)
        menu.addAction(button_exit)
        # additional exit button (why not)
        button_exit.triggered.connect(lambda: self.closeEvent(parent))

        # file I/O actions
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
        save.triggered.connect(self.saveFile)
        load.triggered.connect(self.loadFile)
        email.triggered.connect(self.emailFile)
        undo.triggered.connect(self.undo)
        redo.triggered.connect(self.redo)

        # create simulation settings layout and running layout
        self.createSimulationSetting()
        self.createSimulationRunning()

        # right side toolbar to hold simulation settings
        setting = QToolBar()
        setting.addWidget(self.SimulationChoice)
        setting.addWidget(self.SimulationSetting)
        self.addToolBar(Qt.RightToolBarArea, setting)

        # display grid as central widget
        self.setCentralWidget(self.grid)

        # set fixed size for drag & drop precision
        self.setWindowTitle("Designer")
        self.changeStyle('fusion')

    def emailFile(self):
        designer.giveGUIGrid(grid)
        designer.runSimulation()
        designer.saveSimulationToFile("email.qc")
        address = QInputDialog.getText(
            self, 'Email Address', 'Email Address:')[0]
        subjectLine = QInputDialog.getText(self, 'Subject', 'Subject:')[0]
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
        path = QFileDialog.getSaveFileName(self, "Choose Directory", "E:\\")
        # print(path[0] + ".qc")
        designer.giveGUIGrid(grid)
        designer.runSimulation()
        designer.saveSimulationToFile(path[0] + ".qc")

    def loadFile(self):
        dir_path = QFileDialog.getOpenFileName(self, "Choose .qc file", "E:\\")
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

    # override close event to make sure pop-up window will close when
    # main window is close, otherwise a not-responding pop-up will remain
    # after main window is closed

    def closeEvent(self):
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

    # create interface for running simulation
    def createSimulationRunning(self):
        self.SimulationChoice = QGroupBox("Simulation Actions")
        button1 = QPushButton()
        button1.setText("Run")
        button1.clicked.connect(runSimulation)
        button2 = QPushButton()
        button2.setText("Data Diagram")
        button2.clicked.connect(dataDiagramVisualization)
        button3 = QPushButton()
        button3.setText("LL(1) Grid Parser")
        button3.clicked.connect(showParseGrid)
        button4 = QPushButton()
        button4.setText("Tensor Network Diagram")
        button4.clicked.connect(showTensorNetwork)
        layout = QVBoxLayout()
        layout.addWidget(button1)
        layout.addWidget(button2)
        layout.addWidget(button4)
        layout.addWidget(button3)
        layout.addStretch(1)
        self.SimulationChoice.setLayout(layout)

    # a function that changes setting file and backend based on user's choice
    def updateSimulationTechnique(self):
        if ("H" in self.sim_box.currentText() and "u" not in self.sim_box.currentText()):
            changeSimulationTechniqueHamiltonian()
        elif ("H" in self.sim_box.currentText()):
            changeSimulationTechniqueHamiltonianCuQuantum()
        elif ("F" in self.sim_box.currentText()):
            changeSimulationTechniqueFeynman()
        elif ("D" in self.sim_box.currentText()):
            if self.external_sim_msg.msg_toggle:
                self.external_sim_msg.exec()
            changeSimulationTechniqueDWave()
        elif ("Q" in self.sim_box.currentText()):
            if self.external_sim_msg.msg_toggle:
                self.external_sim_msg.exec()
            changeSimulationTechniqueQiskit()
        elif ("X" in self.sim_box.currentText()):
            if self.external_sim_msg.msg_toggle:
                self.external_sim_msg.exec()
            changeSimulationTechniqueXanadu()
        else:
            if self.external_sim_msg.msg_toggle:
                self.external_sim_msg.exec()
            changeSimulationTechniqueIBM()

    # a function that allows user to set external backend warning msg off
    def externalMsgToggle(self, pushed):
        if (pushed.text() == "Ignore"):
            self.external_sim_msg.msg_toggle = False

    # create interface for simulation settings
    def createSimulationSetting(self):
        self.SimulationSetting = QGroupBox("Simulation Setting")

        layout = QVBoxLayout()
        # check box for measurement, setting will be updated once toggled
        measurement = QCheckBox("Measurement")
        measurement.toggled.connect(self.TypeOnClicked)
        measurement.callsign = "measurement"
        layout.addWidget(measurement)

        # check box for gate suggestion, setting will be updated once toggled
        gate_suggestion = QCheckBox("Gate Sugguestion")
        gate_suggestion.toggled.connect(self.TypeOnClicked)
        gate_suggestion.callsign = "suggestion"
        layout.addWidget(gate_suggestion)

        # check box for incremental saving, setting will be updated once toggled
        incremental_saving = QCheckBox("Incremental Saving")
        incremental_saving.toggled.connect(self.TypeOnClicked)
        layout.addWidget(incremental_saving)
        incremental_saving.callsign = "incresav"

        # check box for incremental simulation, setting will be updated once toggled
        incremental_simulation = QCheckBox("Incremental Simulation")
        incremental_simulation.toggled.connect(self.TypeOnClicked)
        layout.addWidget(incremental_simulation)
        incremental_simulation.callsign = "incresim"

        # check box for photonic mode, setting will be updated once toggled
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

        # a message box that tells user external backend has been selected
        # 'ignore' button has been overriden so that
        # click on it will let message never pop-up again
        self.external_sim_msg = QMessageBox()
        self.external_sim_msg.setIcon(QMessageBox.Information)
        self.external_sim_msg.setWindowTitle("External backend")
        self.external_sim_msg.setStandardButtons(
            QMessageBox.Ok | QMessageBox.Ignore)
        # message on display
        self.external_sim_msg.setText(
            "You have chosen an external backend. QCD will now run your circuit design on an external backend.")
        self.external_sim_msg.setInformativeText(
            "Some external backend have different behaviors when accepting input. You can access their features via the menu bar. ")
        self.external_sim_msg.msg_toggle = True
        self.external_sim_msg.buttonClicked.connect(self.externalMsgToggle)

        # Simulation selection panel
        Simulation = QLabel("Simulation Technique")
        sim_selection = ["Hamiltionian", "Hamiltonian CuQuantum",
                         "Feynman", "DWave Ocean", "Qiskit", "Xanadu"]
        self.sim_box = QComboBox()
        self.sim_box.addItems(sim_selection)
        self.sim_box.currentIndexChanged.connect(
            self.updateSimulationTechnique)

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

    # integration function that connects checkboxs on gui to backend
    def TypeOnClicked(self):
        global grid
        global photonicMode
        global offSetHorizontal

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
            photonicMode = not photonicMode
            offSetHorizontal = 5
            grid = [["-" for i in range(currentWidth + offSetHorizontal)]
                    for j in range(currentHeight)]
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
        x1 = QInputDialog.getInt(self, 'X1', 'Input:')
        if (x1[1]):
            print(x1[0])
            x2 = QInputDialog.getInt(self, 'X2', 'Input:')
            if (x2[1]):
                print(x2[0])
                y1 = QInputDialog.getInt(self, 'Y1', 'Input:')
                if (y1[1]):
                    print(y1[0])
                    y2 = QInputDialog.getInt(self, 'Y2', 'Input:')
                    if (y2[1]):
                        print(y2[0])
        
        print(grid[y1[0]][x1[0] + offSetHorizontal])
        print(grid[y2[0]][x2[0] + offSetHorizontal])

        customGrid = [["-" for i in range(x2[0]-x1[0]+1)]
                      for j in range(y2[0]-y1[0]+1)]

        for i in range(y1[0], y2[0] + 1):
            for j in range(x1[0], x2[0] + 1):
                customGrid[i-y1[0]][j-x1[0]] = grid[i][j+offSetHorizontal]

        customGateName = QInputDialog.getText(self, 'Custom Gate Name', 'Input:')
        print(customGateName)
        if (customGateName[1] == False):
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

    # let Dwave input tab show when user clicks on toolbar
    def showDWaveTab(self):
        self.dwave_tab.show()

    # When the button is clicked, QuantumVQEDemo.py will be run.
    def activateDemo(self):
        try:
            subprocess.Popen(['python3', 'QuantumVQEDemo.py'])
        except Exception as e:
            print(f'Cannot open QuantumVQEDemo.py: {e}')