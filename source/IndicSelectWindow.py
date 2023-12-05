from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib.figure import Figure
from threading import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import tempfile

from DesignerGUI import GraphicsManager, GridManager, GateManager, SimulatorSettings
from GUIHelper import GUIHelper

# the main workbench of qcd, a grid that supports drag & drop
class IndicSelectWindow(QDialog):
    def __init__(self, 
            GraphM: GraphicsManager, 
            GridM: GridManager, 
            GateM: GateManager,
            SS: SimulatorSettings,
            parent=None
    ):
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
        self.GraphM = GraphM
        self.GridM = GridM
        self.GateM = GateM
        self.SS = SS

        # Go through the grid and initialize values
        # For multiqubit gates, skip initializing covered positions
        skipThis = [-1, -1]
        for j in range(1, GraphM.offSetHorizontal + 1):
            for i in range(GraphM.currentHeight):
                GridM.grid[i][j - 1] = " "
                if (skipThis[0] == i and skipThis[1] == j):
                    break

                self.Frame = QFrame(self)
                self.Frame.setStyleSheet("background-color: white;")
                self.Frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
                self.Frame.setLineWidth(0)
                self.layout = QHBoxLayout(self.Frame)
                self.figure = Figure()  # a figure to plot on
                self.canvas = FigureCanvas(self.figure)
                self.ax = self.figure.add_subplot(111)  # create an axis

                if (j == GraphM.offSetHorizontal):  # If we need to create the barrier
                    self.Frame.setStyleSheet("background-color: grey;")
                    Box = QVBoxLayout()
                    Box.addWidget(self.Frame)
                    self.gridLayout.addLayout(Box, i, j-1, len(GridM.grid)-2, 1)
                    GridM.priorBarrier = [i, j - 1, len(GridM.grid)-2, 1]
                else:  # If we are adding just a gate
                    # Find what gate if any should go in position
                    GridM.grid[i][j - 1] = GUIHelper.initial(GateM, SS, i, j - 1)
                    if (GridM.grid[i][j - 1] in GateM.customGates):
                        self.ax.text(0.5, 0.5, GridM.grid[i][j - 1], horizontalalignment='center',
                                     verticalalignment='center', transform=self.ax.transAxes)
                    else:
                        # Show the gate
                        self.ax.imshow(GraphM.gateToImage[GridM.grid[i][j - 1]])
                    self.ax.set_axis_off()
                    self.canvas.draw()  # refresh canvas
                    self.layout.addWidget(self.canvas)
                    self.canvas.installEventFilter(self)
                    Box = QVBoxLayout()
                    Box.addWidget(self.Frame)
                    self.gridLayout.addLayout(Box, i, j - 1)

        # Go through and initialize field user interacts with
        for i in range(GraphM.offSetHorizontal, GraphM.currentWidth + GraphM.offSetHorizontal):
            for j in range(GraphM.currentHeight):
                GridM.grid[j][i] = "-"
                self.Frame = QFrame(self)
                self.Frame.setStyleSheet("background-color: white;")
                self.Frame.setLineWidth(0)
                self.layout = QHBoxLayout(self.Frame)

                self.figure = Figure()  # a figure to plot on
                self.canvas = FigureCanvas(self.figure)
                self.ax = self.figure.add_subplot(111)  # create an axis
                self.ax.imshow(GraphM.gateToImage["-"])
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
            row, col, _, _ = self.gridLayout.getItemPosition(
                self.get_index(event.windowPos().toPoint()))
            self.ax.imshow(self.GridM.grid[row][col])
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
        # If we need to update the grid, update all positions to have GUI be consistent with Grid 2D array
        if self.SS.needToUpdate:
            print("Updating....")
            self.SS.needToUpdate = False
            skip = {(-1, -1)}
            for i in range(self.GraphM.offSetHorizontal, self.GraphM.currentWidth + self.GraphM.offSetHorizontal):
                for j in range(self.GraphM.currentHeight):
                    self.Frame = QFrame(self)
                    self.Frame.setStyleSheet("background-color: white;")
                    self.Frame.setLineWidth(0)
                    self.layout = QHBoxLayout(self.Frame)

                    self.figure = Figure()  # a figure to plot on
                    self.canvas = FigureCanvas(self.figure)
                    self.ax = self.figure.add_subplot(111)  # create an axis
                    if ((j, i) not in self.GateM.positionsWithCustomGates and (j, i) not in skip):
                        if (self.GateM.grid[j][i] not in self.GateM.customGates):
                            self.ax.imshow(self.GraphM.gateToImage[self.GateM.grid[j][i]])
                        else:
                            self.ax.text(0.5, 0.5, self.GateM.grid[j][i], horizontalalignment='center',
                                         verticalalignment='center', transform=self.ax.transAxes)
                        self.ax.set_axis_off()
                        self.canvas.draw()  # refresh canvas
                        self.canvas.installEventFilter(self)
                        self.layout.addWidget(self.canvas)
                        Box = QVBoxLayout()
                        Box.addWidget(self.Frame)
                        self.gridLayout.removeItem(
                            self.gridLayout.itemAtPosition(j, i))
                        self.gridLayout.addLayout(Box, j, i)
                    else:
                        if ((j, i) not in skip):
                            name = self.GateM.positionsWithCustomGates[(j, i)]
                            self.ax.set_axis_off()
                            self.canvas.draw()  # refresh canvas
                            self.canvas.installEventFilter(self)
                            self.layout.addWidget(self.canvas)
                            Box = QVBoxLayout()
                            Box.addWidget(self.Frame)
                            self.gridLayout.addLayout(Box, j, i, len(
                                self.GateM.customGates[name][0]), len(self.GateM.customGates[name][1]))
                            for x in range(len(self.GateM.customGates[name][0])):
                                for y in range(len(self.GateM.customGates[name][1])):
                                    skip.add((j + x, i + y))
                                    self.gridLayout.removeItem(
                                        self.gridLayout.itemAtPosition(j + x, i + y))

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
    def dropEvent(self, 
            event
        ):
        if not event.source().geometry().contains(event.pos()):
            source = self.get_index(event.pos())
            if source is None:
                return
            
            # Get source and destination points
            row, col, _, _ = self.gridLayout.getItemPosition(self.target)
            row2, col2, _, _ = self.gridLayout.getItemPosition(source)
            
            # If it is a photonic gate, get necessary values for gate specification
            if (self.SS.photonicMode == True):
                val1 = QInputDialog.getDouble(
                    self, 'First Gate Argument', 'Input:')[0]
                val2 = QInputDialog.getDouble(
                    self, 'Second Gate Argument', 'Input:')[0]
                # Specify the gate properties
                self.GridM.designer.settings.specialGridSettings[(
                    col2-self.GraphM.offSetHorizontal, row2)] = [val1, val2]
                print(self.GridM.designer.settings.specialGridSettings)

            p1, p2 = self.gridLayout.getItemPosition(
                self.target), self.gridLayout.getItemPosition(source)
            # If we are moving a point on the user board, replace positions
            if (self.gridLayout.getItemPosition(self.target)[1] < self.GraphM.offSetHorizontal):
                self.Frame = QFrame(self)
                self.Frame.setStyleSheet("background-color: white;")
                self.Frame.setLineWidth(0)
                self.layout = QHBoxLayout(self.Frame)
                self.figure = Figure()  # a figure to plot on
                self.canvas = FigureCanvas(self.figure)
                self.ax = self.figure.add_subplot(111)  # create an axis
                isCustom = False

                self.GridM.designer.giveGUIGrid(self.GridM.grid)
                f = tempfile.NamedTemporaryFile(delete=False)
                self.GridM.designer.saveSimulationToFile(f.name)
                self.GateM.undoStack.append(f.name)
                f.close()

                if (GUIHelper.initial(self.GateM, self.SS, row, col) not in self.GateM.customGates):
                    self.ax.imshow(self.GraphM.gateToImage[GUIHelper.initial(self.GateM, self.SS, row, col)])
                else:
                    self.ax.text(0.5, 0.5, GUIHelper.initial(self.GateM, self.SS, row, col), horizontalalignment='center',
                                 verticalalignment='center', transform=self.ax.transAxes)
                    isCustom = True
                    print("Dropped Custom (Drag and Drop)")
                
                if ((row, col) in self.GateM.positionsWithCustomGates):
                    isCustom = True
                    self.GridM.grid[row][col]

                self.ax.set_axis_off()
                self.canvas.draw()  # refresh canvas
                self.canvas.installEventFilter(self)
                self.layout.addWidget(self.canvas)
                Box = QVBoxLayout()
                Box.addWidget(self.Frame)
                self.gridLayout.takeAt(source)

                if (isCustom):
                    print("Calling updateGUILayout")
                    self.GridM.grid[row2][col2] = self.GridM.grid[row][col]
                    self.updateGUILayout()
                else:
                    self.gridLayout.addLayout(Box, row2, col2)  # row2, col2
                    self.GridM.grid[row2][col2] = self.GridM.grid[row][col]
            else:  # Else, ONLY move the gate in the user board
                isCustom = False
                if ((row, col) in self.GateM.positionsWithCustomGates):
                    name = self.GateM.positionsWithCustomGates[(row, col)]
                    for x in range(len(self.GateM.customGates[name][0])):
                        for y in range(len(self.GateM.customGates[name][1])):
                            self.GridM.grid[row + x][col + y] = "-"
                            self.gridLayout.removeItem(
                                self.gridLayout.itemAtPosition(row + x, col + y))
                    self.GridM.grid[row][col] = name
                    self.gridLayout.removeItem(
                        self.gridLayout.itemAtPosition(row, col))
                    del self.GateM.positionsWithCustomGates[(row, col)]
                    isCustom = True
                if ((row2, col2) in self.GateM.positionsWithCustomGates):
                    name = self.GateM.positionsWithCustomGates[(row2, col2)]
                    for x in range(len(self.GateM.customGates[name][0])):
                        for y in range(len(self.GateM.customGates[name][1])):
                            self.GridM.grid[row2 + x][col2 + y] = "-"
                            self.gridLayout.removeItem(
                                self.gridLayout.itemAtPosition(row2 + x, col2 + y))
                    self.GridM.grid[row2][col2] = name
                    self.gridLayout.removeItem(
                        self.gridLayout.itemAtPosition(row2, col2))
                    del self.GateM.positionsWithCustomGates[(row2, col2)]
                    isCustom = True

                self.GridM.grid[row][col], self.GridM.grid[row2][col2] = self.GridM.grid[row2][col2], self.GridM.grid[row][col]
                if (isCustom):
                    print("Calling updateGUILayout")
                    self.canvas.draw()
                    self.updateGUILayout()
                else:
                    tempA = self.gridLayout.itemAtPosition(row, col)
                    tempB = self.gridLayout.itemAtPosition(row2, col2)
                    self.gridLayout.removeItem(
                        self.gridLayout.itemAtPosition(row, col))
                    self.gridLayout.removeItem(
                        self.gridLayout.itemAtPosition(row2, col2))
                    self.gridLayout.addItem(tempA, *p2)
                    self.gridLayout.addItem(tempB, *p1)

            # Print out the grid (for debugging purposes)
            print("Quantum Circuit Printout:")
            print(self.GridM.grid)

            numDepth, numQubits = self.GraphM.currentWidth, self.GraphM.currentHeight
            entry = "-" * 3*(numDepth+1)
            print(entry)
            
            starredPositions = {(-1, -1)}
            for qubit in range(numQubits):
                tempStr = ""
                for depth in range(self.GraphM.offSetHorizontal, numDepth + self.GraphM.offSetHorizontal):
                    if ((qubit, depth) in starredPositions):
                        tempStr += "[*]"
                    else:
                        tempStr += "[" + self.GridM.grid[qubit][depth] + "]"
                    if (len(self.GridM.grid[qubit][depth]) >= 3 and "PP" not in self.GridM.grid[qubit][depth]):
                        starredPositions.add((qubit + 1, depth))
                tempStr += "[M]"
                print(tempStr)
            print(entry)

    # update layout basesd on designer class' grid
    def updateGUILayout(self, 

    ):
        # Basically a repeat from GUI initialization, see those comments for explainations
        skipThis = [-1, -1]
        print("Is this it?")
        for j in range(1, self.GraphM.offSetHorizontal + 1):
            for i in range(self.GraphM.currentHeight):
                if (skipThis[0] == i and skipThis[1] == j):
                    self.GridM.grid[i][j - 1] = "-"
                    break
                self.GridM.grid[i][j-1] = "-"
                self.Frame = QFrame(self)
                self.Frame.setStyleSheet("background-color: white;")
                self.Frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
                self.Frame.setLineWidth(0)
                self.layout = QHBoxLayout(self.Frame)

                self.figure = Figure()  # a figure to plot on
                self.canvas = FigureCanvas(self.figure)
                self.ax = self.figure.add_subplot(111)  # create an axis
                if (j == self.GraphM.offSetHorizontal):
                    self.Frame.setStyleSheet("background-color: grey;")
                    Box = QVBoxLayout()
                    Box.addWidget(self.Frame)
                    self.gridLayout.addLayout(Box, i, j-1, len(self.GridM.grid)-2, 1)
                    self.GridM.priorBarrier = [i, j-1, len(self.GridM.grid)-2, 1]
                else:
                    self.GridM.grid[i][j - 1] = GUIHelper.initial(self.GateM, self.SS, i, j - 1)
                    if (self.GridM.grid[i][j - 1] not in self.GateM.customGates):
                        self.ax.imshow(self.GraphM.gateToImage[self.GridM.grid[i][j - 1]])
                    else:
                        self.ax.text(0.5, 0.5, self.GridM.grid[j][i-1], horizontalalignment='center',
                                     verticalalignment='center', transform=self.ax.transAxes)
                    self.ax.set_axis_off()
                    self.canvas.draw()  # refresh canvas
                    self.layout.addWidget(self.canvas)
                    self.canvas.installEventFilter(self)
                    Box = QVBoxLayout()
                    Box.addWidget(self.Frame)
                    self.gridLayout.addLayout(Box, i, j - 1)

        skip = []
        for i in range(self.GraphM.offSetHorizontal, self.GraphM.currentWidth + self.GraphM.offSetHorizontal):
            for j in range(self.GraphM.currentHeight):
                self.Frame = QFrame(self)
                self.Frame.setStyleSheet("background-color: white;")
                self.Frame.setLineWidth(0)
                self.layout = QHBoxLayout(self.Frame)

                self.figure = Figure()  # a figure to plot on
                self.canvas = FigureCanvas(self.figure)
                self.ax = self.figure.add_subplot(111)  # create an axis
                isCustom = False
                name = "NA"
                if (self.GridM.grid[j][i] not in self.GateM.customGates and (j, i) not in self.GateM.positionsWithCustomGates):
                    self.ax.imshow(self.GraphM.gateToImage[self.GridM.grid[j][i]])
                else:
                    if ((j, i) not in self.GateM.positionsWithCustomGates):
                        name = self.GridM.grid[j][i]
                        self.Frame.setStyleSheet("background-color: black;")
                        self.ax.text(0.2, 0.75, self.GridM.grid[j][i], horizontalalignment='center',
                                     verticalalignment='center', transform=self.ax.transAxes)
                        self.ax.imshow(self.GraphM.gateToImage[" "])
                        isCustom = True
                        print("Custom Detected")
                    else:
                        name = self.GateM.positionsWithCustomGates[(j, i)]
                        for x in range(len(self.GateM.customGates[name][0])):
                            for y in range(len(self.GateM.customGates[name][1])):
                                skip.append((j + x, i + y))
                                self.gridLayout.removeItem(
                                    self.gridLayout.itemAtPosition(j + x, i + y))
                        self.gridLayout.addLayout(Box, j, i, len(
                            self.GateM.customGates[name][0]), len(self.GateM.customGates[name][1]))
                if ((j, i) in skip):
                    self.ax.imshow(self.GraphM.gateToImage[" "])
                    self.Frame.setStyleSheet("background-color: black;")


                self.ax.set_axis_off()
                self.canvas.draw()  # refresh canvas
                self.canvas.installEventFilter(self)
                self.layout.addWidget(self.canvas)
                Box = QVBoxLayout()
                Box.addWidget(self.Frame)
                if (not isCustom):
                    self.gridLayout.addLayout(Box, j, i)
                else:
                    self.gridLayout.addLayout(Box, j, i, len(
                        self.GateM.customGates[name][0]), len(self.GateM.customGates[name][1]))
                    for x in range(len(self.GateM.customGates[name][0])):
                        for y in range(len(self.GateM.customGates[name][1])):
                            self.GridM.grid[j+x][i+y] = (self.GateM.customGates[name])[x][y]
                            skip.append((j+x, i+y))
                    self.GateM.positionsWithCustomGates[(j, i)] = name
        print("UPDATED-------------------")

