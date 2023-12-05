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
        
        # Ooooooooh boy. This is going to hurt. 
        self.xBox.move(self.newWidth(20), self.newHeight(20 + 35 * 2))
        
        
        
        
        
        
        
        
        
        
        
            
    
            
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
        
        
        self.setStyleSheet("background-color: gray;") 
  
        
        
        
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
    
    
    
        self.inputVector = []
        
    
    
    
        # Create info label
        self.xLabel = QLabel("Lorem Ipsum Dolor Sit Amet", self)
        self.xLabel.setFont(QFont('Calibri', 14)) 
        self.xLabel.move(20, 20 + 40 * 1)
        #self.x0Label.show()
        self.xLabel.adjustSize() 
        
        # Create input textbox
        self.xBox = QLineEdit(self)
        self.xBox.move(20, 20 + 35 * 2) # One may note that I break from my movement convention here
        self.xBox.resize(280,40)
        
         
        
        
        #--------------------------------
        
        # Output:
            
            
        # self.label_2.setText(new_info) # <-- Use this
        
        
        
        
        
        
        
        
        # Create a button in the window
        self.calculateButton = QPushButton('Calculate', self)
        self.calculateButton.move(20,760)
        
        # connect button to function calculate()
        self.calculateButton.clicked.connect(self.calculate)
        #self.show()
        
        
        
        
        
        
        
        
        self.show()
        
   
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
        
   



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())