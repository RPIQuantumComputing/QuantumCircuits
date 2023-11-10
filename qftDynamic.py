# -*- coding: utf-8 -*-
"""
Seth Watabe
10/13/2023
A rough draft for a visualization tool for the period finding aspect of Shor's Algorithm.
"""


"""
TO DO:
    
Add arbitrary dimensions to the text box, not fixed. That'll make it work nice with the main code. 
    
Explain also how it can be used for phase approximations and stuff. 
    Maybe a new page. 
    Or maybe redo the explanation
    It maps energy spin units to time, and the amplitude/time such and such things can reduce to p. 
    
Do a version in terms of some arbitrary "p" variable. 
    
Press "Enter" to add element
    
Explain how this is relevant to Shor's on the right panel, give example of what you'd plug in and stuff.  

Use matplotlib to actually show the cancellation of frequencies and stuff to get to 1/p. 

"""










import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import pyqtSlot, Qt
import math

class App(QMainWindow):
    
    # Performs the Quantum Fourier Transform on every element of the passed list
    # Sends the data to the second passed list. 
    def qftMath(self, arr, newList):
    
        for k in range(len(arr)):
            newList.append(complex(0,0))
            #newList.append(complex(0,0))
            tempCoef = complex(1/math.sqrt(len(arr)),0)
            
            tempSum = complex(0,0)
            for n in range(len(arr)):
                tempSum += arr[n] * (math.e ** (-2 * math.pi * 1j * n * k / len(arr)))
                
            
            newList[k] = tempCoef * tempSum
            
        return
    
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Return: 
            self.add_element()
        elif e.key() == Qt.Key_Space:
            self.calculate()
            

    
    def newWidth(self, num):
        return int((num + 0.0) / self.width * (self.frameGeometry().width() + 0.0))
    
    def newHeight(self, num):
        return int((num + 0.0) / self.height * (self.frameGeometry().height() + 0.0))
    
    def resizeEvent(self, event):
        #print("resize")
        
        #self.width = self.frameGeometry().width()
        #self.height = self.frameGeometry().height()
        
        #self.resizeEvent(event)
        
        
        
        # Make all the labels move to their x / self.height * self.frameGeometry().height(), etc. 
        self.xLabel.move(int(20.0 / self.width * self.frameGeometry().width()), int((20 + 40 * 1.0) / self.height * self.frameGeometry().height()))
        
        # Ooooooooh boy. This is going to hurt. 
        self.xBox.move(self.newWidth(20), self.newHeight(20 + 35 * 2))
        
        self.xText.move(self.newWidth(20), self.newHeight(20 + 40 * 3))
        
        
        self.xOutput.move(self.newWidth(20), self.newHeight(20 + 40 * 4))
        
        
        
        
        self.yText.move(self.newWidth(20), self.newHeight(20 + 40 * 7))
        
        self.yOutput.move(self.newWidth(20), self.newHeight(20 + 40 * 8))
        
        self.calculateButton.move(self.newWidth(20), self.newHeight(600))
        
        self.elementButton.move(self.newWidth(160), self.newHeight(600))
        
        self.clearButton.move(self.newWidth(300), self.newHeight(600))
        
        self.imageLabel.move(self.newWidth(600), self.newHeight(100))
        
        self.imageText.move(self.newWidth(600), self.newHeight(20 + 40 * 10))
        
        
        self.titleLabel.move(self.newWidth(500), self.newHeight(20))
        
        
        
        
        
        
        
        
        
        
            
    
            
    # GUI Initialization 
    def __init__(self):
        super().__init__()
        
        
        """
        # This is supposed to make the window scrollable. 
        # This should work. It doesn't. 
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        scroll = QScrollArea()
        scroll.setWidget(self)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(400)
        layout.addWidget(scroll)
        self.setLayout(layout)
        """
        
        
        self.title = 'QFT Calculator'
        #self.left = 80
        #self.top = 140
        #self.width = 1600
        #self.height = 800
        
        
        
        
        screen = self.screen()
        #print('Screen: %s' % screen.name())
        #size = screen.size()
        #print('Size: %d x %d' % (size.width(), size.height()))
        rect = screen.availableGeometry()
        print('Available: %d x %d' % (1600.0 / 1920 * rect.width(), 800.0 / 1008 * rect.height()))
        
        self.left = int(80.0 / 1920 * rect.width())
        self.top = int(140.0 / 1008 * rect.height())
        self.width = int(1600.0 / 1920 * rect.width()) # used to be 1600
        self.height = int(800.0 / 1008 * rect.height()) # used to be 800
        
        self.initUI()
    
    
    
    # GUI Setup
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
    
    
        #self.instructionLabel = QLabel("Enter your vector:", self)
        #self.instructionLabel.move(20, 20)
        # The following line is necessary. I guess it doesn't make my label the size it should be by default. 
        #self.instructionLabel.adjustSize() 
        #self.instructionLabel.show()
    
    
    
        self.inputVector = []
        
    
    
    
        # Create info label
        self.xLabel = QLabel("Enter an element of your vector:", self)
        self.xLabel.move(20, 20 + 40 * 1)
        #self.x0Label.show()
        self.xLabel.adjustSize() 
        
        # Create input textbox
        self.xBox = QLineEdit(self)
        self.xBox.move(20, 20 + 35 * 2) # One may note that I break from my movement convention here
        self.xBox.resize(280,40)
        
        # Create info label
        self.xText = QLabel("Your Input Vector", self)
        self.xText.move(20, 20 + 40 * 3)
        self.xText.adjustSize() 
        
        # Create dynamic info textbox 
        self.xOutput = QLabel("_______________________________", self)
        self.xOutput.setWordWrap(True)
        self.xOutput.move(20, 20 + 40 * 4)
        self.xOutput.adjustSize() 
        
        
        #--------------------------------
        
        # Output vector:
            
            
        # self.label_2.setText(new_info) # <-- Use this
        
        
        
        # Create info label 
        self.yText = QLabel("Your Output Vector", self)
        self.yText.move(20, 20 + 40 * 7)
        self.yText.adjustSize() 
        
        
        # Create dynamic info label 
        self.yOutput = QLabel("_______________________________", self)
        #self.yOutput.resize(1000,40) // Doesn't work??? 
        self.yOutput.setWordWrap(True)
        self.yOutput.move(20, 20 + 40 * 8)
        self.yOutput.adjustSize() 
        
        
        
        
        
        
        
        
        # Create a button in the window
        self.calculateButton = QPushButton('Calculate', self)
        self.calculateButton.move(20,760)
        
        # connect button to function calculate()
        self.calculateButton.clicked.connect(self.calculate)
        #self.show()
        
        
        
        
        
        
        self.elementButton = QPushButton('Add Element', self)
        self.elementButton.move(160,760)
        
        # connect button to function add_element()
        self.elementButton.clicked.connect(self.add_element)
        
        
        
        
        self.clearButton = QPushButton('Clear', self)
        self.clearButton.move(300,760)
        
        # connect button to function clear()
        self.clearButton.clicked.connect(self.clear)
        
        
        #--------------------------------
        
        self.imageLabel = QLabel(self)
        self.imageLabel.move(600, 100)
        self.pixmap = QPixmap('qft.png')
        self.imageLabel.setPixmap(self.pixmap)
        self.imageLabel.adjustSize()
        
        self.imageText = QLabel("The Quantum Fourier Transform is the quantum computational analog of the discrete Fourier Transform.\nInstead of acting on a vector, it is passed a quantum state.\nIt can often be represented simply as a series of Hadamard gates applied to all n qubits.\nIt has applications in Shor's Algorithm, estimating the eigenvalues of a unitary operator (quantum phase estimation), and the hidden subgroup problem.", self)
        #self.yOutput.resize(1000,40) // Doesn't work??? 
        self.imageText.setWordWrap(True)
        self.imageText.setFont(QFont('Times', 10)) 
        self.imageText.move(600, 20 + 40 * 10)
        self.imageText.adjustSize() 
        
        
        self.titleLabel = QLabel("Quantum Fourier Transform Tool", self)
        #self.titleLabel.setWordWrap(True)
        self.titleLabel.move(500, 20)
        self.titleLabel.setFont(QFont('Times', 20)) 
        self.titleLabel.adjustSize()
        
        
        
        
        self.show()
        
        
    # GUI Button Functions
    @pyqtSlot()
    def add_element(self):
        xVal = float(self.xBox.text())
        self.inputVector.append(complex(xVal, 0)) 
        tempArr = []
        for i in range(len(self.inputVector)):
            #print(i)
            tempArr.append(str(self.inputVector[i]))
            #print(i)
        self.xOutput.setText(", ".join(tempArr))
        self.xOutput.adjustSize() 
        
        self.xBox.clear()
    
    @pyqtSlot()
    def calculate(self):
        
        
        #QMessageBox.question(self, 'Message - pythonspot.com', "You typed: " + textboxValue, QMessageBox.Ok, QMessageBox.Ok)
        #QMessageBox.question(self, 'Message - TEST', "QFT: " + str(x0Val), QMessageBox.Ok, QMessageBox.Ok)
        
        
       
        
        #Call math fxn here
        
        
        answerList = []
        self.qftMath(self.inputVector, answerList)
        
        tempArr = []
        for i in range(len(answerList)):
            tempArr.append(str(answerList[i]))
        self.yOutput.setText(", ".join(tempArr))
        self.yOutput.adjustSize() 
        
        
    @pyqtSlot()
    def clear(self):
        
        self.inputVector.clear() 
        tempArr = []
        for i in range(len(self.inputVector)):
            #print(i)
            tempArr.append(str(self.inputVector[i]))
            #print(i)
        self.xOutput.setText(", ".join(tempArr))
        self.xOutput.adjustSize() 
        
        self.yOutput.setText(", ".join(tempArr))
        self.yOutput.adjustSize() 
        
        print("width:", self.frameGeometry().width(), "| height:", self.frameGeometry().height())
        
        #width = mainWindow.frameGeometry().width()
        #height = mainWindow.frameGeometry().height()
        
        
        #Proof of concept
        #print(1/math.sqrt(5) * (1 + 2 * math.e ** (-2 * math.pi * 1j / 5) + 3 * math.e ** (-4 * math.pi * 1j / 5) + 4 * math.e ** (-6 * math.pi * 1j / 5) + 5 * math.e ** (-8 * math.pi * 1j / 5)))
        



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())