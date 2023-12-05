# -*- coding: utf-8 -*-
"""
Seth Watabe
10/13/2023
A rough draft for a visualization tool for the period finding aspect of Shor's Algorithm.
"""


"""
TO DO:
    
    
Make the button do the calculation w/ given values

Figure out how to mess with i

Change y labels to reflect new values. 


"""










import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
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
        self.left = 100
        self.top = 100
        self.width = 1600
        self.height = 800
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
        
    
    
    
        # Create textbox
        self.xLabel = QLabel("Enter an element of your vector:", self)
        self.xLabel.move(20, 20 + 40 * 1)
        #self.x0Label.show()
        self.xLabel.adjustSize() 
        
        self.xBox = QLineEdit(self)
        self.xBox.move(20, 20 + 35 * 2) # One may note that I break from my movement convention here
        self.xBox.resize(280,40)
        
        
        self.xText = QLabel("Your Input Vector", self)
        self.xText.move(20, 20 + 40 * 3)
        self.xText.adjustSize() 
        
        
        self.xOutput = QLabel("_______________________________", self)
        self.xOutput.setWordWrap(True)
        self.xOutput.move(20, 20 + 40 * 4)
        self.xOutput.adjustSize() 
        
        
        #--------------------------------
        
        # Output vector:
            
            
        # self.label_2.setText(new_info) # <-- Use this
        
        
        self.yText = QLabel("Your Output Vector", self)
        self.yText.move(20, 20 + 40 * 7)
        self.yText.adjustSize() 
        
        
        self.yOutput = QLabel("_______________________________", self)
        #self.yOutput.resize(1000,40) // Doesn't work??? 
        self.yOutput.setWordWrap(True)
        self.yOutput.move(20, 20 + 40 * 8)
        self.yOutput.adjustSize() 
        
        
        
        
        
        
        
        
        # Create a button in the window
        self.button = QPushButton('Calculate', self)
        self.button.move(20,760)
        
        # connect button to function on_click
        self.button.clicked.connect(self.on_click)
        #self.show()
        
        
        
        
        
        
        self.button2 = QPushButton('Add Element', self)
        self.button2.move(160,760)
        
        # connect button to function on_click
        self.button2.clicked.connect(self.add_element)
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
    
    @pyqtSlot()
    def on_click(self):
        
        
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
        
        
        
        #Proof of concept
        #print(1/math.sqrt(5) * (1 + 2 * math.e ** (-2 * math.pi * 1j / 5) + 3 * math.e ** (-4 * math.pi * 1j / 5) + 4 * math.e ** (-6 * math.pi * 1j / 5) + 5 * math.e ** (-8 * math.pi * 1j / 5)))
        



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())