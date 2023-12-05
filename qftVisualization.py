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
    
    def qftMath(self, arr):
        newList = [complex(0,0),complex(0,0),complex(0,0),complex(0,0),complex(0,0)]
        for k in range(len(arr)):
            tempCoef = complex(1/math.sqrt(len(arr)),0)
            
            tempSum = complex(0,0)
            for n in range(len(arr)):
                tempSum += arr[n] * (math.e ** (-2 * math.pi * 1j * n * k / len(arr)))
                
            
            newList[k] = tempCoef * tempSum
            
        return newList
            
            
            

    def __init__(self):
        super().__init__()
        self.title = 'QFT Calculator'
        self.left = 100
        self.top = 100
        self.width = 800
        self.height = 800
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
    
    
        self.instructionLabel = QLabel("Enter your vector:", self)
        self.instructionLabel.move(20, 20)
        # The following line is necessary. I guess it doesn't make my label the size it should be by default. 
        self.instructionLabel.adjustSize() 
        #self.instructionLabel.show()
    
    
    
        # Create textbox
        self.x0Label = QLabel("x0:", self)
        self.x0Label.move(20, 20 + 40 * 1)
        #self.x0Label.show()
        
        self.x0Box = QLineEdit(self)
        self.x0Box.move(100, 20 + 40 * 1)
        self.x0Box.resize(280,40)
        #--------------------------------
        self.x1Label = QLabel("x1:", self)
        self.x1Label.move(20, 20 + 40 * 2)
        #self.x1Label.show()
        
        self.x1Box = QLineEdit(self)
        self.x1Box.move(100, 20 + 40 * 2)
        self.x1Box.resize(280,40)
        #--------------------------------
        self.x2Label = QLabel("x2:", self)
        self.x2Label.move(20, 20 + 40 * 3)
        #self.x2Label.show()
        
        self.x2Box = QLineEdit(self)
        self.x2Box.move(100, 20 + 40 * 3)
        self.x2Box.resize(280,40)
        #--------------------------------
        self.x3Label = QLabel("x3:", self)
        self.x3Label.move(20, 20 + 40 * 4)
        #self.x3Label.show()
        
        self.x3Box = QLineEdit(self)
        self.x3Box.move(100, 20 + 40 * 4)
        self.x3Box.resize(280,40)
        #--------------------------------
        self.x4Label = QLabel("x4:", self)
        self.x4Label.move(20, 20 + 40 * 5)
        #self.x4Label.show()
        
        self.x4Box = QLineEdit(self)
        self.x4Box.move(100, 20 + 40 * 5)
        self.x4Box.resize(280,40)
        
        
        #--------------------------------
        
        # Output vector:
            
            
        # self.label_2.setText(new_info) # <-- Use this
        
        
        self.y0Label = QLabel("y0: ", self)
        self.y0Label.move(20, 20 + 40 * 8)
        
        self.y0Output = QLabel("_______________________________", self)
        self.y0Output.move(100, 20 + 40 * 8)
        self.y0Output.adjustSize() 
        
        self.y1Label = QLabel("y1: ", self)
        self.y1Label.move(20, 20 + 40 * 9)
        
        self.y1Output = QLabel("_______________________________", self)
        self.y1Output.move(100, 20 + 40 * 9)
        self.y1Output.adjustSize() 
        
        self.y2Label = QLabel("y2: ", self)
        self.y2Label.move(20, 20 + 40 * 10)
        
        self.y2Output = QLabel("_______________________________", self)
        self.y2Output.move(100, 20 + 40 * 10)
        self.y2Output.adjustSize() 
        
        self.y3Label = QLabel("y3: ", self)
        self.y3Label.move(20, 20 + 40 * 11)
        
        self.y3Output = QLabel("_______________________________", self)
        self.y3Output.move(100, 20 + 40 * 11)
        self.y3Output.adjustSize() 
        
        self.y4Label = QLabel("y4: ", self)
        self.y4Label.move(20, 20 + 40 * 12)
        
        self.y4Output = QLabel("_______________________________", self)
        self.y4Output.move(100, 20 + 40 * 12)
        self.y4Output.adjustSize() 
        
        
        
        
        
        
        
        
        # Create a button in the window
        self.button = QPushButton('Calculate', self)
        self.button.move(20,760)
        
        # connect button to function on_click
        self.button.clicked.connect(self.on_click)
        self.show()
    
    @pyqtSlot()
    def on_click(self):
        #textboxValue = self.textbox.text()
        x0Val = float(self.x0Box.text())
        x1Val = float(self.x1Box.text())
        x2Val = float(self.x2Box.text())
        x3Val = float(self.x3Box.text())
        x4Val = float(self.x4Box.text())
        
        
        #QMessageBox.question(self, 'Message - pythonspot.com', "You typed: " + textboxValue, QMessageBox.Ok, QMessageBox.Ok)
        #QMessageBox.question(self, 'Message - TEST', "QFT: " + str(x0Val), QMessageBox.Ok, QMessageBox.Ok)
        
        
        x0Comp = complex(x0Val, 0)
        x1Comp = complex(x1Val, 0)
        x2Comp = complex(x2Val, 0)
        x3Comp = complex(x3Val, 0)
        x4Comp = complex(x4Val, 0)
        
        
        #Call math fxn here
        
        
        inputArr = []
        inputArr.append(x0Comp)
        inputArr.append(x1Comp)
        inputArr.append(x2Comp)
        inputArr.append(x3Comp)
        inputArr.append(x4Comp)
        
        answerList = self.qftMath(inputArr)
        
        self.y0Output.setText(str(answerList[0]))
        self.y1Output.setText(str(answerList[1]))
        self.y2Output.setText(str(answerList[2]))
        self.y3Output.setText(str(answerList[3]))
        self.y4Output.setText(str(answerList[4]))
        
        self.y0Output.adjustSize() 
        self.y1Output.adjustSize() 
        self.y2Output.adjustSize() 
        self.y3Output.adjustSize() 
        self.y4Output.adjustSize() 
        
        
        #Proof of concept
        #print(1/math.sqrt(5) * (1 + 2 * math.e ** (-2 * math.pi * 1j / 5) + 3 * math.e ** (-4 * math.pi * 1j / 5) + 4 * math.e ** (-6 * math.pi * 1j / 5) + 5 * math.e ** (-8 * math.pi * 1j / 5)))
        



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())