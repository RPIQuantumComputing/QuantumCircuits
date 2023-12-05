# -*- coding: utf-8 -*-
"""
Seth Watabe
12/1/23
A visualization tool for Euclid's Algorithm, specifically the part related to Shor's Algorithm. 
"""











import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import pyqtSlot, Qt
import math

class App(QMainWindow):
    
    
    myWidth = 1920
    myHeight = 1008
    myTop = 140
    myLeft = 80
    
    
    
    # The recursive function that performs Euler's Algorithm
    def EulerAlg(self, A, B):
        
        # If either of the two numbers is 0, return the other. 
        if(A == 0):
            return B
        
        elif(B == 0):
            return A
        
        # Stores the values of each part for the next iteration
        tempA = B
        tempB = A % B
        
        # Recursively calls itself on new arguments. 
        return self.EulerAlg(tempA, tempB)
        
    
    
    def resetDimensions(self):
        self.myWidth = 1920
        self.myHeight = 1008
        self.myTop = 140
        self.myLeft = 80
        
    def dynamicDimensions(self):
        self.myWidth = self.width()
        self.myHeight = self.height()
        self.myTop = self.top()
        self.myLeft = self.left()
    
    
    
    
    
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
        
        self.xBox.move(self.newWidth(20), self.newHeight(20 + 30 * 3))
        
        self.calculateButton.move(self.newWidth(700), self.newHeight(600))
        
        self.x2Label.move(self.newWidth(20), self.newHeight(20 + 40 * 5))
        
        self.x2Box.move(self.newWidth(20), self.newHeight(20 + 35 * 7))
        
        
        self.titleLabel.move(self.newWidth(550), self.newHeight(20))
        
        self.yOutput.move(self.newWidth(20), self.newHeight(20 + 40 * 10))
        
        self.imageText.move(self.newWidth(600), self.newHeight(20 + 40 * 4))
        
        
        
            
    
            
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
        
        
        self.title = 'Euclid\'s Algorithm Calculator'
        #self.left = 80
        #self.top = 140
        #self.width = 1600
        #self.height = 800
        
        
        self.setStyleSheet("background-color: darkcyan;") 
  
        
        
        
        #screen = self.screen()
        #print('Screen: %s' % screen.name())
        #size = screen.size()
        #print('Size: %d x %d' % (size.width(), size.height()))
        #rect = screen.availableGeometry()
        #print('Available: %d x %d' % (1600.0 / 1920 * rect.width(), 800.0 / 1008 * rect.height()))
        
        #self.left = int(80.0 / 1920 * rect.width())
        #self.top = int(140.0 / 1008 * rect.height())
        #self.width = int(1600.0 / 1920 * rect.width()) # used to be 1600
        #self.height = int(800.0 / 1008 * rect.height()) # used to be 800
        
        self.resize(1920, 1008)
        
        self.left = int(80.0 / 1920 * self.myWidth)
        self.top = int(140.0 / 1008 * self.myHeight)
        self.width = int(1600.0 / 1920 * self.myWidth)
        self.height = int(800.0 / 1008 * self.myHeight)
            
        #print('Available: %d x %d' % (1600.0 / 1920 * self.width(), 800.0 / 1008 * self.height()))
    
        
        #self.initUI()
        
        
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
    
    
    
        
        
    
    
    
        # Create info label
        self.xLabel = QLabel("A:", self)
        self.xLabel.setFont(QFont('Calibri', 14)) 
        self.xLabel.move(20, 20 + 40 * 1)
        #self.x0Label.show()
        self.xLabel.adjustSize() 
        
        # Create input textbox
        self.xBox = QLineEdit(self)
        self.xBox.move(20, 20 + 30 * 3) # One may note that I break from my movement convention here
        self.xBox.resize(280,40)
        
        self.xBox.setStyleSheet("background-color : darkgray")
        
        
        
        
        self.x2Label = QLabel("B:", self)
        self.x2Label.setFont(QFont('Calibri', 14)) 
        self.x2Label.move(20, 20 + 40 * 5)
        #self.x0Label.show()
        self.x2Label.adjustSize() 
        
        # Create input textbox
        self.x2Box = QLineEdit(self)
        self.x2Box.move(20, 20 + 35 * 7) # One may note that I break from my movement convention here
        self.x2Box.resize(280,40)
        
        self.x2Box.setStyleSheet("background-color : darkgray")
        
        
        self.titleLabel = QLabel("Euler's Algorithm Calculator", self)
        #self.titleLabel.setWordWrap(True)
        self.titleLabel.move(550, 20)
        self.titleLabel.setFont(QFont('Times', 20)) 
        self.titleLabel.adjustSize()
        
        
        
        
        self.imageText = QLabel("Euler's Algorithm is a method to determine the greatest common divisor (GCD) of two integers.\nThe process is featured in the latter parts of Shor's Algorithm.\nThe algorithm involves performing integer and modulo division between the two numbers.\nThe first number assumes the second number's value, and the second number becomes the remainder of the two.\nThis process repeats until the remainder is 0, at which point the previous remainder is returned as the answer.\nThis can be useful in the scope of Shor's Algorithm to find the GCD of two numbers where one could be some arbitrary multiple of the other.\nThe whole process has log(n) time complexity.", self)
        #self.yOutput.resize(1000,40) // Doesn't work??? 
        self.imageText.setWordWrap(True)
        self.imageText.setFont(QFont('Times', 10)) 
        self.imageText.move(600, 20 + 40 * 4)
        self.imageText.adjustSize() 
        
         
        
        
        #--------------------------------
        
        # Output:
            
        # Create dynamic info label 
        self.yOutput = QLabel("_______________________________", self)
        self.yOutput.setFont(QFont('Calibri', 14))
        #self.yOutput.resize(1000,40) // Doesn't work??? 
        self.yOutput.setWordWrap(True)
        self.yOutput.move(20, 20 + 40 * 10)
        self.yOutput.adjustSize() 
        
            
        # self.label_2.setText(new_info) # <-- Use this
        
        
        
        
        self.yOutput.move(self.newWidth(20), self.newHeight(20 + 40 * 8))
        
        
        
        # Create a button in the window
        self.calculateButton = QPushButton('Find GCD', self)
        self.calculateButton.move(700,760)
        self.calculateButton.setGeometry(700, 760, 300, 100)
        
        # connect button to function calculate()
        self.calculateButton.clicked.connect(self.calculate)
        #self.show()
        
        self.calculateButton.setStyleSheet("background-color : darkgray")
        
        
        
        
        
        
        self.show()
        
   
    @pyqtSlot()
    def calculate(self):
        
        
        #QMessageBox.question(self, 'Message - pythonspot.com', "You typed: " + textboxValue, QMessageBox.Ok, QMessageBox.Ok)
        #QMessageBox.question(self, 'Message - TEST', "QFT: " + str(x0Val), QMessageBox.Ok, QMessageBox.Ok)
        
        
       
        
        #Call math fxn here
        A = int(self.xBox.text())
        B = int(self.x2Box.text())
        
        answer = self.EulerAlg(A, B)
            
        self.yOutput.setText("GCD: " + str(answer))






if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())