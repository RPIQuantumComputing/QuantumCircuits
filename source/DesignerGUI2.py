from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QVBoxLayout, QSplitter, QMessageBox
from PyQt5.QtCore import Qt, QMimeData, QPoint
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QDrag, QPainter, QPen
from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMainWindow
import sys

class Overlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))

        # Iterate through connections for each gate type
        for gate_type, connections in self.parent().multiqubit_gate_connections.items():
            for connection in connections:
                painter.drawLine(connection[0], connection[1])

class QuantumGate:
    def __init__(self, name, num_controls, num_targets):
        self.name = name
        self.num_controls = num_controls
        self.num_targets = num_targets

class GridSizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Set Grid Size')
        
        self.layout = QFormLayout(self)
        self.rowsInput = QLineEdit(self)
        self.colsInput = QLineEdit(self)
        self.layout.addRow("Rows:", self.rowsInput)
        self.layout.addRow("Columns:", self.colsInput)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addRow(self.buttons)

    def getValues(self):
        return (int(self.rowsInput.text()), int(self.colsInput.text()))

class DraggableLabel(QLabel):
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mimedata = QMimeData()
        mimedata.setText(self.text())
        drag.setMimeData(mimedata)

        drag.exec_(Qt.CopyAction | Qt.MoveAction)

class ControlledGateCell(QLabel):
    def __init__(self, parent=None, gate_name="", row=None, col=None):
        super().__init__(parent)
        self.row = row  # Row position in the grid
        self.col = col  # Column position in the grid
        self.gate_name = gate_name  # Store the gate name
        self.is_control = False
        self.is_target = False
        self.is_line = False
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid black; width: 40px; height: 40px;")

        self.loadGateImage(gate_name)

    def loadGateImage(self, gate_name):
        if gate_name in ["H", "T", "S", "X", "Y", "Z"]:  # List all single qubit gates
            pixmap = QPixmap(f"../assets/{gate_name}.png")  # Assuming images are in an 'images' folder
            self.setPixmap(pixmap)

    # Mouse press event for drag initiation
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        # Set the flag to indicate the widget is being dragged
        self.is_being_dragged = True

        drag = QDrag(self)
        mimedata = QMimeData()
        mimedata.setText(self.gate_name)  # Use the gate name for the drag data
        drag.setMimeData(mimedata)

        # Execute the drag operation and check the result
        result = drag.exec_(Qt.CopyAction | Qt.MoveAction)

        # Reset the flag after the drag operation is complete
        self.is_being_dragged = False

        # If the drag was successful (MoveAction), then you can handle any necessary cleanup here.
        if result == Qt.MoveAction:
            # Handle any cleanup if needed
            pass

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.black, 2))
        rect = self.rect()

        # Draw line if the cell is part of a connection
        if self.is_line:
            painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
            mid_point_x = rect.center().x()
            painter.drawLine(mid_point_x, 0, mid_point_x, rect.height())

        # Draw control as a filled circle
        if self.is_control:
            painter.setBrush(Qt.black)
            radius = min(rect.width(), rect.height()) / 4
            painter.drawEllipse(rect.center(), radius, radius)

        # Draw target as an 'X'
        if self.is_target:
            painter.drawLine(rect.topLeft(), rect.bottomRight())
            painter.drawLine(rect.topRight(), rect.bottomLeft())

        # Draw the gate name
        if self.gate_name in ["H", "T", "S", "X", "Y", "Z"]:
            painter.drawText(rect, Qt.AlignCenter, self.gate_name)

class DropArea(QLabel):
    def __init__(self, parent_widget, row, col):
        super().__init__()
        self.parent_widget = parent_widget  # Changed attribute name to parent_widget
        self.row = row
        self.col = col
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid black; width: 40px; height: 40px;")
        self.setAcceptDrops(True)


    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def mousePressEvent(self, event):
        # Check if this column is the one with the control placed for CNOT
        if self.parent_widget.cnot_started and self.col == self.parent_widget.cnot_column:
            # Set the target
            self.parent_widget.place_cnot_gate(self.col, self.row)

    def dropEvent(self, event):
        gate_text = event.mimeData().text()
        source_widget = event.source()

        if isinstance(source_widget, ControlledGateCell) and source_widget.gate_name == gate_text:
            # Moving gate within the grid
            self.parent_widget.move_gate_within_grid(source_widget, self.row, self.col)
        elif gate_text in self.parent_widget.multiqubit_gates:
            # Handle placing or moving multi-qubit gate
            if self.parent_widget.active_gates.get(self.col):
                # Add target/control to an existing multi-qubit gate
                self.parent_widget.add_target_to_gate(self.col, self.row, self.parent_widget.multiqubit_gates[gate_text])
            else:
                # Place new multi-qubit gate
                self.parent_widget.place_multiqubit_gate(gate_text, self.col, self.row)
        elif gate_text in self.parent_widget.items:
            # Place single qubit gate
            self.parent_widget.place_single_qubit_gate(gate_text, self.row, self.col)
        else:
            QMessageBox.warning(self, 'Error', 'Invalid gate type.')
        event.acceptProposedAction()

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize attributes
        self.cnot_started = False
        self.cnot_column = None
        self.control_row = None
        # Added multiqubit gate representation
        self.multiqubit_gates = {
            "CNOT": QuantumGate("CNOT", 1, 1),
            "Toffoli": QuantumGate("Toffoli", 2, 1)
            # Add more gates as needed
        }
        self.gate_positions = []  # This will be a 2D list updated in setupGrid
        self.multiqubit_gate_connections = {}
        self.active_gates = {}  # Tracks active multiqubit gates


        # Set up the UI elements
        splitter = QSplitter(Qt.Horizontal)
        self.left_selection_area = QGridLayout()
        self.grid_layout = QGridLayout()  # Initialize grid_layout here

        # Left Selection Area
        self.items = ["H", "T", "S", "X", "Y", "Z", "CNOT", "Toffoli"]
        for idx, item in enumerate(self.items):
            row, col = divmod(idx, 2)
            label = DraggableLabel(item)
            label.setStyleSheet("border: 1px solid black; padding: 10px;")
            self.left_selection_area.addWidget(label, row, col)

        # Initialize overlay before calling setupGrid
        self.overlay = Overlay(self)
        self.overlay.resize(self.size())  # Make sure the overlay covers the entire grid

        # Create and execute the dialog to set the grid size
        self.gridSizeDialog = GridSizeDialog(self)
        if self.gridSizeDialog.exec_():
            rows, cols = self.gridSizeDialog.getValues()
            self.setupGrid(rows, cols)

        # Splitter setup
        left_widget = QWidget()
        left_widget.setLayout(self.left_selection_area)
        splitter.addWidget(left_widget)

        right_widget = QWidget()
        right_widget.setLayout(self.grid_layout)
        splitter.addWidget(right_widget)
        splitter.setSizes([int(self.width() / 3), int((2 * self.width()) / 3)])

        # Main layout setup
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(splitter)
        self.setLayout(self.main_layout)

        # Show the maximized main widget
        self.showMaximized()

    def move_gate_within_grid(self, source_widget, new_row, new_col):
        if self.gate_positions[new_row][new_col] == "":
            # Remove the gate from its original position
            old_row, old_col = source_widget.row, source_widget.col
            gate_name = source_widget.gate_name
            self.gate_positions[old_row][old_col] = ""
            self.grid_layout.removeWidget(source_widget)
            source_widget.deleteLater()

            # Check if the gate is part of a multi-qubit gate
            if gate_name in self.multiqubit_gates:
                # Update active_gates dictionary with new positions
                self.update_multiqubit_gate_positions(old_row, old_col, new_row, new_col, gate_name)

            # Place the gate in the new position
            self.gate_positions[new_row][new_col] = gate_name
            new_gate_cell = ControlledGateCell(self, gate_name, new_row, new_col)
            self.grid_layout.addWidget(new_gate_cell, new_row, new_col)
        else:
            QMessageBox.warning(self, 'Error', 'Target cell is already occupied.')


    def place_single_qubit_gate(self, gate_name, row, col):
        # Check if the cell is already occupied
        if self.gate_positions[row][col] != "":
            QMessageBox.warning(self, 'Error', 'Cell already occupied.')
            return

        # Update the gate position in the grid
        self.gate_positions[row][col] = gate_name

        gate_cell = ControlledGateCell(self, gate_name, row, col)
        self.grid_layout.addWidget(gate_cell, row, col)
    
    def place_multiqubit_gate(self, gate_name, col, row):
        # Ensure single qubit gates are not overwritten
        if self.gate_positions[row][col] != "":
            QMessageBox.warning(self, 'Error', 'This cell is already occupied.')
            return


        gate = self.multiqubit_gates.get(gate_name)
        if not gate:
            QMessageBox.warning(self, 'Error', f'Unknown gate: {gate_name}')
            return

        # Check if a gate is already started in this column
        if col in self.active_gates:
            self.add_target_to_gate(col, row, gate)
        else:
            self.start_new_gate(col, row, gate)

        # Set row and col for the newly placed gate
        gate_widget = self.grid_layout.itemAtPosition(row, col).widget()
        if gate_widget and isinstance(gate_widget, ControlledGateCell):
            gate_widget.row = row
            gate_widget.col = col

        self.update_connections()

    def start_new_gate(self, col, row, gate):
        if gate.num_controls + gate.num_targets > 1:
            # Start a new multiqubit gate
            self.active_gates[col] = {'started': True, 'control': [row], 'target': [], 'type': gate.name}
            control_cell = ControlledGateCell(self, gate.name, row, col)
            control_cell.is_control = True
            self.grid_layout.addWidget(control_cell, row, col)
        else:
            # Handle single qubit gate here
            pass

    def add_target_to_gate(self, col, row, gate):
        gate_info = self.active_gates[col]
        if len(gate_info['control']) < gate.num_controls:
            # Add another control
            gate_info['control'].append(row)
            control_cell = ControlledGateCell(self, gate.name, row, col)
            control_cell.is_control = True
            self.grid_layout.addWidget(control_cell, row, col)
        elif len(gate_info['target']) < gate.num_targets:
            # Add a target
            gate_info['target'].append(row)
            target_cell = ControlledGateCell(self, gate.name, row, col)
            target_cell.is_target = True
            self.grid_layout.addWidget(target_cell, row, col)

            if len(gate_info['target']) == gate.num_targets:
                # All targets placed, draw connection
                self.draw_gate_connections(col, gate_info)
                gate_info['started'] = False  # Gate placement finished

    def update_connections(self):
        # Clear existing connections
        self.multiqubit_gate_connections.clear()

        for col, gate_info in self.active_gates.items():
            if gate_info['started']:
                continue

            # Logic to determine the start and end points of connections
            for control_row in gate_info['control']:
                for target_row in gate_info['target']:
                    start_point = self.calculate_connection_point(control_row, col)
                    end_point = self.calculate_connection_point(target_row, col)

                    # Store the connections
                    gate_type = gate_info['type']
                    if gate_type not in self.multiqubit_gate_connections:
                        self.multiqubit_gate_connections[gate_type] = []
                    self.multiqubit_gate_connections[gate_type].append((start_point, end_point))

        self.overlay.update()

    def calculate_connection_point(self, row, col):
        widget = self.grid_layout.itemAtPosition(row, col).widget()
        if widget:
            return widget.geometry().center()
        return QPoint()

    def draw_gate_connections(self, col, gate_info):
        for control_row in gate_info['control']:
            for target_row in gate_info['target']:
                for row in range(min(control_row, target_row) + 1, max(control_row, target_row)):
                    # Skip drawing a line if a single qubit gate is present
                    if self.gate_positions[row][col] == "":
                        line_cell = ControlledGateCell(self, gate_info['type'], row, col)
                        line_cell.is_line = True
                        self.grid_layout.addWidget(line_cell, row, col)

    def update_multiqubit_gate_positions(self, old_row, old_col, new_row, new_col, gate_name):
        # Iterate through the active_gates to find the gate and update its position
        for col, gate_info in self.active_gates.items():
            if gate_info['type'] == gate_name:
                if old_row in gate_info['control']:
                    gate_info['control'].remove(old_row)
                    gate_info['control'].append(new_row)
                if old_row in gate_info['target']:
                    gate_info['target'].remove(old_row)
                    gate_info['target'].append(new_row)
        
        # Redraw connections
        self.update_connections()

    def configureGrid(self):
        if self.gridSizeDialog.exec_():
            rows, cols = self.gridSizeDialog.getValues()
            self.setupGrid(rows, cols)

    def setupGrid(self, rows, cols):
        # Clear the existing grid layout first
        for i in reversed(range(self.grid_layout.count())): 
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.deleteLater()
            self.grid_layout.removeWidget(widget_to_remove)

        # Initialize the 2D list with empty strings
        self.gate_positions = [["" for _ in range(cols)] for _ in range(rows)]

        
        # Create the grid with the specified number of rows and columns
        for i in range(rows):
            for j in range(cols):
                drop_area = DropArea(self, i, j)
                self.grid_layout.addWidget(drop_area, i, j)

        # Clear active gates when resetting grid
        self.active_gates.clear()
        self.update_connections()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()        
        self.main_widget = MainWidget()  # Instantiate MainWidget
        self.setCentralWidget(self.main_widget)  # Set MainWidget as central widget
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())