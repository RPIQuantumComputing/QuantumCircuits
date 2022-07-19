from PyQt6.QtCore import Qt, QMimeData, QSize
from PyQt6.QtGui import QDrag, QIcon, QAction
from PyQt6.QtWidgets import (QApplication, QListWidget, QListView, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QListWidgetItem, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QToolBar, QToolBox, QStatusBar, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)

import DesignerFile as Designer

designer = Designer.Designer()

class DragButton(QPushButton):
    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)
            drag.exec_(Qt.MoveAction)

class Setting(QDialog):
    def dropEvent(self, event):
        if not event.source().geometry().contains(event.pos()):
            source = self.get_index(event.pos())
            if source is None:
                return

            i, j = max(self.target, source), min(self.target, source)
            p1, p2 = self.grid.getItemPosition(i), self.grid.getItemPosition(j)

            self.grid.addItem(self.grid.takeAt(i), *p2)
            self.grid.addItem(self.grid.takeAt(j), *p1)

    def __init__(self, parent=None):
        super(Setting, self).__init__(parent)
        win = QWidget()
        self.originalPalette = QApplication.palette()

        background = QComboBox()
        background.addItems(QStyleFactory.keys())

        self.grid = QGridLayout()
        for i in range(1,5):
        	for j in range(1,5):
        		self.grid.addWidget(QPushButton("B"+str(i)+str(j)),i,j)

        win.setLayout(self.grid)
        win.setGeometry(100,100,200,100)
        
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

        toolbar.addWidget(background)

        main_layout = QGridLayout()
        main_layout.addWidget(win)
        main_layout.addWidget(self.SimulationChoice, 0, 1)
        main_layout.addWidget(self.SimulationSetting, 2, 1)
        main_layout.setMenuBar(toolbar)
        self.setLayout(main_layout)
        #self.setStyleSheet("background-color: yellow;")

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
        num_qubits.setValue(2)
        qubit_label = QLabel("&Number of Qubits: ")
        qubit_label.setBuddy(num_qubits)

        num_width = QSpinBox(self.SimulationSetting)
        num_width.setValue(10)
        width_label = QLabel("&Width: ")
        
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
        if radioButton.isChecked():
            designer.settings.backend = radioButton.sim
        

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    setting = Setting()
    setting.show()
    sys.exit(app.exec())