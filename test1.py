import sys
import os
from PyQt6 import QtCore
from PyQt6.QtWidgets import *
from functools import partial

class HelpWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(200, 300)
        label=QLabel('Hi!Glad to see you using my app! Here is step-by-step instructions for pleasant work in my app:')
        label.setFont(self.get_font(label))
        label.move(0, 0)
        self.setCentralWidget(label)
        self.setWindowTitle('Help window')
    
    def get_font(self, label):
        font=label.font()
        font.setPointSize(20)
        return font
    

app=QApplication(sys.argv)

window=HelpWindow()
window.move(0, 0)
window.show()
window2=HelpWindow()
window2.move(0, 0)
window2.show()
sys.exit(app.exec())
