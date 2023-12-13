import sys
from PyQt6 import QtCore
from PyQt6.QtWidgets import *
from functools import partial
LABELS='labels'
ADDING='adding'
SEARCH_RESULTS='search_results'
CHANGING='changing'
class Settings:
    def __init__(self) -> None:
        self.default_size=[{'default':252+2*4+2,
                            'large':864+2*8+2,
                            }, 30]
        self.size=[self.default_size[0]['default'], self.default_size[1]]
        self.one_size=21


class PushButton:
    def __init__(self, text='⊗'):
        self.button=QPushButton(text)
        self.button.setMaximumSize(21, 30)
        
    def printing(self):
        return self.button
    

class Label:
    def __init__(self, text):
        self.label=QLabel(text)

    def printing(self):
        return self.label
    

class LineEdit:
    def __init__(self, text=''):
        self.lineedit=QLineEdit(text)

    def printing(self):
        return self.lineedit
    


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.layout=QGridLayout()
        self.setContentsMargins(1, 1, 1, 1)
        self.layout.setSpacing(2)

        self.settings=Settings()

        self.layout.setDefaultPositioning(1, QtCore.Qt.Orientation.Horizontal)

        self.search_field=QLineEdit()
        self.search_field.setMinimumSize(self.settings.one_size, 0)
        self.layout.addWidget(self.search_field, 0, 0, 1, 10)

        self.add_button=QPushButton('+')
        self.add_button.setMaximumSize(self.settings.one_size, 30)
        self.layout.addWidget(self.add_button, 0, 15, 1, 1)
        self.add_button.clicked.connect(self.add_button_clicked)

        self.search_button=QPushButton('🔍︎')
        #self.search_field.foc
        self.search_button.setMinimumSize(0,0)
        self.search_button.setMaximumSize(self.settings.one_size, 30)
        self.layout.addWidget(self.search_button, 0, 14, 1, 1)
        self.search_button.clicked.connect(self.search)

        self.choose_field=QComboBox()
        self.choose_field.addItems(['All', 'russian','Ukrainian','English', 'Bulgarian'])
        self.layout.addWidget(self.choose_field, 0, 11, 1, 3)

        self.adding=False
        self.labels=[]
        self.objects={
            LABELS:[],
            ADDING:[],
            SEARCH_RESULTS:[],
            CHANGING:{},
        }
        self.set_size()
        #self.check_events()

        """self.timer = QtCore.QTimer()
        self.timer.start(2)
        self.timer.timeout.connect(self.update)"""

        widget=QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

    def createLabels(self):
        self.labels=[
                Label('Rus'),
                Label('Ukr'),
                Label('Eng'),
                Label('Bul')
            ]
        self.objects[LABELS]=self.labels
            
        """for i in range(4):
            self.layout.addWidget(self.labels[i], 1, i*6, 1, 6)"""

    def add_button_clicked(self):
        self.adding=not self.adding
        if self.adding:
            if not self.labels:
                self.createLabels()
            self.refresh_adding()
            #self.setFixedSize(893, 80)
            #self.layout.addWidget(label for label in labels, 1, (i-4)*(-3), 1, 3)
            
        else:
            self.write()

    def write(self):
        do=True
        for edit in self.adding_edits:
            if not edit.printing().text():
                do=False
        if do:
            with open('database.txt', 'r', encoding='UTF-8') as file:
                text=file.read()
            with open('database.txt', 'w', encoding='UTF-8') as file:
                file.write('$'.join(self.adding_edits[i].lineedit.text().capitalize() for i in range(4))+'\n'+text)
        self.objects[ADDING]=[]
        self.update()

    def search(self):
        self.objects[SEARCH_RESULTS]=[]
        if not self.search_field=='':
            search=self.search_field.text()
            with open('database.txt', 'r', encoding='UTF-8') as file:
                text=file.readlines()
                for i in range(len(text)):
                    if self.get_search_language()==0:
                        do=search.lower() in text[i].lower()
                    else:
                        do=search.lower() in text[i].split('$')[self.get_search_language()-1].lower()
                    if do:
                        if not self.objects[LABELS]:
                            self.createLabels()
                        line=text[i].split('$')
                        line[-1]=line[-1][:-1]
                        for j in range(len(line)):
                            line[j]=Label(line[j])
                        line.append(PushButton('✎'))
                        line.append(PushButton())
                        line[-2].button.clicked.connect(partial(self.change_button_clicked, self.get_label_n_adding()+len(self.objects[SEARCH_RESULTS])+1))
                        line[-1].button.clicked.connect(partial(self.close_button_clicked, self.get_label_n_adding()+len(self.objects[SEARCH_RESULTS])+1))
                        self.objects[SEARCH_RESULTS].append(line)

        if not self.objects[SEARCH_RESULTS]:
            line=[Label('No matching results found'), Label(''),Label(''),Label(''),Label(''),PushButton()]
            line[-1].button.clicked.connect(partial(self.close_button_clicked, self.get_label_n_adding()+1))
            self.objects[SEARCH_RESULTS].append(line)
        self.update()
    
    def update(self):
        for i in reversed(range(4, self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        
        if self.objects[SEARCH_RESULTS] or self.objects[ADDING]:
            self.createLabels()
        else:
            self.objects[LABELS]=[]

        self.style_objects()
        if self.objects[LABELS]:
            for i in range(4):
                self.layout.addWidget(self.objects[LABELS][i].label, 1, i*12, 1, 12)
        if self.objects[ADDING]:
            for i in range(len(self.objects[ADDING])):
                self.layout.addWidget(self.objects[ADDING][i].printing(), 2, i*12+(i>=4)+(i==5), 1, 12-(i>=4)*11)
        for i in range(len(self.objects[SEARCH_RESULTS])):
            for j in range(len(self.objects[SEARCH_RESULTS][i])):
                self.layout.addWidget(self.objects[SEARCH_RESULTS][i][j].printing(), self.get_line_num(i), j*12+(j>=4), 1, 12-(j>=4)*11)
            
        self.set_size()
    
    def set_size(self):
        self.settings.size[1]=int(self.settings.default_size[1]*(1+len(self.objects[LABELS])/4+len(self.objects[ADDING])/4+len(self.objects[SEARCH_RESULTS])))
        if self.settings.size[1]>self.settings.default_size[1]:
            self.settings.size[0]=self.settings.default_size[0]['large']
        else:
            self.settings.size[0]=self.settings.default_size[0]['default']
        self.setFixedSize(self.settings.size[0], 20+self.settings.size[1])
    
    def get_line_num(self, index):
        return int(len(self.objects[LABELS])/4+len(self.objects[ADDING])/4+index+1)
    
    def get_label_n_adding(self):
        return int(len(self.objects[ADDING])/4)
    
    def style_objects(self):
        for i in range(len(self.objects[LABELS])):
            self.objects[LABELS][i].label.setStyleSheet(
                "border-style: outset;"
                "border-width: 2px;"
                "border-color: blue;"
                "border-radius: 15%;"
                "font-size: 20px;"
                )
    
    def close_button_clicked(self, row):
        if row==0:
            self.objects[ADDING]=[]
            self.adding=False
        else:
            row-=1
            row-=self.get_label_n_adding()
            self.objects[SEARCH_RESULTS].pop(row)

        self.update_buttons()
        self.update()

    def change_button_clicked(self, row):
        row-=1
        row-=self.get_label_n_adding()
        if row not in self.objects[CHANGING].keys():
            self.objects[CHANGING][row]='$'.join(self.objects[SEARCH_RESULTS][row][i].printing().text() for i in range(4))+"\n"
            for i in range(4):
                self.objects[SEARCH_RESULTS][row][i]=LineEdit(self.objects[SEARCH_RESULTS][row][i].printing().text())
        else:
            new_text='$'.join(self.objects[SEARCH_RESULTS][row][i].printing().text() for i in range(4))+'\n'
            for i in range(4):
                self.objects[SEARCH_RESULTS][row][i]=Label(self.objects[SEARCH_RESULTS][row][i].printing().text())
            with open('database.txt', 'r', encoding='UTF-8') as file:
                file_text=file.readlines()
                for i in range(len(file_text)):
                    if file_text[i]==self.objects[CHANGING][row]:
                        file_text[i]=new_text
            with open('database.txt', 'w', encoding='UTF-8') as file:
                file.writelines(file_text)
            del self.objects[CHANGING][row]



        self.update()

    def update_buttons(self):
        self.update_close_buttons()
        self.update_change_buttons()

    def update_close_buttons(self):
        for key in self.objects.keys():
            if key!=LABELS:
                if key==ADDING:
                    if self.adding:
                        self.objects[key][5].button.disconnect()
                        self.objects[key][5].button.clicked.connect(partial(self.close_button_clicked, 0))
                else:
                    for i in range(len(self.objects[key])):
                        self.objects[key][i][5].button.disconnect()
                        self.objects[key][i][5].button.clicked.connect(partial(self.close_button_clicked, self.get_label_n_adding()+i+1))
    
    def update_change_buttons(self):
        for i in range(len(self.objects[SEARCH_RESULTS])):
            self.objects[SEARCH_RESULTS][i][4].button.disconnect()
            self.objects[SEARCH_RESULTS][i][4].button.clicked.connect(partial(self.close_button_clicked, self.get_label_n_adding()+i+1))

    def refresh_adding(self):
        self.adding_edits=[
                LineEdit(),
                LineEdit(),
                LineEdit(),
                LineEdit(),
                PushButton('↺'),
                PushButton(),
            ]
        self.adding_edits[-2].button.clicked.connect(self.refresh_adding)
        self.adding_edits[-1].button.clicked.connect(partial(self.close_button_clicked, 0))
        self.objects[ADDING]=self.adding_edits
        self.adding_edits[0].printing().setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.adding_edits[0].printing().setFocus()
        self.update_close_buttons()
        self.update()

    def get_search_language(self):
        return self.choose_field.currentIndex()
        

                
                
app=QApplication(sys.argv)

window=MainWindow()
window.move(0, 0)
window.show()
app.exec()
