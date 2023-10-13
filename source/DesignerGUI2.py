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
        # You can customize this part based on your needs

        layout.addWidget(selection_widget, 0, 0)
        layout.setColumnMinimumWidth(0, 100)  # Adjust the width

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
