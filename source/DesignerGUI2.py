from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QVBoxLayout, QSplitter, QMessageBox
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag, QPainter, QPen
from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox
import sys

class Overlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.cnot_lines = []  # This will store tuples of QPoint for start and end points of lines

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))

        for line in self.cnot_lines:
            painter.drawLine(line[0], line[1])

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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_control = False
        self.is_target = False
        self.is_line = False
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid black; width: 40px; height: 40px;")

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.black, 2))
        rect = self.rect()

        # Draw line as a vertical line if the cell is part of the connection
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
        # Handle the drop event for CNOT and other gates
        gate_text = event.mimeData().text()
        if gate_text == "CNOT":
            self.parent_widget.place_cnot_gate(self.col, self.row)
        else:
            self.setText(gate_text)
        event.acceptProposedAction()


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize attributes
        self.cnot_started = False
        self.cnot_column = None
        self.control_row = None
        self.cnot_positions = {}  # Keep track of all CNOT control and target positions by column
        self.gate_positions = []  # This will be a 2D list updated in setupGrid

        # Set up the UI elements
        splitter = QSplitter(Qt.Horizontal)
        self.left_selection_area = QGridLayout()
        self.grid_layout = QGridLayout()  # Initialize grid_layout here

        # Left Selection Area
        self.items = ["H", "T", "S", "X", "Y", "Z", "CNOT"]
        for idx, item in enumerate(self.items):
            row, col = divmod(idx, 2)
            label = DraggableLabel(item)
            label.setStyleSheet("border: 1px solid black; padding: 10px;")
            self.left_selection_area.addWidget(label, row, col)

        # Create the dialog to set the grid size
        self.gridSizeDialog = GridSizeDialog(self)
        if self.gridSizeDialog.exec_():
            rows, cols = self.gridSizeDialog.getValues()
            self.setupGrid(rows, cols)

       # After setting up the grid
        self.overlay = Overlay(self)
        self.overlay.resize(self.size())  # Make sure the overlay covers the entire grid
        self.update_overlay()

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
        self.showMaximized()

    def place_cnot_gate(self, col, row):
        existing_cnot = self.cnot_positions.get(col, {})
        existing_control = existing_cnot.get('control')
        existing_target = existing_cnot.get('target')
        self.gate_positions[row][col] = "CNOT"  # Set control position

        # If there's an existing CNOT in this column, and we're within its control and target range, prevent placement
        if existing_cnot and existing_target is not None:
            if existing_control <= row <= existing_target or existing_target <= row <= existing_control:
                QMessageBox.warning(self, 'Error', 'Cannot place a CNOT here.')
                return

        # If we haven't started a CNOT yet, place the control
        if not self.cnot_started:
            self.cnot_started = True
            self.cnot_column = col
            self.cnot_positions[col] = {'control': row, 'target': None}  # Initialize target as None
            control_cell = ControlledGateCell()
            control_cell.is_control = True
            self.grid_layout.addWidget(control_cell, row, col)
        else:
            # If we're finishing a CNOT, check that the column is the same and place the target
            if col != self.cnot_column or row == existing_control:
                QMessageBox.warning(self, 'Error', 'Target must be in the same column and different row as control.')
                return
            # Place the target
            self.cnot_positions[col]['target'] = row
            target_cell = ControlledGateCell()
            target_cell.is_target = True
            self.grid_layout.addWidget(target_cell, row, col)
            self.draw_connection(existing_control, row, col)
            self.cnot_started = False  # Reset the CNOT placement process

    def draw_connection(self, control_row, target_row, col):
        # Draw the connection line between the control and the target
        for row in range(min(control_row, target_row) + 1, max(control_row, target_row)):
            line_cell = ControlledGateCell()
            line_cell.is_line = True
            self.grid_layout.addWidget(line_cell, row, col)
        self.gate_positions[max(control_row, target_row) - 1][col] = "*"  # Set target and line positions

    def add_cnot_gate(self, control_row, target_row, col):
        # Remove existing widgets if any and add ControlledGateCell for the target and line
        for row in range(5):  # Assuming a 5x5 grid as previously set up
            item = self.grid_layout.itemAtPosition(row, col)
            if item:
                widget = item.widget()
                if widget:
                    self.grid_layout.removeWidget(widget)
                    widget.deleteLater()

            cell = ControlledGateCell(self, row, col)
            if row == control_row:
                cell.is_control = True
            elif row == target_row:
                cell.is_target = True
            elif control_row < row < target_row or target_row < row < control_row:
                cell.is_line = True  # This will draw a vertical line

            self.grid_layout.addWidget(cell, row, col)

    def create_or_update_cnot_column(self, col, row):
        if col in self.control_positions and col in self.target_positions:
            # If both control and target are already set in this column, show an error message
            QMessageBox.warning(self, 'Error', 'This column already has a CNOT gate defined.')
            return

        if col not in self.control_positions:
            # Set this cell as the control
            self.control_positions[col] = row
            cell = self.grid_layout.itemAtPosition(row, col).widget()
            if cell:
                cell.is_control = True
                cell.update()
        elif col not in self.target_positions:
            # Set this cell as the target
            self.target_positions[col] = row
            cell = self.grid_layout.itemAtPosition(row, col).widget()
            if cell:
                cell.is_target = True
                cell.update()

            # Draw the line between control and target
            self.update_cnot_connection(col)
        else:
            # This is a new column for CNOT, so we'll set this cell as control
            self.control_positions[col] = row
            # We need to instantiate a ControlledGateCell, not just update the existing QLabel
            controlled_gate = ControlledGateCell()
            controlled_gate.is_control = True  # Set as control
            self.grid_layout.addWidget(controlled_gate, row, col)


    def update_cnot_connection(self, col):
        if col in self.control_positions and col in self.target_positions:
            control_row = self.control_positions[col]
            target_row = self.target_positions[col]
            for row in range(min(control_row, target_row) + 1, max(control_row, target_row)):
                cell = self.grid_layout.itemAtPosition(row, col).widget()
                if cell:
                    cell.is_control = True  # Using the same flag for drawing lines
                    cell.update()

    def configureGrid(self):
        if self.gridSizeDialog.exec_():
            rows, cols = self.gridSizeDialog.getValues()
            self.setupGrid(rows, cols)

    def setupGrid(self, rows, cols):
        # Clear the existing grid layout first
        for i in reversed(range(self.grid_layout.count())): 
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            self.grid_layout.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)
        
        # Initialize the 2D list with empty strings
        self.gate_positions = [["" for _ in range(cols)] for _ in range(rows)]
        
        # Create the grid with the specified number of rows and columns
        for i in range(rows):
            for j in range(cols):
                drop_area = DropArea(self, i, j)
                self.grid_layout.addWidget(drop_area, i, j)

    def update_overlay(self):
        # Call this method whenever you need to update the lines
        self.overlay.cnot_lines.clear()

        # Calculate the start and end points for the CNOT lines
        for col, cnot in self.cnot_positions.items():
            if cnot.get('control') is not None and cnot.get('target') is not None:
                control_widget = self.grid_layout.itemAtPosition(cnot['control'], col).widget()
                target_widget = self.grid_layout.itemAtPosition(cnot['target'], col).widget()

                # Calculate the center y-coordinates for control and target widgets
                control_center_y = control_widget.geometry().center().y()
                target_center_y = target_widget.geometry().center().y()

                # X-coordinate is the same for both points
                x = control_widget.geometry().center().x()

                self.overlay.cnot_lines.append((QPoint(x, control_center_y), QPoint(x, target_center_y)))

        self.overlay.update()  # Trigger a repaint of the overlay
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_widget = MainWidget()
    main_widget.show()
    sys.exit(app.exec_())