import sys, random
from unittest import skip
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.figure import Figure
from PIL import Image
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

ignoreX = 4 # Always the same

gateToImage = {" ": Image.open("EMPTY.png"), "-": Image.open("GATE.png"), "H": Image.open("H.png"), 
				"T": Image.open("T.png"), "S": Image.open("S.png"), "X": Image.open("X.png"), "Y": Image.open("Y.png"),
				"Z": Image.open("Z.png"), "C": Image.open("CNOT.png")}
currentWidth = 8
currentHeight = 5
offSetHorizontal = 3
grid = [["-" for i in range(currentWidth + 3)] for j in range(currentHeight)]

hamiltonian = False
import DesignerFile
designer = DesignerFile.Designer()

def inital(row, col):
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
		return "C"
	return " "

def runSimulation(self):
	print("---------------------Running Simulation-------------------------------------")
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
				if(grid[qubit][depth] == 'C'):
					designer.gateAddition("CNOT", depth-3, qubit)
				else:
					designer.gateAddition(grid[qubit][depth], depth-3, qubit)
				tempStr += "[" + grid[qubit][depth] + "]"
			if(grid[qubit][depth] == 'C'):
				starredPositions.add((qubit + 1, depth))
			tempStr += "[M]"
		print(tempStr)
	print(entry)
	print("------------------------BACKEND GOT-------------------------------------")
	designer.printDesign()
	designer.runSimulation()
	plt = designer.getVisualization()
	plt.show()

def changeSimulationTechniqueHamiltonian():
	designer.settings.backend = "HamiltionSimulation"
def changeSimulationTechniqueFeynman():
	designer.settings.backend = "FeynmanSimulation"

class Window(QMainWindow):
	def __init__(self, parent=None):
		super(Window, self).__init__(parent)
		
		self.grid = IndicSelectWindow()
		self.originalPalette = QApplication.palette()

		background = QComboBox()
		background.addItems(QStyleFactory.keys())

		
		toolbar = QToolBar("TOOLBAR")
		toolbar.setIconSize(QSize(20, 20))
		
		button_file = QAction("&File", self)
		toolbar.addAction(button_file)
		
		button_class = QAction("&Class", self)
		toolbar.addAction(button_class)
		
		button_learn = QAction("&Learn", self)
		toolbar.addAction(button_learn)

		self.createSimulationChoice()
		self.createSimulationSetting()
		self.createSimulationRunning()

		toolbar.addWidget(background)
		
		self.addToolBar(toolbar)

		setting = QToolBar()
		setting.addWidget(self.SimulationChoice)
		setting.addWidget(self.SimulationSetting)
		
		self.addToolBar(Qt.BottomToolBarArea, setting)
		
		self.setCentralWidget(self.grid)
		
		self.setFixedSize(1920, 960)
		self.setWindowTitle("Designer")
		self.changeStyle('fusion')
	def changeStyle(self, styleName):
		QApplication.setStyle(QStyleFactory.create(styleName))
		self.changePalette()
		
	def changePalette(self):
		QApplication.setPalette(self.originalPalette)

	def createSimulationChoice(self):
		self.SimulationChoice = QGroupBox("Simulation Type")

		radioButton1 = QRadioButton("Hamiltonian")
		radioButton1.sim = "Hamiltonian"
		radioButton1.toggled.connect(self.TypeOnClicked)
		radioButton2 = QRadioButton("Feynman")
		radioButton2.sim = "Feynman"
		radioButton2.toggled.connect(self.TypeOnClicked)
		radioButton1.setChecked(True)
		
		layout = QVBoxLayout()
		layout.addWidget(radioButton1)
		layout.addWidget(radioButton2)
		layout.addStretch(1)
		self.SimulationChoice.setLayout(layout)


	def createSimulationRunning(self):
		self.SimulationChoice = QGroupBox("Running Simulation")
		button1 = QPushButton()
		button1.setText("Run")
		button1.clicked.connect(runSimulation)
		layout = QVBoxLayout()
		layout.addWidget(button1)
		layout.addStretch(1)
		self.SimulationChoice.setLayout(layout)

	def updateSimulationTechnique(self, i):
		if("H" in self.sim_box.currentText()):
			changeSimulationTechniqueHamiltonian()
		else:
			changeSimulationTechniqueFeynman()

	def createSimulationSetting(self):
		self.SimulationSetting = QGroupBox("Simulation Setting")
		
		layout = QVBoxLayout()
		measurement = QCheckBox("Measurement")
		layout.addWidget(measurement)
		gate_suggestion = QCheckBox("Gate Sugguestion")
		layout.addWidget(gate_suggestion)
		incremental_saving = QCheckBox("Incremental Saving")
		layout.addWidget(incremental_saving)
		incremental_simulation = QCheckBox("Incremental Simulation")
		layout.addWidget(incremental_simulation)
		
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
		qubit_label = QLabel("&Number of Qubits: ")
		qubit_label.setBuddy(num_qubits)

		num_width = QSpinBox(self.SimulationSetting)
		num_width.setValue(8)
		width_label = QLabel("&Width: ")

		localSimulation = QLabel("Local Simulation Technique")
		sim_selection = ["Hamiltionian", "Feynman"]
		self.sim_box = QComboBox()
		self.sim_box.currentIndexChanged.connect(self.updateSimulationTechnique)

		self.sim_box.addItems(sim_selection)
		layout.addWidget(localSimulation)
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
		
	def TypeOnClicked(self):
		radioButton = self.sender()

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
					grid[j][i] = " "
					break
				grid[i][j] = " "
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
			p1, p2 = self.gridLayout.getItemPosition(i), self.gridLayout.getItemPosition(j)
			self.gridLayout.addItem(self.gridLayout.takeAt(i), *p2)
			self.gridLayout.addItem(self.gridLayout.takeAt(j), *p1)
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
				self.gridLayout.addLayout(Box, row, col)
				grid[row2][col2] = grid[row][col]
			else:
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
					if(grid[qubit][depth] == 'C'):
						starredPositions.add((qubit + 1, depth))
				tempStr += "[M]"
				print(tempStr)
			print(entry)



if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = Window()
	window.show()
	w = IndicSelectWindow()
	w.show()
	sys.exit(app.exec_())