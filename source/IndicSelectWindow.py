# the main workbench of qcd, a grid that supports drag & drop
class IndicSelectWindow(QDialog):
    def __init__(self, parent=None):
        global priorBarrier
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

        # Go through the grid and initialize values
        # For multiqubit gates, skip initializing covered positions
        skipThis = [-1, -1]
        for j in range(1, offSetHorizontal + 1):
            for i in range(currentHeight):
                grid[i][j - 1] = " "
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

                if (j == offSetHorizontal):  # If we need to create the barrier
                    self.Frame.setStyleSheet("background-color: grey;")
                    Box = QVBoxLayout()
                    Box.addWidget(self.Frame)
                    self.gridLayout.addLayout(Box, i, j-1, len(grid)-2, 1)
                    priorBarrier = [i, j - 1, len(grid)-2, 1]
                else:  # If we are adding just a gate
                    # Find what gate if any should go in position
                    grid[i][j - 1] = initial(i, j - 1)
                    if (grid[i][j - 1] in customGates):
                        self.ax.text(0.5, 0.5, grid[i][j - 1], horizontalalignment='center',
                                     verticalalignment='center', transform=self.ax.transAxes)
                    else:
                        # Show the gate
                        self.ax.imshow(gateToImage[grid[i][j - 1]])
                    self.ax.set_axis_off()
                    self.canvas.draw()  # refresh canvas
                    self.layout.addWidget(self.canvas)
                    self.canvas.installEventFilter(self)
                    Box = QVBoxLayout()
                    Box.addWidget(self.Frame)
                    self.gridLayout.addLayout(Box, i, j - 1)

        # Go through and initialize field user interacts with
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
            row, col, _, _ = self.gridLayout.getItemPosition(
                self.get_index(event.windowPos().toPoint()))
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
        global needToUpdate

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
        if needToUpdate:
            print("Updating....")
            needToUpdate = False
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
                    if ((j, i) not in positionsWithCustomGates and (j, i) not in skip):
                        if (grid[j][i] not in customGates):
                            self.ax.imshow(gateToImage[grid[j][i]])
                        else:
                            self.ax.text(0.5, 0.5, grid[j][i], horizontalalignment='center',
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
                            name = positionsWithCustomGates[(j, i)]
                            self.ax.set_axis_off()
                            self.canvas.draw()  # refresh canvas
                            self.canvas.installEventFilter(self)
                            self.layout.addWidget(self.canvas)
                            Box = QVBoxLayout()
                            Box.addWidget(self.Frame)
                            self.gridLayout.addLayout(Box, j, i, len(
                                customGates[name][0]), len(customGates[name][1]))
                            for x in range(len(customGates[name][0])):
                                for y in range(len(customGates[name][1])):
                                    skip.add((j + x, i + y))
                                    self.gridLayout.removeItem(
                                        self.gridLayout.itemAtPosition(j + x, i + y))

    # If releasing, event on drag and drop occured, so neglect this gate
    def mouseReleaseEvent(self):
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
            row, col, _, _ = self.gridLayout.getItemPosition(self.target)
            row2, col2, _, _ = self.gridLayout.getItemPosition(source)
            
            # If it is a photonic gate, get necessary values for gate specification
            if (photonicMode == True):
                val1 = QInputDialog.getDouble(
                    self, 'First Gate Argument', 'Input:')[0]
                val2 = QInputDialog.getDouble(
                    self, 'Second Gate Argument', 'Input:')[0]
                # Specify the gate properties
                designer.settings.specialGridSettings[(
                    col2-offSetHorizontal, row2)] = [val1, val2]
                print(designer.settings.specialGridSettings)

            p1, p2 = self.gridLayout.getItemPosition(
                self.target), self.gridLayout.getItemPosition(source)
            # If we are moving a point on the user board, replace positions
            if (self.gridLayout.getItemPosition(self.target)[1] < offSetHorizontal):
                self.Frame = QFrame(self)
                self.Frame.setStyleSheet("background-color: white;")
                self.Frame.setLineWidth(0)
                self.layout = QHBoxLayout(self.Frame)
                self.figure = Figure()  # a figure to plot on
                self.canvas = FigureCanvas(self.figure)
                self.ax = self.figure.add_subplot(111)  # create an axis
                isCustom = False

                designer.giveGUIGrid(grid)
                f = tempfile.NamedTemporaryFile(delete=False)
                designer.saveSimulationToFile(f.name)
                undoStack.append(f.name)
                f.close()

                if (initial(row, col) not in customGates):
                    self.ax.imshow(gateToImage[initial(row, col)])
                else:
                    self.ax.text(0.5, 0.5, initial(row, col), horizontalalignment='center',
                                 verticalalignment='center', transform=self.ax.transAxes)
                    isCustom = True
                    print("Dropped Custom (Drag and Drop)")
                
                if ((row, col) in positionsWithCustomGates):
                    isCustom = True
                    grid[row][col]

                self.ax.set_axis_off()
                self.canvas.draw()  # refresh canvas
                self.canvas.installEventFilter(self)
                self.layout.addWidget(self.canvas)
                Box = QVBoxLayout()
                Box.addWidget(self.Frame)
                self.gridLayout.takeAt(source)

                if (isCustom):
                    print("Calling updateGUILayout")
                    grid[row2][col2] = grid[row][col]
                    self.updateGUILayout()
                else:
                    self.gridLayout.addLayout(Box, row2, col2)  # row2, col2
                    grid[row2][col2] = grid[row][col]
            else:  # Else, ONLY move the gate in the user board
                isCustom = False
                if ((row, col) in positionsWithCustomGates):
                    name = positionsWithCustomGates[(row, col)]
                    for x in range(len(customGates[name][0])):
                        for y in range(len(customGates[name][1])):
                            grid[row + x][col + y] = "-"
                            self.gridLayout.removeItem(
                                self.gridLayout.itemAtPosition(row + x, col + y))
                    grid[row][col] = name
                    self.gridLayout.removeItem(
                        self.gridLayout.itemAtPosition(row, col))
                    del positionsWithCustomGates[(row, col)]
                    isCustom = True
                if ((row2, col2) in positionsWithCustomGates):
                    name = positionsWithCustomGates[(row2, col2)]
                    for x in range(len(customGates[name][0])):
                        for y in range(len(customGates[name][1])):
                            grid[row2 + x][col2 + y] = "-"
                            self.gridLayout.removeItem(
                                self.gridLayout.itemAtPosition(row2 + x, col2 + y))
                    grid[row2][col2] = name
                    self.gridLayout.removeItem(
                        self.gridLayout.itemAtPosition(row2, col2))
                    del positionsWithCustomGates[(row2, col2)]
                    isCustom = True

                grid[row][col], grid[row2][col2] = grid[row2][col2], grid[row][col]
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
            print(grid)

            numDepth, numQubits = currentWidth, currentHeight
            entry = "-" * 3*(numDepth+1)
            print(entry)
            
            starredPositions = {(-1, -1)}
            for qubit in range(numQubits):
                tempStr = ""
                for depth in range(offSetHorizontal, numDepth + offSetHorizontal):
                    if ((qubit, depth) in starredPositions):
                        tempStr += "[*]"
                    else:
                        tempStr += "[" + grid[qubit][depth] + "]"
                    if (len(grid[qubit][depth]) >= 3 and "PP" not in grid[qubit][depth]):
                        starredPositions.add((qubit + 1, depth))
                tempStr += "[M]"
                print(tempStr)
            print(entry)

    # update layout basesd on designer class' grid
    def updateGUILayout(self):
        global priorBarrier

        # Basically a repeat from GUI initialization, see those comments for explainations
        skipThis = [-1, -1]
        print("Is this it?")
        for j in range(1, offSetHorizontal + 1):
            for i in range(currentHeight):
                if (skipThis[0] == i and skipThis[1] == j):
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
                if (j == offSetHorizontal):
                    self.Frame.setStyleSheet("background-color: grey;")
                    Box = QVBoxLayout()
                    Box.addWidget(self.Frame)
                    self.gridLayout.addLayout(Box, i, j-1, len(grid)-2, 1)
                    priorBarrier = [i, j-1, len(grid)-2, 1]
                else:
                    grid[i][j - 1] = initial(i, j - 1)
                    if (grid[i][j - 1] not in customGates):
                        self.ax.imshow(gateToImage[grid[i][j - 1]])
                    else:
                        self.ax.text(0.5, 0.5, grid[j][i-1], horizontalalignment='center',
                                     verticalalignment='center', transform=self.ax.transAxes)
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
                if (grid[j][i] not in customGates and (j, i) not in positionsWithCustomGates):
                    self.ax.imshow(gateToImage[grid[j][i]])
                else:
                    if ((j, i) not in positionsWithCustomGates):
                        name = grid[j][i]
                        self.Frame.setStyleSheet("background-color: black;")
                        self.ax.text(0.2, 0.75, grid[j][i], horizontalalignment='center',
                                     verticalalignment='center', transform=self.ax.transAxes)
                        self.ax.imshow(gateToImage[" "])
                        isCustom = True
                        print("Custom Detected")
                    else:
                        name = positionsWithCustomGates[(j, i)]
                        for x in range(len(customGates[name][0])):
                            for y in range(len(customGates[name][1])):
                                skip.append((j + x, i + y))
                                self.gridLayout.removeItem(
                                    self.gridLayout.itemAtPosition(j + x, i + y))
                        self.gridLayout.addLayout(Box, j, i, len(
                            customGates[name][0]), len(customGates[name][1]))
                if ((j, i) in skip):
                    self.ax.imshow(gateToImage[" "])
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
                        customGates[name][0]), len(customGates[name][1]))
                    for x in range(len(customGates[name][0])):
                        for y in range(len(customGates[name][1])):
                            grid[j+x][i+y] = (customGates[name])[x][y]
                            skip.append((j+x, i+y))
                    positionsWithCustomGates[(j, i)] = name
        print("UPDATED-------------------")

