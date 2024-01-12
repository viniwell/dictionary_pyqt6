from PyQt6.QtWidgets import *
from PyQt6 import QtCore, QtGui
import sys
from functools import partial

class Main_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        layout=QVBoxLayout()
        self.setWindowTitle('App')
        self.label=QLabel('Label')
        layout.addWidget(self.label)
        self.menu=QMenu('Search')
        self.actions=['Theme', 'Thema', 'Thematic']
        for act in self.actions:
            self.actions[self.actions.index(act)]=self.menu.addAction(act)
        connection=[action.triggered.connect(partial(self.triger_con, action)) for action in self.actions]
        layout.addWidget(self.menu)
        widget=QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.show()
        """self.t1=QtCore.QThread()
        self.t1.started.connect(self.start_menu)
        self.t1.start()"""
        #self.start_menu()
    
    
    def triger_con(self, action):
        print(action.text())

    def start_menu(self):
        #self.menu.exec(QtCore.QPoint(0, 0))
        self.menu.show()
        self.activateWindow()




app=QApplication(sys.argv)
window = Main_Window()
sys.exit(app.exec())