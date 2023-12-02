# Designer File
from pydoc import visiblename
import numpy as np
import GateFile
import SettingsFile
import SimulationFile
import copy
import pickle
import SettingsFile
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.cm as cm
import matplotlib as mpl


class Designer:
    # Store necessary field elements
    numSinceLastShown = 100
    gridHeight = -1
    gridWidth = -1
    grid = []
    tempGrid = []
    settings = SettingsFile.Settings()
    result = None
    resultingHistogram = None

    # Cursed as it is, this uses the Singleton design pattern to ensure duplicate gate objects are not create,
    # instead one stores the positions and identifying string
    visible_gates = {'H': GateFile.GateFactory("Individual", 'H', np.array([[1/np.sqrt(2) + 0.0j, 1/np.sqrt(2) + 0.0j], [1/np.sqrt(2) + 0.0j, -1/np.sqrt(2) + 0.0j]]), [-1]),
                     '-': GateFile.GateFactory("Individual", '-', np.array([[1.0+0.0j, 0.0+0.0j], [0.0+0.0j, 1.0+0.0j]]), [-1]),
                     'CNOT': GateFile.GateFactory("Multiple", 'CNOT', np.array([[1 + 0.0j, 0 + 0.0j, 0 + 0.0j, 0 + 0.0j], [0 + 0.0j, 1 + 0.0j, 0 + 0.0j, 0 + 0.0j], [0 + 0.0j, 0 + 0.0j, 0 + 0.0j, 1 + 0.0j], [0 + 0.0j, 0 + 0.0j, 1 + 0.0j, 0 + 0.0j]]), [-2, -1]),
                     'CNOTR': GateFile.GateFactory("Multiple", 'CNOT', np.array([[1 + 0.0j, 0 + 0.0j, 0 + 0.0j, 0 + 0.0j], [0 + 0.0j, 0 + 0.0j, 0 + 0.0j, 1 + 0.0j], [0 + 0.0j, 0 + 0.0j, 1 + 0.0j, 0 + 0.0j], [0 + 0.0j, 1 + 0.0j, 1 + 0.0j, 0 + 0.0j]]), [-2, -1]),
                     'X': GateFile.GateFactory("Individual", 'X', np.array([[0 + 0.0j, 1 + 0.0j], [1 + 0.0j, 0 + 0.0j]]), [-1]),
                     'Y': GateFile.GateFactory("Individual", 'Y', np.array([[0 + 0.0j, 0-1j], [0+1j, 0 + 0.0j]]), [-1]),
                     'Z': GateFile.GateFactory("Individual", 'Z', np.array([[1 + 0.0j, 0 + 0.0j], [0 + 0.0j, -1 + 0.0j]]), [-1]),
                     'S': GateFile.GateFactory("Individual", 'S', np.array([[1 + 0.0j, 0 + 0.0j], [0 + 0.0j, 0+1j]]), [-1]),
                     'T': GateFile.GateFactory("Individual", 'T', np.array([[1 + 0.0j, 0 + 0.0j], [0 + 0.0j, 0+np.exp(1j*np.pi/4)]]), [-1]),
                     'PD': GateFile.GateFactory("Individual", 'PD', np.array([0]), [-1]),
                     'PX': GateFile.GateFactory("Individual", 'PX', np.array([0]), [-1]),
                     'PZ': GateFile.GateFactory("Individual", 'PZ', np.array([0]), [-1]),
                     'PS': GateFile.GateFactory("Individual", 'PS', np.array([0]), [-1]),
                     'PV': GateFile.GateFactory("Individual", 'PV', np.array([0]), [-1]),
                     'PF': GateFile.GateFactory("Individual", 'PF', np.array([0]), [-1]),
                     'PBS': GateFile.GateFactory("Multiple", 'PBS', np.array([0]), [-2, -1]),
                     'PMZ': GateFile.GateFactory("Multiple", 'PMZ', np.array([0]), [-2, -1]),
                     'PS2': GateFile.GateFactory("Multiple", 'PS2', np.array([0]), [-2, -1]),
                     'PCX': GateFile.GateFactory("Multiple", 'PCX', np.array([0]), [-2, -1]),
                     'PCZ': GateFile.GateFactory("Multiple", 'PCZ', np.array([0]), [-2, -1]),
                     'PCK': GateFile.GateFactory("Multiple", 'PCK', np.array([0]), [-2, -1]),
                     'PPV': GateFile.GateFactory("Individual", 'PPV', np.array([0]), [-1]),
                     'PPC': GateFile.GateFactory("Individual", 'PPC', np.array([0]), [-1]),
                     'PPF': GateFile.GateFactory("Individual", 'PPF', np.array([0]), [-1])}

    # initalize field elements based on input
    def __init__(self, newGridHeight=5, newGridWidth=8):
        self.gridHeight = newGridHeight
        self.gridWidth = newGridWidth
        for _ in range(self.gridWidth):
            tempArray = []
            for _ in range(self.gridHeight):
                tempArray.append(self.visible_gates['-'])
            self.grid.append(tempArray)

    # Getters for field information
    def giveGUIGrid(self, GUI):
        self.tempGrid = GUI

    def getGUIGrid(self):
        return self.tempGrid

    # Takes given position on GUI grid and updates Designer's grid [ONLY deal with user-ediable portion]
    def gateAddition(self, name, posX, posY):
        if(name not in self.visible_gates):
            print("ERROR: Trying to add gate")
        # Make a copy of grid
        self.grid[posX][posY] = copy.deepcopy(self.visible_gates[name])
        # Change location
        self.grid[posX][posY].setPoint([posX, posY])
        tempQubits = []
        # Get involved qubits
        qubits = self.grid[posX][posY].gate_qubitsInvolved
        # Find the values of such qubits
        for i in range(len(qubits)):
            tempQubits.append(posY + i)
        self.grid[posX][posY].setInvolvedQubits(tempQubits)
        self.printDesign()
        if(self.numSinceLastShown >= 10 and self.settings.gate_suggestion == True): # If gate suggestions are on
            self.numSinceLastShown = 0
            self.suggestSimplifications(self.grid) # Suggest suggestions if number of moves exceeds requirement
        self.numSinceLastShown += 1

    # Replaces gate with empty gate
    def gateRemoval(self, posX, posY):
        self.grid[posX][posY] = self.visible_gates['-']

    def printDesign(self):  # For debugging purposes
        circuitOperators = [
            [['-', [j]] for j in range(self.gridHeight)] for i in range(self.gridWidth)]
        for widthIdx in range(self.gridWidth):
            for heightIdx in range(self.gridHeight):
                if(self.grid[widthIdx][heightIdx].getName() != '-'):
                    if(len(self.grid[widthIdx][heightIdx].getName()) >= 3 and "PP" not in self.grid[widthIdx][heightIdx].getName()):
                        circuitOperators[widthIdx][heightIdx] = [self.grid[widthIdx][heightIdx].getName(
                        ), self.grid[widthIdx][heightIdx].gate_qubitsInvolved]
                        circuitOperators[widthIdx][heightIdx+1] = [self.grid[widthIdx]
                                                                   [heightIdx].getName(), self.grid[widthIdx][heightIdx].gate_qubitsInvolved]
                    else:
                        circuitOperators[widthIdx][heightIdx] = [self.grid[widthIdx][heightIdx].getName(
                        ), self.grid[widthIdx][heightIdx].gate_qubitsInvolved]
        print("Quantum Circuit Printout:")
        numDepth = self.gridWidth
        numQubits = self.gridHeight
        entry = ""
        for depth in range(3*(numDepth+1)):
            entry += "-"
        print(entry)
        for qubit in range(numQubits):
            tempStr = ""
            for depth in range(numDepth):
                if(len(circuitOperators[depth][qubit][0]) >= 3 and "PP" not in self.grid[widthIdx][heightIdx].getName()):
                    if(qubit == circuitOperators[depth][qubit][1][0]):
                        tempStr += " [*] "
                    else:
                        tempStr += " [x] "
                else:
                    tempStr += "[" + circuitOperators[depth][qubit][0] + "]"
            tempStr += " [M] "
            print(tempStr)
        print(entry)


    """ 
    TODO:
        Fix this bug. The backend needs to constantly updated. 
    """
    def update(self, show):
        simulation = SimulationFile.Simulation(self.settings)
        simulation.sendStateInfo(self.gridWidth, self.gridHeight, self.grid)
        self.result = simulation.get_results(show=show)
        self.resultingHistogram = simulation.get_visualization()
    
    # Specify simulation settings, send grid information, run simulation, and get results
    def runSimulation(self):
        print(self.settings.specialGridSettings)
        self.update(show=True)

    # Return back found result histogram
    def getVisualization(self):
        return self.resultingHistogram

    # Return back found result
    def getStatistics(self):
        self.update(show=False)
        return self.result

    # Allows one to set the backend being used
    def setBackend(self, name):
        self.settings.backend = name

    # Saves field elements to file including GUI grid for state recovery
    def saveSimulationToFile(self, filename="quantumCircuitLatest.qc"):
        self.printDesign()
        fileFormat = {"results": self.result,
                      "gate_set": self.visible_gates, "gridWidth": self.gridWidth, "gridHeight": self.gridHeight,
                      "grid": self.grid, "settings": self.settings, "GUIGrid": self.tempGrid}
        with open(filename, 'wb') as fileSave:
            pickle.dump(fileFormat, fileSave)

    # Load field elements from file and reconstruct matplotlib figure from data, simulation dependent
    def loadSimulationFromFile(self, filename="quantumCircuitLatest.qc"):
        with open(filename, 'rb') as fileSave:
            fileFormat = pickle.load(fileSave)
            print(fileFormat)
            grid = fileFormat["grid"]
            self.result = fileFormat["results"]
            self.settings = fileFormat["settings"]
            hasResults = False
            try:
                print(self.results)
                hasResults = True
            except:
                pass
            if(hasResults and self.settings.backend == "HamiltonianSimulation"):
                results = self.result
                fig = plt.figure(figsize=(20, 5))
                xVal = []
                yVal = []
                norm = mpl.colors.Normalize(vmin=0, vmax=np.pi)
                cmap = cm.hsv
                m = cm.ScalarMappable(norm=norm, cmap=cmap)
                for entry in results:
                    xVal.append(entry[0][::-1])
                    yVal.append(entry[1]*100)
                phases = [m.to_rgba(np.angle(results[j][2] * 1j)) for j in range(len(results))]

                df = pd.DataFrame(
                    dict(
                        x=xVal,
                        y=yVal,
                        phase=phases
                    )
                )
                df_sorted = df.sort_values('x')
                plt.bar(df_sorted['x'], df_sorted['y'],
                        width=0.4, color=df_sorted['phase'])
                plt.xlabel("Computational Result")
                plt.ylabel("Probability")
                rotationAmount = math.floor(90/(1 + np.exp(-(((len(xVal))/3)-5))))
                plt.xticks(rotation=rotationAmount)
                cbar = plt.colorbar(m)
                cbar.set_label('Relative Phase of State (Radians)',
                           rotation=-90, labelpad=20)
                plt.title("Probability Distribution of Given Quantum Circuit")
                self.resultingHistogram = plt
            if(hasResults and self.settings.backend == "FeynmanSimulation"):
                fig = plt.figure(figsize = (20, 5))
                xVal = []
                yVal = []
                total = 0
                for _, y in self.results.items():
                    total += y
                for a, b in self.results.items():
                    xVal.append(a)
                    yVal.append((b / total) * 100)

                df = pd.DataFrame(
                    dict(
                        x=xVal,
                        y=yVal
                    )
                )

                df_sorted = df.sort_values('x')
                plt.bar(df_sorted['x'], df_sorted['y'], width = 0.4)
                plt.xlabel("Computational Result")
                plt.ylabel("Probability")
                rotationAmount = math.floor(90/(1 + np.exp(-(((len(xVal))/3)-5))))
                plt.xticks(rotation = rotationAmount)
                plt.title("Probability Distribution of Given Quantum Circuit")
                self.histogramResult = plt
            if(hasResults and self.settings.backend == "DWaveSimulation"):
                valuesFound = []
                for energy, in self.results.data(fields=['energy']):
                    valuesFound.append(energy)
                fig = plt.figure(figsize = (20, 5))
                plt.hist(valuesFound)
                plt.xlabel("Minimum Energy of Solutions")
                plt.ylabel("Amount of Occurences")
                self.histogramResult = plt
            self.visible_gates = fileFormat["gate_set"]
            self.gridWidth = fileFormat["gridWidth"]
            self.gridHeight = fileFormat["gridHeight"]
            self.tempGrid = fileFormat["GUIGrid"]

    # Various getters and setters
    def setObjective(self, string):
        self.settings.objectiveQUBOS = string
    
    def addVariable(self, string):
        self.settings.variableDeclarationsQUBO.append(string)
    
    def addConstraint(self, string):
        self.settings.constraintsQUBO.append(string)
        
    def addBitstring(self, string):
        self.settings.bitstringsSample.append(string)

    # Run qiskit transpilation to get gate suggestions
    def suggestSimplifications(self, grid):
        starredPositions = {(-1,-1)}
        from qiskit import QuantumCircuit
        from qiskit import Aer, transpile
        circuit = QuantumCircuit(self.gridHeight)
        for qubit in range(len(grid)):
            for depth in range(3, len(grid[qubit])):
                if(grid[qubit][depth] != '-'):
                    if(grid[qubit][depth] == 'H'):
                        circuit.h(qubit)
                    if(grid[qubit][depth] == 'X'):
                        circuit.x(qubit)
                    if(grid[qubit][depth] == 'Y'):
                        circuit.y(qubit)
                    if(grid[qubit][depth] == 'Z'):
                        circuit.z(qubit)
                    if(grid[qubit][depth] == 'S'):
                        circuit.s(qubit)
                    if(grid[qubit][depth] == 'T'):
                        circuit.t(qubit)
                    if(grid[qubit][depth] == 'CNOT'):
                        circuit.cnot(qubit, qubit + 1)
                        qubit += 1
        circuit.measure_all()
        print(circuit)
        backend = Aer.get_backend('statevector_simulator')
        from qiskit import transpile
        couplingMapping = [] # Currently, only nearest-neighbor topology, so specify it (dependents on qubit number)
        for qubitIdx in range(self.gridHeight - 1):
            couplingMapping.append([qubitIdx, qubitIdx + 1])
        # Save transpilation result
        simplified = transpile(circuit, backend=backend, coupling_map=couplingMapping, optimization_level=3)
        simplified.draw(output='mpl', filename='../assets/simplified.png') 
        # Plot result
        import matplotlib.image as mpimg
        img = mpimg.imread('../assets/simplified.png')
        imgplot = plt.imshow(img)
        plt.show()
