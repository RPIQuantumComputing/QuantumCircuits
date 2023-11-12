# -*- coding: utf-8 -*-
"""
Seth Watabe
11/10/2023
A login page for the student/educator page of Quantum Circuits
"""




import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import pyqtSlot, Qt
import math

class App(QMainWindow):
    
    
    
    
    
            
    # GUI Initialization 
    def __init__(self):
        super().__init__()
        
        
        
        self.title = 'Login Page'
        
        
        self.setStyleSheet("background-color: gray;") 
  
        
        
        screen = self.screen()
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
    

        
    
    
    
        # Create info label
        self.xLabel = QLabel("Enter your username:", self)
        self.xLabel.setFont(QFont('Calibri', 14)) 
        self.xLabel.move(20, 20 + 40 * 1)
        #self.x0Label.show()
        self.xLabel.adjustSize() 
        
        # Create input textbox
        self.uBox = QLineEdit(self)
        self.uBox.move(20, 20 + 35 * 2) # One may note that I break from my movement convention here
        self.uBox.resize(280,40)
        
        
        # Create info label
        self.xLabel = QLabel("Enter your password:", self)
        self.xLabel.setFont(QFont('Calibri', 14)) 
        self.xLabel.move(20, 20 + 45 * 3)
        #self.x0Label.show()
        self.xLabel.adjustSize() 
        
        # Create input textbox
        self.uBox = QLineEdit(self)
        self.uBox.move(20, 20 + 35 * 5) # One may note that I break from my movement convention here
        self.uBox.resize(280,40)
        
        
        
        
        #--------------------------------
    
        
        self.show()
        
        
    # GUI Button Functions
    


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())