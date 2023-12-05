import DesignerFile
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PIL import Image
from threading import *
from redmail import EmailSender

class GraphicsManager:
    def __init__(self):
        self.gateToImage = {" ": Image.open("../assets/EMPTY.png"), "-": Image.open("../assets/GATE.png"), "H": Image.open("../assets/H.png"),
               "T": Image.open("../assets/T.png"), "S": Image.open("../assets/S.png"), "X": Image.open("../assets/X.png"), "Y": Image.open("../assets/Y.png"),
               "Z": Image.open("../assets/Z.png"), "CNOT": Image.open("../assets/CNOT.png"),
               "PBS": Image.open("../assets/PBS.png"), "PCK": Image.open("../assets/PCK.png"), "PCX": Image.open("../assets/PCX.png"),
               "PCZ": Image.open("../assets/PCZ.png"), "PD": Image.open("../assets/PD.png"), "PF": Image.open("../assets/PF.png"),
               "PMZ": Image.open("../assets/PMZ.png"), "PPC": Image.open("../assets/PPC.png"), "PPF": Image.open("../assets/PPF.png"),
               "PPV": Image.open("../assets/PPV.png"), "PS": Image.open("../assets/PS.png"), "PS2": Image.open("../assets/PS2.png"),
               "PV": Image.open("../assets/PV.png"), "PX": Image.open("../assets/PX.png"), "PZ": Image.open("../assets/PZ.png")}
        self.currentWidth = 8
        self.currentHeight = 6
        self.offSetHorizontal = 3
        self.hamiltonian = False

class GridManager:
    def __init__(self, GM: GraphicsManager):
        self.grid = [["-" for i in range(GM.currentWidth + GM.offSetHorizontal)] for j in range(GM.currentHeight)]
        self.priorBarrier = [-1, -1, -1, -1]
        self.designer = DesignerFile.Designer(GM.currentHeight, GM.currentWidth)

class GateManager:
    def __init__(self):
        self.customGates = {}
        self.positionsWithCustomGates = {(-1, -1): "NA"}
        self.undoStack = []
        self.redoStack = []

class SimulatorSettings:
    def __init__(self):
        self.needToUpdate = False
        self.photonicMode = False
        self.DWaveVar = ""
        self.DWaveCon = ""
        self.DwaveObjective = ""
        #self.cuQuantumTab = PartialSimulationTab()
        self.cuQuantumBitStrings = []
        self.cuQuantumGateSplit = 0
        self.cuQuantumConfig = [0, 1, 2, 3]

class EmailManager:
    def __init__(self, host, port, username, password):
        self.gmail = EmailSender(host=host, port=port, username=username, password=password)