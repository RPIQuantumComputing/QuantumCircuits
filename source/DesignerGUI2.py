import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QPushButton

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

        # Create a grid (right side) for drag-and-drop
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        # Add grid cells with numerical input boxes
        # Implement drag-and-drop functionality here

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
