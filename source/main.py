import sys
from PyQt5.QtWidgets import *

# Imported Python files
from Window import Window
from source.DesignerGUI import GraphicsManager, GridManager, GateManager, SimulatorSettings, EmailManager


class Main():
    def __init__(self):
        self.GraphM = GraphicsManager()
        self.GridM = GridManager(self.GraphM)
        self.GateM = GateManager()
        self.SS = SimulatorSettings()
        self.Email = EmailManager(host='smtp.office365.com',
                                  port=587,
                                  username="quantumcircuits@outlook.com",
                                  password="dylansheils0241")
        self.app = QApplication(sys.argv)
        self.window = Window(self.GraphM, self.GridM, self.GateM, self.SS, self.Email)

    def run(self):
        main_class.window.show()
        sys.exit(main_class.app.exec_())


# Create the application, window, and close application if asked
if __name__ == "__main__":
    main_class = Main()
    main_class.run()
