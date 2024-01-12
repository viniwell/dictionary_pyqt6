import sys
import os
from PyQt6 import QtCore
from PyQt6 import QtGui
from PyQt6.QtGui import QCloseEvent, QKeyEvent
from PyQt6.QtWidgets import *
from functools import partial
import json

have_file=False

for file in os.listdir('.'):
    if file=='database.json':
        have_file=True

if not have_file:
    file=open('database.json', 'w')
    json.dump([[], ['Theme', 'Українська', 'English'], ['Theme', 'Українська', 'English'], ['Unrecorded'], 'English'], file)
    file.close()

LABELS='labels'
ADDING='adding'
SEARCH_RESULTS='search_results'
CHANGING='changing'
PAGINATION='pagination'
LINES='lines'

def get_layout(list, al):
    layout=QHBoxLayout()
    for obj in list:
        layout.addWidget(obj.printing(), obj.one_size[0], alignment=al)
    return layout

class Line:
    def __init__(self, kargs, args, window):
        self.window=window
        self.objects={kargs[i]:args[i] for i in range(len(kargs))}
        self.buttons=[]
    
    def append(self, field, object):
        if field:
            self.objects[field]=object
        else:
            self.buttons.append(object)

    def get_layout(self):
        layout = QHBoxLayout()
        for index in self.objects.keys():
            if self==self.window.first_line:
                layout.addWidget(self.objects[index].printing(), self.objects[index].one_size[0], alignment=QtCore.Qt.AlignmentFlag.AlignRight)
            else:
                if index in self.window.settings.active_fields:
                    layout.addWidget(self.objects[index].printing(), self.objects[index].one_size[0], alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        for button in self.buttons:
            layout.addWidget(button.printing(), button.one_size[0], alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        return layout
    
    def text(self):
        text=[]
        for obj in self.objects.values():
            text.append(obj.text())
        text='$'.join(t for t in text)
        return text

    def get_list(self):
        return [obj.text() for obj in self.objects.values()]

class Settings:
    def __init__(self) -> None:
        self.one_size=16
        self.page=0
        self.words_per_page=12
        self.default_size=[{'default': self.one_size*23,
                            'large': self.one_size*65,
                            }, 30]
        self.one_size_vertical=self.default_size[1]-5
        self.size=[self.default_size[0]['default'], self.default_size[1]]
        self.spacing=7

        with open('database.json', 'r') as file:
            data=json.load(file)

        self.fields=data[1]
        self.active_fields=[str(num) for num in data[2]]
        self.themes=data[3]
        self.app_language=data[4]

    def set_app_language(self, index):
        self.app_language=index
        
    def set_themes(self, themes):
        self.themes=themes

class Widget:
    def __init__(self, width, height, window):
        self.one_size=[width, height]
        self.size=[width*window.settings.one_size, height*window.settings.one_size_vertical]
        self.set_size()
        self.main_window=window
    
    def printing(self):
        pass

    def set_size(self):
        self.printing().setFixedSize(self.size[0], self.size[1])
        


class PushButton(Widget):
    def __init__(self, width, height, window,text='⊗'):
        self.button=QPushButton(text)
        super().__init__(width, height, window)
        
    def printing(self):
        return self.button
    
    def text(self):
        return self.printing().text()
    

class Label(Widget):
    def __init__(self, width, height, window,text):
        self.label=QLabel(text)
        super().__init__(width, height, window)

    def printing(self):
        return self.label
    
    def text(self):
        return self.printing().text()
    
class MyQLineEdit(QLineEdit):
    def __init__(self, text, lineedit):
        super().__init__(text)
        self.lineedit=lineedit
    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key()==int(QtCore.Qt.Key.Key_S):
            if event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
                if self.lineedit.main_window.windows[1].isHidden:
                    self.lineedit.main_window.show_window(self.lineedit.main_window.windows[1])
        elif event.key()==int(QtCore.Qt.Key.Key_H):
            if event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
                self.lineedit.main_window.show_window(self.lineedit.main_window.windows[0])
        else:
            super().keyReleaseEvent(event)
        

class LineEdit(Widget):
    def __init__(self, width, height, window,text=''):
        self.lineedit=MyQLineEdit(text, self)
        self.lineedit.returnPressed.connect(self.handle_click)
        super().__init__(width, height, window)

    def printing(self):
        return self.lineedit
    
    def check(self):
        if len(str(self.lineedit.text()))==0:
            self.lineedit.setText('Unrecorded')
            return True
        else:
            return False
        
    def text(self):
        return self.printing().text()
    
    def handle_click(self):
        if self==self.main_window.search_field:
            self.main_window.search()
        elif self in self.main_window.objects[ADDING].objects.values():
            self.main_window.write()
        else:
            self.main_window.enter_pressed(self)

    def action_clicked(self, menu, index):
        self.lineedit.setText(menu.actions[index].text())
        menu.printing().setParent(None)
        del self.menu
        self.menu=None
    

class Combobox(Widget):
    def __init__(self, width, height, window,choices, index=0):
        self.combobox=QComboBox()
        self.combobox.addItems(choices)
        self.combobox.setCurrentIndex(index)
        super().__init__(width, height, window)

    def printing(self):
        return self.combobox
    
    def text(self):
        return self.printing().currentText()
    
class Checkbox(Widget):
    def __init__(self, width, height, window, status=False):
        self.checkbox=QCheckBox()
        self.checkbox.setChecked(status)
        super().__init__(width, height, window)

    def printing(self):
        return self.checkbox

    def text(self):
        return self.printing().isChecked()
    

class Menu(Widget):
    def __init__(self, width, height, window, parent, actions):
        self.menu = MyQMenu()
        self.parent=parent
        self.set_actions(actions)
        self.set_position()
        super().__init__(width, height, window)
        """t=QtCore.QThread()
        t.started.connect(self.menu.exec)
        t.start()"""
        self.menu.show()
        

    def set_actions(self, actions):
        self.actions=['']*len(actions)
        for i in range(len(actions)):
            self.actions[i]=self.menu.addAction(actions[i])
            self.actions[i].triggered.connect(partial(self.parent.action_clicked, self, i))

    def set_position(self):
        self.printing().move(QtCore.QPoint(self.parent.printing().x(), self.parent.printing().y()))

    def printing(self):
        return self.menu
    

class MyQMenu(QMenu):
    def __init__(self):
        super().__init__()
    
    def closeEvent(self, event: QCloseEvent):
        print('close menu')
        event.ignore()

    
class HelpWindow(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window=main_window
        self.setWindowIcon(QtGui.QIcon('./images/icon_dict.png'))
        label=QLabel('Hi!Glad to see you using my app! Here is step-by-step instructions for pleasant work in my app:')
        label.setStyleSheet(
            "float: top;"
            "margin-left: 5px;"
            "margin-top: 0px;"
            )
        label.setWordWrap(True)
        label.setFont(self.get_font(label))
        self.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(label)
        self.setWindowTitle('Help window')
        self.show_hide_anim=QtCore.QPropertyAnimation(self, b'geometry')
        self.show_hide_anim.setDuration(130)
        self.show_hide_anim.setEasingCurve(QtCore.QEasingCurve.Type.InBounce)
        self.show_hide_anim.setStartValue(QtCore.QRect(0, 0, 0, 0))
        self.show_hide_anim.setEndValue(QtCore.QRect(400, 200, 300, 300))
    
    def get_font(self, label):
        font=label.font()
        font.setPointSize(16)
        return font

    def showEvent(self, event) -> None:
        event.accept()
        self.show_hide_anim.setDirection(QtCore.QAbstractAnimation.Direction.Forward)
        self.show_hide_anim.start()
    
    def closeEvent(self, event):
        """Called when the user closes the settings window"""
        event.ignore()
        self.show_hide_anim.setDirection(QtCore.QAbstractAnimation.Direction.Backward)
        self.show_hide_anim.start()
        self.hide()
        self.main_window.check_windows()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Dictionary')
        self.setWindowIcon(QtGui.QIcon('./images/icon_dict.png'))

        self.layout=QVBoxLayout()
        self.setContentsMargins(1, 1, 1, 1)
        self.layout.setSpacing(2)

        self.settings=Settings()
        with open('database.json', 'r') as file:
            self.db=json.load(file)[0]

        self.extra_win=0

        self.adding=False
        self.labels=[]
        self.objects={
            LABELS:Line([], [], self),
            ADDING:Line([], [], self),
            SEARCH_RESULTS:[],
            CHANGING:{},
            PAGINATION:False,
            LINES:[]
        }
        self.update()

    def show_window(self, window):
        self.setEnabled(False)
        self.extra_win+=1
        window.show()

    def create_first_line(self, text, index):
        self.search_field=LineEdit(10, 1, self, text)
        menu=Menu(10, 1, self, self.search_field, ['baldy', 'buddy', 'asshole'])
        self.search_field.menu=menu

        self.choose_field=Combobox(3, 1, self, ['All']+[self.settings.fields[self.settings.fields.index(i)] for i in self.settings.active_fields], index)

        self.search_button=PushButton(1, 1, self, '🔍︎')
        self.search_button.printing().clicked.connect(self.search)

        self.add_button=PushButton(1, 1, self, '+')
        self.add_button.printing().clicked.connect(self.add_button_clicked)

        self.view_all_button=PushButton(3, 1, self,'View all')
        self.view_all_button.printing().clicked.connect(self.show_all)

        self.help_button=PushButton(1, 1, self, '?')

        self.settings_button=PushButton(1, 1, self, '⚙️')
        self.windows=[HelpWindow(self), SettingsWindow(self)]

        self.first_line=[self.search_field, self.search_button, self.choose_field, self.add_button, self.view_all_button, self.help_button, self.settings_button]

    def closeEvent(self, event):
        self.save_data()
        sys.exit()
    
    def save_data(self):
        with open('database.json', 'w') as file:
            json.dump([self.db, self.settings.fields, self.settings.active_fields, self.settings.themes,self.settings.app_language], file)

    def keyReleaseEvent(self, event:QtCore.QEvent):
        if event.key()==int(QtCore.Qt.Key.Key_S):
            if event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
                self.show_window(self.windows[1])
        elif event.key()==int(QtCore.Qt.Key.Key_H):
            if event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
                self.show_window(self.windows[0])
    
    def check_windows(self):
        self.extra_win-=1
        if not self.extra_win:
            self.setEnabled(True)

        self.update()

    def enter_pressed(self, object):
        for line in self.objects[SEARCH_RESULTS][self.settings.page]:
            if object in line.objects.values():
                self.change_button_clicked(line)
        
    def createLabels(self):
        labels=Line([], [], self)
        for field in range(len(self.settings.fields)):
            labels.append(self.settings.fields[field], Label(12, 1, self, self.settings.fields[field]))
        labels.buttons.append(PushButton(3, 1, self, 'Clear all'))
        labels.buttons[-1].button.clicked.connect(self.clear_all)
        self.objects[LABELS]=labels

    def add_button_clicked(self):
        self.adding=not self.adding
        if self.adding:
            if not self.objects[LABELS]:
                self.createLabels()
            self.refresh_adding()
            #self.setFixedSize(893, 80)
            #self.layout.addWidget(label for label in labels, 1, (i-4)*(-3), 1, 3)
        else:
            self.write()

    def write(self):
        count=0
        for edit in self.objects[ADDING].objects.values():
            if not isinstance(edit, Combobox):
                count+=edit.check()
        if count!=(len(self.settings.active_fields)-bool('Theme' in self.settings.active_fields)):
            new_text='$'.join(self.objects[ADDING].objects[key].text() if key in self.settings.active_fields else 'Unrecorded' for key in self.settings.fields)
            if new_text not in self.db:
                self.db.insert(0, [self.objects[ADDING].objects[key].text() if key in self.settings.active_fields else 'Unrecorded' for key in self.settings.fields])
                line=Line(self.settings.fields, [Label(12, 1, self, self.db[0][i]) for i in range(len(self.settings.fields))], self)
                for button in self.create_basic_buttons(line):
                    line.buttons.append(button)
                self.objects[LINES].insert(0, line)
                self.objects[ADDING]=Line([], [], self)
            else:
                print('already exists')
                self.adding=not self.adding
        self.update()

    def create_basic_buttons(self, line):
        buttons=[PushButton(1, 1, self, '✎'), PushButton(1, 1, self)]
        buttons[0].printing().clicked.connect(partial(self.change_button_clicked, line))
        buttons[1].printing().clicked.connect(partial(self.close_button_clicked, line))
        return buttons

    def search(self):
        if not self.search_field.text()=='':
            self.settings.page=0
            self.objects[LINES]=[]
            text=self.db
            search=self.search_field.text()
            do=0
            for i in range(len(text)):
                if self.get_search_language()==-1:
                    for j in self.settings.active_fields:
                        do+=bool(search.lower() in text[i][self.settings.fields.index(j)].lower())
                else:
                    do+=bool(search.lower() in text[i][self.get_search_language()].lower())
                if do:
                    test='.'.join(text[i][self.settings.fields.index(field)] for field in self.settings.active_fields)
                    if test.count('Unrecorded')!=len(self.settings.active_fields):
                        if not self.objects[LABELS]:
                            self.createLabels()
                        line=Line(self.settings.fields, [Label(12, 1, self, self.db[i][j]) for j in range(len(self.settings.fields))], self)
                        for button in self.create_basic_buttons(line):
                            line.append(None, button)
                        self.objects[LINES].append(line)
                    do=0
            self.check_objects()
            self.update()
    
    def update(self):
        for i in reversed(range(self.layout.count())):
            for j in reversed(range(self.layout.itemAt(i).count())):
                self.layout.itemAt(i).itemAt(j).widget().setParent(None)
            self.layout.itemAt(i).setParent(None)
        try:
            self.create_first_line(self.search_field.printing().text(), self.choose_field.printing().currentIndex())
        except Exception:
            self.create_first_line('', 0)
        self.layout.addLayout(get_layout(self.first_line, QtCore.Qt.AlignmentFlag.AlignRight))
        self.connect_buttons()
        
        if self.objects[LINES] or self.objects[ADDING].objects:
            self.createLabels()
        else:
            self.objects[LABELS]=Line([], [], self)

        self.style_objects()
        if self.objects[LABELS].objects:
            self.layout.addLayout(self.objects[LABELS].get_layout())

        if self.objects[ADDING].objects:
            self.layout.addLayout(self.objects[ADDING].get_layout())
        self.create_search_results()
        try:
            for num in range(len(self.objects[SEARCH_RESULTS][self.settings.page])):
                self.layout.addLayout(self.objects[SEARCH_RESULTS][self.settings.page][num].get_layout())
        except Exception as e:
            print(e)
            pass
        pag_layout=self.update_pagination()
        if pag_layout:
            self.layout.addLayout(pag_layout)
        self.set_size()

        widget=QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
    
    def connect_buttons(self):
        self.help_button.printing().clicked.connect(partial(self.show_window, self.windows[0]))
        self.settings_button.printing().clicked.connect(partial(self.show_window, self.windows[1]))

    def create_search_results(self):
        self.objects[SEARCH_RESULTS]=[]
        page=-1
        for i in range(len(self.objects[LINES])):
            if i%11==0:
                page+=1
                self.objects[SEARCH_RESULTS].append([])
            self.objects[SEARCH_RESULTS][page].append(self.objects[LINES][i])

    def normalize_sizes(self):
        for element in self.objects[ADDING].objects+self.objects[LABELS].objects:
            element.set_size()
        for i in range(self.objects[LINES]):
            for element in self.objects[SEARCH_RESULTS][self.settings.page][i].objects:
                element.set_size()
        for element in self.first_line.objects:
            element.set_size()

    def check_objects(self):
        if len(self.objects[LINES])==0:
            line=Line([field for field in self.settings.active_fields], [Label(12, 1, self, 'No matching results found')]+[Label(1, 1, self,'')]*(len(self.settings.active_fields)-1), self)
            line.append(None, PushButton(1, 1, self))
            line.buttons[-1].button.clicked.connect(partial(self.close_button_clicked, line))
            self.objects[LINES].append(line)

    def set_size(self):
        if self.objects[SEARCH_RESULTS]:
            self.settings.size[1]=int(self.settings.default_size[1]*(1+bool(len(self.objects[LABELS].objects))+bool(len(self.objects[ADDING].objects))+len(self.objects[SEARCH_RESULTS][self.settings.page])+self.objects[PAGINATION]))
        else:
            self.settings.size[1]=int(self.settings.default_size[1]*(1+bool(len(self.objects[LABELS].objects))+bool(len(self.objects[ADDING].objects))))
        if self.settings.size[1]>self.settings.default_size[1]*2:
            self.settings.size[0]=self.settings.one_size*(12*len(self.settings.active_fields)+3)+self.settings.spacing*(len(self.settings.active_fields)+4)
        else:
            self.settings.size[0]=self.settings.default_size[0]['default']
        self.setFixedSize(self.settings.size[0], self.settings.size[1]+10)
    
    def style_objects(self):
        for i in self.settings.active_fields:
            if i in self.objects[LABELS].objects.keys():
                self.objects[LABELS].objects[i].label.setStyleSheet(
                    "border-style: outset;"
                    "border-width: 2px;"
                    "border-color: blue;"
                    "border-radius: 25%;"
                    "font-size: 20px;"
                    )
        
    def close_button_clicked(self, line):
        if line not in self.objects[LINES]:
            self.objects[ADDING]=Line([], [], self)
            self.adding=False
        else:
            self.objects[LINES].remove(line)
        self.update()

    def change_button_clicked(self, line):
        index=self.objects[LINES].index(line)
        if line not in self.objects[CHANGING].keys():
            #self.objects[CHANGING][line]='$'.join(self.objects[SEARCH_RESULTS][self.settings.page][index].objects[i].printing().text() for i in range(5))+"\n"
            self.objects[CHANGING][line]=line.get_list()
            for field in self.settings.fields:
                if field!='Theme':
                    self.objects[LINES][index].objects[field]=LineEdit(12, 1, self, self.objects[LINES][index].objects[field].printing().text())
                else:
                    self.objects[LINES][index].objects[field]=Combobox(12, 1, self, self.settings.themes)
        else:
            self.check_line(line)
            new_line=line.get_list()
            if new_line.count('Unrecorded')==len(self.settings.fields):
                self.db.remove(self.objects[CHANGING][line])
                self.objects[LINES].remove(line)
            else:
                for field in self.settings.fields:
                    line.objects[field]=Label(12, 1, self, line.objects[field].text())
                self.db[self.db.index(self.objects[CHANGING][line])]=new_line
            del self.objects[CHANGING][line]
        self.update()

    def check_line(self, line):
        for object in line.objects.values():
            if isinstance(object, LineEdit):
                object.check()

    def refresh_adding(self):
        adding_edits=Line([], [], self)
        for i in self.settings.fields:
            adding_edits.append(i, Combobox(12, 1, self, self.settings.themes) if i=='Theme' else LineEdit(12, 1, self))
        adding_edits.append(None, PushButton(1, 1, self,'↺'))
        adding_edits.append(None, PushButton(1, 1, self))
        adding_edits.buttons[-2].button.clicked.connect(self.refresh_adding)
        adding_edits.buttons[-1].button.clicked.connect(partial(self.close_button_clicked, 0))
        self.objects[ADDING]=adding_edits
        self.update()

    def get_search_language(self):
        text=self.choose_field.printing().currentText()
        feedback=False
        for field in self.settings.fields:
            if field==text:
                feedback=True
                return self.settings.fields.index(field)
        if not feedback:
            return -1
    
    def update_pagination(self):
        if len(self.objects[SEARCH_RESULTS])>1:
            layout=QHBoxLayout()
            self.objects[PAGINATION]=True
            if self.settings.page!=0:
                prev_button=PushButton(1, 1, self, '←')
                prev_button.button.clicked.connect(partial(self.update_page, -1))
                layout.addWidget(prev_button.printing(), alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
            info_tablo=Label(2, 1, self, f'{self.settings.page+1} of {len(self.objects[SEARCH_RESULTS])}')
            layout.addWidget(info_tablo.printing(), alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
            if self.settings.page!=len(self.objects[SEARCH_RESULTS])-1:
                next_button=PushButton(1, 1, self, '→')
                next_button.button.clicked.connect(partial(self.update_page, 1))
                layout.addWidget(next_button.printing(), alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
            self.set_size()
            return layout
        else:
            self.objects[PAGINATION] = False

    def update_page(self, k):
        self.settings.page+=k
        self.update()

    def large(self):
        return self.objects[LABELS] or self.objects[ADDING] or self.objects[SEARCH_RESULTS][self.settings.page]
    
    def show_all(self):
        self.objects[LINES]=[]
        for i in range(len(self.db)):
            line=Line([t for t in self.settings.fields], [Label(12, 1, self, t) for t in self.db[i]], self)
            for button in self.create_basic_buttons(line):
                line.append(None, button)
            self.objects[LINES].append(line)
        self.check_objects()
        self.update()

    def clear_all(self):
        self.settings.page=0
        self.objects[LINES]=[]
        self.update()


class SettingsWindow(QMainWindow):
    def __init__(self, main_window:MainWindow):
        super().__init__()
        self.setWindowTitle('Settings')
        self.setGeometry(400, 200, 500, 500)
        self.setFixedSize(500, 500)
        self.setWindowIcon(QtGui.QIcon('./images/icon_dict.png'))
        # Variables
        self.main_window=main_window
        self.settings=self.main_window.settings
        self.modes=['App language', 'Themes', 'Fields']
        self.themes=self.settings.themes
        self.themes_objects=[]
        self.fields_objects=[]
        self.mainbar_scroll=0
        
        self.update()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.save()
        self.main_window.check_windows()
    
    def update(self):
        try:
            self.mainbar_scroll=self.mainbar_scrollarea.verticalScrollBar().value()
        except Exception:
            pass
        self.main_layout=QHBoxLayout()
        self.create_sidebar()
        self.create_mainbar()
        self.mainbar_scrollarea.verticalScrollBar().setValue(self.mainbar_scroll)

        self.main_layout.addLayout(self.sidebar_layout, 1)
        self.main_layout.addWidget(self.mainbar_scrollarea, 6)

        widget=QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)
    
    def create_sidebar(self):
        self.sidebar_layout=QVBoxLayout()
        for mode in self.modes:
            button=PushButton(5, 1, self.main_window, mode)
            button.printing().clicked.connect(partial(self.change_index, self.modes.index(mode)))
            self.sidebar_layout.addWidget(button.printing())

    def change_index(self, index):
        self.mainbar_scrollarea.verticalScrollBar().setValue(self.headers[index].printing().y())

    def save(self):
        self.main_window.settings.app_language=self.language_choice_combobox.printing().currentText()
        self.main_window.settings.themes=[line[0].text() for line in self.themes_objects[:-1]]
        for line in self.main_window.objects[LINES]:
                for obj in line.objects.values():
                    if isinstance(obj, Combobox):
                        obj.combobox.clear()
                        obj.combobox.addItems(self.settings.themes)
        self.save_fields()

    def save_fields(self):
        self.settings.active_fields=[]
        new_fields=[line[1].text() for line in self.fields_objects[:-1] if isinstance(line[1], Label)]
        self.settings.active_fields=[line[1].text() for line in self.fields_objects[:-1] if line[0].printing().isChecked() and isinstance(line[1], Label)]
        for line in self.main_window.objects[LINES]:
            line.objects={field:(line.objects[field] if field in line.objects.keys() else ((Label(12, 1, self, 'Unrecorded') if isinstance(line.objects[list(line.objects.keys())[0]], Label) else ((Combobox(12, 1, self, self.settings.themes) if field=='Theme' else LineEdit(12, 1, self, 'Unrecorded')))))) for field in new_fields}
        if len(self.main_window.objects[ADDING].objects):
            self.main_window.objects[ADDING].objects={field:(self.main_window.objects[ADDING].objects[field] if field in self.main_window.objects[ADDING].objects.keys() else ((Label(12, 1, self, 'Unrecorded') if isinstance(self.main_window.objects[ADDING].objects[list(self.main_window.objects[ADDING].objects.keys())[0]], Label) else ((Combobox(12, 1, self, self.settings.themes) if field=='Theme' else LineEdit(12, 1, self, 'Unrecorded')))))) for field in new_fields}
        for line in self.main_window.objects[CHANGING].keys():
            self.main_window.objects[CHANGING][line]=line.get_list()
        self.settings.fields=new_fields

    def create_mainbar(self):
        self.headers=[]
        mainbar_layout=QVBoxLayout()

        language_choice_layout=QVBoxLayout()
        self.headers.append(Label(8, 2, self.main_window, self.modes[0]))
        language_choice_layout.addWidget(self.headers[0].printing(), alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.language_choice_combobox=Combobox(9, 2, self.main_window, ['English', 'Українська', 'Deutshe'])
        language_choice_layout.addWidget(self.language_choice_combobox.printing())
        mainbar_layout.addLayout(language_choice_layout)

        themes_overall_layout=QVBoxLayout()
        self.headers.append(Label(8, 2, self.main_window, self.modes[1]))
        themes_overall_layout.addWidget(self.headers[1].printing(), alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        themes_scrollarea=QScrollArea()
        themes_scrollarea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        themes_scrollarea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        themes_scrollarea.setWidgetResizable(True)
        themes_scrollarea.setFixedSize(300,250)
        themes_layout=QVBoxLayout()
        self.create_themes_objects()
        for line in self.themes_objects:
            line_layout=QHBoxLayout()
            for object in line:
                line_layout.addWidget(object.printing(), alignment=QtCore.Qt.AlignmentFlag.AlignRight if isinstance(object, PushButton) else QtCore.Qt.AlignmentFlag.AlignLeft)
            themes_layout.addLayout(line_layout)
        themes_groupbox=QGroupBox()
        themes_groupbox.setLayout(themes_layout)
        themes_scrollarea.setWidget(themes_groupbox)
        if themes_scrollarea.verticalScrollBar():
            themes_scrollarea.verticalScrollBar().setValue(self.themes_objects[-1][0].printing().y())
        themes_overall_layout.addWidget(themes_scrollarea)
        mainbar_layout.addLayout(themes_overall_layout)

        fields_overall_layout=QVBoxLayout()
        self.headers.append(Label(8, 2, self.main_window, self.modes[2]))
        fields_overall_layout.addWidget(self.headers[2].printing(), alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        fields_scrollarea=QScrollArea()
        fields_scrollarea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        fields_scrollarea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        fields_scrollarea.setWidgetResizable(True)
        fields_scrollarea.setFixedSize(300,250)
        fields_layout=QVBoxLayout()
        self.create_fields_objects()
        for line in self.fields_objects:
            line_layout=QHBoxLayout()
            for object in line:
                line_layout.addWidget(object.printing(), alignment=QtCore.Qt.AlignmentFlag.AlignRight if isinstance(object, PushButton) else QtCore.Qt.AlignmentFlag.AlignLeft)
            fields_layout.addLayout(line_layout)
        fields_groupbox=QGroupBox()
        fields_groupbox.setLayout(fields_layout)
        fields_scrollarea.setWidget(fields_groupbox)
        fields_overall_layout.addWidget(fields_scrollarea)
        mainbar_layout.addLayout(fields_overall_layout)

        self.mainbar_scrollarea=QScrollArea()
        self.mainbar_scrollarea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.mainbar_scrollarea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.mainbar_scrollarea.setWidgetResizable(True)
        self.mainbar_scrollarea.setFixedSize(350,500)
        mainbar_groupbox=QGroupBox()
        mainbar_groupbox.setLayout(mainbar_layout)
        self.mainbar_scrollarea.setWidget(mainbar_groupbox)


    def create_fields_objects(self):
        if not self.fields_objects:
            for field in self.settings.fields:
                if field!='Theme':
                    line=[Checkbox(1, 1, self.main_window, True if field in self.settings.active_fields else False), Label(6, 1, self.main_window, field), PushButton(1, 1, self.main_window, '✎'), PushButton(1, 1, self.main_window, '🗑')]
                    line[-1].printing().clicked.connect(partial(self.delete_field, line))
                    line[-2].printing().clicked.connect(partial(self.change_field, line))
                else:
                    line=[Checkbox(1, 1, self.main_window, True if field in self.settings.active_fields else False), Label(6, 1, self.main_window, field)]
                line[0].printing().clicked.connect(partial(self.fields_checkbox_clicked, line))
                self.fields_objects.append(line)
            self.fields_objects.append(self.create_adding_field_line())
    
    def fields_checkbox_clicked(self, line):
        index=self.fields_objects.index(line)
        self.fields_objects[index][0].printing().setChecked(not line[0].printing().isChecked())
        if not self.fields_objects[index][0].printing().isChecked():
            if self.get_active_fields_amount()<=4:
                self.fields_objects[index][0].printing().setChecked(True)
            else:
                for i in range(len(self.fields_objects[:-1])):
                    if self.fields_objects[i][0].printing().isChecked() and i!=index:
                        self.fields_objects[i][0].printing().setChecked(False)
                        break
                self.fields_objects[index][0].printing().setChecked(True)
        else:
            if self.get_active_fields_amount()==1:
                print('You have only 1 field left')
            else:
                self.fields_objects[index][0].printing().setChecked(False)
        self.update()
    
    def get_active_fields_amount(self):
        ans=0
        for line in self.fields_objects[:-1]:
            if line[0].printing().isChecked():
                ans+=1
        return ans

    def create_adding_field_line(self):
        line=[LineEdit(6, 1, self.main_window), PushButton(1, 1, self.main_window, '+')]
        line[-1].printing().clicked.connect(self.add_field)
        return line
    
    def add_field(self):
        if self.fields_objects[-1][0].text() and self.fields_objects[-1][0].text() not in self.get_fields_list():
            line=[Checkbox(1, 1, self.main_window), Label(6, 1, self.main_window, self.fields_objects[-1][0].text()), PushButton(1, 1, self.main_window, '✎'), PushButton(1, 1, self.main_window, '🗑')]
            line[-1].printing().clicked.connect(partial(self.delete_field, line))
            line[-2].printing().clicked.connect(partial(self.change_field, line))
            line[0].printing().clicked.connect(partial(self.fields_checkbox_clicked, line))
            self.fields_objects.pop(-1)
            self.fields_objects.append(line)
            self.fields_objects.append(self.create_adding_field_line())
            self.main_window.db=[line+['Unrecorded'] for line in self.main_window.db.copy()]
            self.update()
        else:
            print('Error')
    
    def get_fields_list(self, index=-1):
        if index!=-1:
            return [item[1].text() for item in self.fields_objects[:-1] if self.fields_objects.index(item)!=index]
        else:
            return [item[1].text() for item in self.fields_objects[:-1]]
        
    def delete_field(self, line):
        if len(self.fields_objects)>3:
            index=self.fields_objects.index(line)
            delete=[self.main_window.db[i].pop(index) for i in range(len(self.main_window.db))]
            self.fields_objects.remove(line)
            self.update()
        else:
            print('You have a few fields')
    
    def change_field(self, line):
        index=self.fields_objects.index(line)
        if isinstance(line[1], Label):
            self.fields_objects[index][1]=LineEdit(6, 1, self.main_window, line[1].text())
        else:
            if line[1].text() and line[1].text() not in self.get_fields_list(index):
                self.fields_objects[index][1]=Label(6, 1, self.main_window, line[1].text())
            else:
                print('error')
        self.update()

    def create_themes_objects(self):
        if not self.themes_objects:
            for theme in self.themes:
                line=[Label(6, 1, self.main_window, theme), PushButton(1, 1, self.main_window, '✎'), PushButton(1, 1, self.main_window, '🗑')]
                line[1].printing().clicked.connect(partial(self.change_theme, line))
                line[2].printing().clicked.connect(partial(self.delete_theme, line))
                self.themes_objects.append(line)
            self.themes_objects.append(self.create_adding_theme_line())
        else:
            pass
    
    def create_adding_theme_line(self):
        line=[LineEdit(6, 1, self.main_window), PushButton(1, 1, self.main_window, '+')]
        line[1].printing().clicked.connect(self.add_theme)
        return line
        
    def change_theme(self, line):
        index=self.themes_objects.index(line)
        if isinstance(self.themes_objects[index][0], Label):
            self.themes_objects[index][0]=LineEdit(6, 1, self.main_window, self.themes_objects[index][0].text())
        else:
            if self.themes_objects[index][0].text() and self.themes_objects[index][0].text() not in self.get_themes_list(index):
                self.themes_objects[index][0]=Label(6, 1, self.main_window, self.themes_objects[index][0].text())
            else:
                print('error')
        self.update()

    def get_themes_list(self, index=-1):
        if index!=-1:
            return [item[0].text() for item in self.themes_objects[:-1] if self.themes_objects.index(item)!=index]
        else:
            return [item[0].text() for item in self.themes_objects[:-1]]


    def delete_theme(self, line):
        index=self.themes_objects.index(line)
        if len(self.themes_objects)>2:
            self.themes_objects.pop(index)
            self.update()
        else:
            print('only one left')

    def add_theme(self):
        if self.themes_objects[-1][0].text() and self.themes_objects[-1][0].text() not in self.get_themes_list():
            line=[Label(6, 1, self.main_window, self.themes_objects[-1][0].text()), PushButton(1, 1, self.main_window, '✎'), PushButton(1, 1, self.main_window, '🗑')]
            line[1].printing().clicked.connect(partial(self.change_theme, line))
            line[2].printing().clicked.connect(partial(self.delete_theme, line))
            self.themes_objects.pop(-1)
            self.themes_objects.append(line)
            self.themes_objects.append(self.create_adding_theme_line())
        self.update()

        



                
                
app=QApplication(sys.argv)

window=MainWindow()
window.move(0, 0)
window.show()
sys.exit(app.exec())
