from PyQt6.QtWidgets import *
from  PyQt6 import QtCore
import sys
from functools import partial

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.layout=QVBoxLayout()
        self.labels=[QLabel('HI'), QLineEdit('Bye'), QPushButton('Press me')]
        [self.layout.addWidget(w) for w in self.labels]
        self.labels[-1].clicked.connect(self.change)
        self.set_cw()
        self.show()
    
    def set_cw(self):
        w=QWidget()
        w.setLayout(self.layout)
        self.setCentralWidget(w)
    
    def change(self):
        for w in self.labels[:2]:
            w.setText(w.text()*2)
        
if __name__=="__main__":
    app = QApplication([])
    window = MainWindow()
    sys.exit(app.exec())
