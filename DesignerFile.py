# Designer File
from pydoc import visiblename
import numpy as np
import GateFile
import SettingsFile
import SimulationFile
import copy

class Designer:
    gridHeight = -1
    gridWidth = -1
    grid = []
    settings = SettingsFile.Settings()
    result = None
    resultingHistgram = None
    visible_gates = {'H': GateFile.GateFactory("Individual", 'H', np.array([[1/np.sqrt(2) + 0.0j, 1/np.sqrt(2) + 0.0j], [1/np.sqrt(2) + 0.0j, -1/np.sqrt(2) + 0.0j]]),[-1]),
                     '-': GateFile.GateFactory("Individual", '-', np.array([[1.0+0.0j, 0.0+0.0j], [0.0+0.0j,1.0+0.0j]]), [-1]),
                    'CNOT': GateFile.GateFactory("Multiple", 'CNOT', np.array([[1+ 0.0j,0+ 0.0j,0+ 0.0j,0+ 0.0j],[0+ 0.0j,1+ 0.0j,0+ 0.0j,0+ 0.0j],[0+ 0.0j,0+ 0.0j,0+ 0.0j,1+ 0.0j],[0+ 0.0j,0+ 0.0j,1+ 0.0j,0+ 0.0j]]), [-2, -1]),
                    'CNOTR': GateFile.GateFactory("Multiple", 'CNOT', np.array([[1+ 0.0j,0+ 0.0j,0+ 0.0j,0+ 0.0j],[0+ 0.0j,0+ 0.0j,0+ 0.0j,1+ 0.0j],[0+ 0.0j,0+ 0.0j,1+ 0.0j,0+ 0.0j],[0+ 0.0j,1+ 0.0j,1+ 0.0j,0+ 0.0j]]), [-2, -1]),
                    'X': GateFile.GateFactory("Individual", 'X', np.array([[0 + 0.0j, 1+ 0.0j],[1+ 0.0j,0+ 0.0j]]),[-1]), 
                    'Y': GateFile.GateFactory("Individual", 'Y', np.array([[0+ 0.0j, 0-1j],[0+1j, 0+ 0.0j]]), [-1]),
                    'Z': GateFile.GateFactory("Individual", 'Z', np.array([[1+ 0.0j, 0+ 0.0j],[0+ 0.0j,-1+ 0.0j]]), [-1]), 
                    'S': GateFile.GateFactory("Individual", 'S', np.array([[1+ 0.0j,0+ 0.0j],[0+ 0.0j,0+1j]]), [-1]), 
                    'T': GateFile.GateFactory("Individual", 'T', np.array([[1+ 0.0j,0+ 0.0j],[0+ 0.0j,0+np.exp(1j*np.pi/4)]]),[-1])}
    
    def __init__(self, newGridHeight=5, newGridWidth=8):
        self.gridHeight = newGridHeight
        self.gridWidth = newGridWidth
        for _ in range(self.gridWidth):
            tempArray = []
            for _ in range(self.gridHeight):
                tempArray.append(self.visible_gates['-'])
            self.grid.append(tempArray)

    def gateAddition(self, name, posX, posY):
        if(name not in self.visible_gates):
            print("ERROR: Trying to add gate")
        self.grid[posX][posY] = copy.deepcopy(self.visible_gates[name])
        self.grid[posX][posY].setPoint([posX, posY])
        tempQubits = []
        qubits = self.grid[posX][posY].gate_qubitsInvolved
        for i in range(len(qubits)):
            tempQubits.append(posY + i)
        self.grid[posX][posY].setInvolvedQubits(tempQubits)

    def gateRemoval(self, posX, posY):
        self.grid[posX][posY] = self.visible_gates['-']

    def printDesign(self): # For debugging purposes
        circuitOperators = [[['-', [j]] for j in range(self.gridHeight)] for i in range(self.gridWidth)]
        for widthIdx in range(self.gridWidth):
            for heightIdx in range(self.gridHeight):
                if(self.grid[widthIdx][heightIdx].getName() != '-'):
                    if(self.grid[widthIdx][heightIdx].getName() == 'CNOT'):
                        circuitOperators[widthIdx][heightIdx] = [self.grid[widthIdx][heightIdx].getName(), self.grid[widthIdx][heightIdx].gate_qubitsInvolved]
                        circuitOperators[widthIdx][heightIdx+1] = [self.grid[widthIdx][heightIdx].getName(), self.grid[widthIdx][heightIdx].gate_qubitsInvolved]
                    else:
                        circuitOperators[widthIdx][heightIdx] = [self.grid[widthIdx][heightIdx].getName(), self.grid[widthIdx][heightIdx].gate_qubitsInvolved]
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
                if(circuitOperators[depth][qubit][0] == 'CNOT'):
                    if(qubit == circuitOperators[depth][qubit][1][0]):
                        tempStr += "[*]"
                    else:
                        tempStr += "[x]"
                else:
                    tempStr += "[" + circuitOperators[depth][qubit][0] + "]"
            tempStr += "[M]"
            print(tempStr)
        print(entry)
    
    def runSimulation(self):
        simulation = SimulationFile.Simulation(self.settings)
        simulation.sendStateInfo(self.gridWidth, self.gridHeight, self.grid)
        self.result = simulation.get_results()
        self.resultingHistgram = simulation.get_visualization()

    def getVisualization(self):
        return self.resultingHistgram
