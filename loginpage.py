# -*- coding: utf-8 -*-
"""
Seth Watabe
11/10/2023
A login page for the student/educator page of Quantum Circuits
"""


"""
TO-DO: 
    
    Hash the password
    Flesh out the invalidPassword() checker 
    


"""



import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import pyqtSlot, Qt
from hashlib import sha256

def invalidUsername(username):
    if(len(username) == 0):
        return True
    
    if(username.find(" ") != -1):
        return True
    
def invalidPassword(password):
    if(len(password) == 0):
        return True
    
    if(password.find(" ") != -1):
        return True
    
    

class App(QMainWindow):
    
    
    # These are nearly global, but I do santize them every time they are used
    username = ""
    password = ""
    
    
        
    
    
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Return: 
            self.enterBoxes()
        
    
    def newWidth(self, num):
        return int((num + 0.0) / self.width * (self.frameGeometry().width() + 0.0))
    
    def newHeight(self, num):
        return int((num + 0.0) / self.height * (self.frameGeometry().height() + 0.0))
    
    def resizeEvent(self, event):
        
        #dynamic resizing
        self.uLabel.move(self.newWidth(650), self.newHeight(220 + 25 * 1))
        self.uBox.move(self.newWidth(650), self.newHeight(220 + 30 * 2))
        
        self.pLabel.move(self.newWidth(650), self.newHeight(220 + 45 * 3))
        self.pBox.move(self.newWidth(650), self.newHeight(220 + 35 * 5))
        
        self.updateLabel.move(self.newWidth(650), self.newHeight(220 + 45 * 6))
            
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
        self.uLabel = QLabel("Enter your username:", self)
        self.uLabel.setFont(QFont('Calibri', 14)) 
        self.uLabel.move(650, 220 + 25 * 1)
        self.uLabel.adjustSize() 
        
        # Create input textbox
        self.uBox = QLineEdit(self)
        self.uBox.move(650, 220 + 30 * 2)
        self.uBox.resize(280,40)
        
        
        # Create info label
        self.pLabel = QLabel("Enter your password:", self)
        self.pLabel.setFont(QFont('Calibri', 14)) 
        self.pLabel.move(650, 220 + 45 * 3)
        self.pLabel.adjustSize() 
        
        # Create input textbox
        self.pBox = QLineEdit(self)
        self.pBox.move(650, 220 + 35 * 5) 
        self.pBox.resize(280,40)
        
        
        # Status update label
        self.updateLabel = QLabel("", self)
        self.updateLabel.setFont(QFont('Calibri', 14)) 
        self.updateLabel.move(650, 220 + 45 * 6)
        self.updateLabel.adjustSize() 
        
        
        
        
        #--------------------------------
    
        
        self.show()
        
        
    # GUI Button Functions
    @pyqtSlot()
    def enterBoxes(self): 
        username = self.uBox.text().strip()
        print(username)
        
        # Plaintext. Do not let this password get exposed outside of this scope
        insecurePassword = self.pBox.text().strip()
        
        # Hashes the given password to be checked against whatever database we're using. 
        password = sha256(insecurePassword.encode('utf-8')).hexdigest()
        print(password)
        
        
        
        
        self.uBox.clear()
        self.pBox.clear()
    
    
        if(invalidUsername(username)):
            # It's ambiguous on purpose, to dissuade brute force
            print("bad username or password")
            # Sanitize the username and password variables
            username = ""
            password = ""
            self.updateLabel.setText("Invalid username or password.")
            self.updateLabel.adjustSize() 
            return False
        elif(invalidPassword(insecurePassword)):
            print("bad username or password")
            username = ""
            password = ""
            self.updateLabel.setText("Invalid username or password.")
            self.updateLabel.adjustSize() 
            return False
        else:
            insecurePassword = ""
            # This doesn't mean the login was a success, just that the information is valid. 
            
            self.updateLabel.setText("Success!")
            self.updateLabel.adjustSize() 
            
        
            
            
            
        #insert the username/password checker and login functions here. 
            
        
        return True
        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())