import sys
import DesignerFile
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PIL import Image
from threading import *
from redmail import EmailSender

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
grid = [["-" for i in range(currentWidth + offSetHorizontal)]
        for j in range(currentHeight)]
priorBarrier = [-1, -1, -1, -1]

# Initialize Designer
designer = DesignerFile.Designer(currentHeight, currentWidth)

# Various graphics settings
hamiltonian = False
needToUpdate = False
photonicMode = False

# Specific global state for DWave Annealer
DWaveVar = ""
DWaveCon = ""
DwaveObjective = ""

# Specific global state for cuQuantum
cuQuantumBitStrings = []
cuQuantumGateSplit = 0
cuQuantumConfig = [0, 1, 2, 3]

gmail = EmailSender(
    host='smtp.office365.com',
    port=587,
    username="quantumcircuits@outlook.com",
    password="dylansheils0241"
)



# Create the application, window, and close application if asked
app = QApplication(sys.argv)
cuQuantumTab = PartialSimulationTab()
window = Window()
window.show()
sys.exit(app.exec_())
