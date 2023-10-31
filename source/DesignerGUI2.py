import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QPushButton, QLineEdit, QLabel

class CustomWidget(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        operation = event.mimeData().text()
        self.setText(operation)

class GridWidget(QWidget):
    def __init__(self, width, height):
        super().__init__()
        self.grid_layout = QGridLayout(self)
        self.width = width
        self.height = height
        self.grid = []

        for i in range(self.height):
            row = []
            for j in range(self.width):
                input_box = QLineEdit()
                row.append(input_box)
                self.grid_layout.addWidget(input_box, i, j)
            self.grid.append(row)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QGridLayout(central_widget)

        # Create a selection widget (left side)
        selection_widget = QWidget()
        selection_layout = QGridLayout(selection_widget)

        # Add buttons for operations
        operations = ["X", "Y", "Z", "CNOT", "CX", "CZ", "RX", "RY", "RZ", "P", "T", "T'", "P'", "H", "M", "Toffoli", "U(theta1, theta2, theta3)", "RZZ", "RYY", "RXX", "RXY"]
        row = 0
        col = 0
        for operation in operations:
            operation_button = CustomWidget(operation)
            selection_layout.addWidget(operation_button, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1

        layout.addWidget(selection_widget, 0, 0)
        layout.setColumnMinimumWidth(0, 200)  # Adjust the width

        # Create input fields for grid width and height
        width_label = QLabel("Grid Width:")
        height_label = QLabel("Grid Height:")
        self.width_input = QLineEdit()
        self.height_input = QLineEdit()

        layout.addWidget(width_label, 1, 0)
        layout.addWidget(self.width_input, 1, 1)
        layout.addWidget(height_label, 2, 0)
        layout.addWidget(self.height_input, 2, 1)

        # Create a grid (right side) for drag-and-drop
        grid_widget = GridWidget(1, 1)  # Default grid size
        layout.addWidget(grid_widget, 0, 1)
        layout.setColumnStretch(1, 1)  # Allow resizing of the right grid

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Custom PyQt5 Widget')
        self.show()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
