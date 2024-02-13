import sys
import os
from PyQt6 import QtCore
from PyQt6 import QtGui
from PyQt6.QtCore import QObject
from PyQt6.QtGui import QCloseEvent, QContextMenuEvent, QKeyEvent
from PyQt6.QtWidgets import *
from functools import partial
import json
import ctypes
from numba import jit

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
        layout.addWidget(obj.printing(), alignment=al)
    return layout

def widget_by_layout(layout):
    w=QWidget()
    w.setLayout(layout)
    w.setStyleSheet("""
        margin-top: 1px;
""")
    return w

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
                    if index=='Theme':
                        if isinstance(self.objects[index], LineEdit):
                            self.objects[index].theme=True
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
    def __init__(self, main_window) -> None:
        self.main_window=main_window
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

        self.main_window.db=data[0]
        self.fields=data[1]
        self.active_fields=[str(num) for num in data[2]]
        self.app_language=data[4]

    def set_app_language(self, index):
        self.app_language=index
        
    def set_themes(self, themes):
        self.themes=themes

    @property
    def themes(self):
        themes=[]
        for line in self.main_window.db:
            try:
                themes.append(line[0])
            except:
                pass
        return list(set(themes)) 
    

class Widget:
    def __init__(self, width, height, window):
        self.one_size=[width, height]
        self.size=[width*window.settings.one_size, height*window.settings.one_size_vertical]
        self.set_size()
        self.main_window=window
        #self.printing().setParent(self.main_window)
    
    def printing(self):
        pass

    def set_size(self):
        self.printing().setFixedSize(self.size[0], self.size[1])
    
    def contextMenuEvent(self, event: QContextMenuEvent, time=None):
        try:
            self.message.hide()
        except:
            pass
        self.message = QMenu(self.main_window)
        adding = [self.message.addAction(act) for act in self.messages]
        connection = [act.triggered.connect(partial(self.delete_menu, self.message)) for act in self.message.actions()]
        if time:
            timer=QtCore.QTimer(self.message)
            timer.timeout.connect(partial(self.delete_menu, self.message))
            timer.start(time)
        self.message.show()
        self.message.move(event)
        self.messages=[]

    def delete_menu(self, menu):
        try:
            menu.close()
        except:
            pass
        self.messages=[]

    def set_image(self, path):
        image=QtGui.QImage(path)
        self.printing().setIcon(QtGui.QIcon(QtGui.QPixmap(image)))
        

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
        self.parent=lineedit
        self.textChanged.connect(self.textchange)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key()==int(QtCore.Qt.Key.Key_S):
            if event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
                if self.parent.main_window.windows[1].isHidden:
                    self.parent.main_window.show_window(self.parent.main_window.windows[1])
        elif event.key()==int(QtCore.Qt.Key.Key_H):
            if event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
                self.parent.main_window.show_window(self.parent.main_window.windows[0])
        else:
            super().keyReleaseEvent(event)

    def textchange(self):
        if self.parent.theme:
            if len(self.text())!=0:
                t=self.parent.main_window.settings.themes
                variants=[theme for theme in t if self.text().lower() in theme.lower() and self.text().lower()!=theme.lower()]
                try:
                    variants=variants[:5]
                except:
                    pass
                """if variants:
                    if not self.parent.menu:
                        self.parent.menu=MenuWindow(self.parent, variants)
                    else:
                        self.parent.menu.set_objects(variants)
                else:
                    if self.parent.menu:
                        self.parent.menu.set_objects(variants)"""
                menu=QMenu(self.parent.printing())
                [menu.addAction(act) for act in variants]
                [act.triggered.connect(partial(self.setText, act.text())) for act in menu.actions()]
                #menu.move(QtCore.QPoint(self.parent.printing().x()-7, self.parent.printing().y()+2*self.parent.printing().height()))
                menu.move(self.parent.printing().rect().bottomLeft())
                menu.show()
                app.setActiveWindow(self.parent.main_window)
                self.parent.main_window.activateWindow()
                print(self.parent.main_window.isActiveWindow(), menu.isActiveWindow())
                
                self.activateWindow()
                self.setFocus(QtCore.Qt.FocusReason.PopupFocusReason)

    
    def editingfinished(self):
        try:
            self.parent.menu.close()
            del self.parent.menu
            self.parent.menu=None
        except:
            pass
        

class LineEdit(Widget):
    def __init__(self, width, height, window,text=''):
        self.lineedit=MyQLineEdit(text, self)
        self.lineedit.returnPressed.connect(self.handle_click)
        self.theme=False
        self.menu=None
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
    

class MenuWindow(QMainWindow):
    def __init__(self, parent, objects):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.layout=QVBoxLayout()
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        self.parent=parent
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.set_objects(objects)
        self.set_position()
        self.setStyleSheet("""
            QPushButton{
                           margin-left: 0px;
                           margin-top: 0px;
            }
            QMainWindow{
                           padding-left: 0px;
                           border-radius: 45%
            }
        """)
        self.set_size()
        self.set_central_w()
        self.show()

    def set_position(self):
        self.move(QtCore.QPoint(self.parent.printing().x()-7, self.parent.printing().y()+2*self.parent.printing().height()))

    def set_size(self):
        self.setFixedSize(self.parent.printing().width(), len(self.objects)*self.parent.main_window.settings.default_size[1])
    
    def set_objects(self, objects):
        if objects:
            self.layout=QVBoxLayout()
            self.objects=['']*len(objects)
            for i in range(len(objects)):
                self.objects[i]=PushButton(12, 1, self.parent.main_window, objects[i])
                self.objects[i].printing().clicked.connect(partial(self.action_clicked,i))
                self.layout.addWidget(self.objects[i].printing())
                self.set_size()
                self.set_central_w()
        else:
            self.parent.menu=None
            self.close()
            del self

    def action_clicked(self, index):
        self.parent.printing().setText(self.objects[index].printing().text())
        self.parent.menu=None
        self.close()
        del self

    def set_central_w(self):
        widget=QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

    
class HelpWindow:
    def __init__(self, main_window):
        self.main_window=main_window
        label=QLabel('Hi!Glad to see you using my app! Here is step-by-step instructions for pleasant work in my app:')
        label.setStyleSheet(
            "float: top;"
            "margin-left: 5px;"
            "margin-top: 0px;"
            )
        label.setWordWrap(True)
        label.setFont(self.get_font(label))

        self.layout=QVBoxLayout()
        self.layout.addWidget(label, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
    
    def get_font(self, label):
        font=label.font()
        font.setPointSize(16)
        return font
    

class MainWindow(QMainWindow):
    MENU_ICONS={
        'Home':'./images/home.png',
        'Settings':'./images/settings.png',
        'Help':'/images/help.png',
        'Exit':'/images/exit.png',
    }
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Dictionary')
        self.setWindowIcon(QtGui.QIcon('./images/icon_dict.png'))

        self.layout=QVBoxLayout()
        self.setContentsMargins(1, 1, 1, 1)
        self.layout.setSpacing(1)

        self.settings=Settings(self)

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
        self.init()
    
    def home_mode_layout(self):
        main_part=QVBoxLayout()

        main_part.addWidget(widget_by_layout(get_layout(self.first_line, QtCore.Qt.AlignmentFlag.AlignRight)), alignment=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignRight)
        
        if self.objects[LINES] or self.objects[ADDING].objects:
            self.createLabels()
        else:
            self.objects[LABELS]=Line([], [], self)

        if self.objects[LABELS].objects:
            main_part.addWidget(widget_by_layout(self.objects[LABELS].get_layout()), alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTop)

        if self.objects[ADDING].objects:
            main_part.addWidget(widget_by_layout(self.objects[ADDING].get_layout()), alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTop)

        self.create_search_results()
        try:
            for num in range(len(self.objects[SEARCH_RESULTS][self.settings.page])):
                w=widget_by_layout(self.objects[SEARCH_RESULTS][self.settings.page][num].get_layout())
                w.mouseDoubleClickEvent=partial(self.change_button_clicked, line=self.objects[SEARCH_RESULTS][self.settings.page][num])
                w.mouseReleaseEvent=partial(self.line_clicked, line=self.objects[SEARCH_RESULTS][self.settings.page][num])
                main_part.addWidget(w, alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTop)
        except:
            pass

        pag_layout=self.update_pagination()
        if pag_layout:
            main_part.addLayout(pag_layout)
        main_part.setSpacing(0)
        main_part.setContentsMargins(1, 0, 1, 0)
        
        return main_part
    
    def line_clicked(self, event, line):
        if event.button()==QtCore.Qt.MouseButton.RightButton:
            self.createChoiceMenu(event, line)

    def createChoiceMenu(self, event, line):
        menu=QMenu(self)
        if line==self.objects[ADDING]:
            menu.addAction('Add', self.add_button_clicked)
        if line in self.objects[CHANGING].keys():
            menu.addAction('Save changes', partial(self.change_button_clicked, line=line))
        else:
            menu.addAction('Change', partial(self.change_button_clicked, line=line))

        menu.addAction('Delete', partial(self.delete_line, line))
        
        menu.addAction('Close line', partial(self.close_button_clicked, line))
        menu.exec(event.globalPosition().toPoint())

    def delete_line(self, line):
        if line.get_list() in self.db:
            self.db.remove(line.get_list())
            self.objects[LINES].remove(line)
        self.update()


    def init(self):
        self.help_window=HelpWindow(self)
        self.settings_window=SettingsWindow(self)

        self.create_first_line()

        self.sw=QStackedWidget()
        for layout in [self.home_mode_layout(), self.settings_window.layout, self.help_window.layout]:
            self.sw.addWidget(widget_by_layout(layout))

        self.layout=QHBoxLayout()

        menu_layout=QVBoxLayout()
        menu_layout.addWidget(self.menu)
        gb=QGroupBox()
        gb.setLayout(menu_layout)
        gb.setStyleSheet("""border: 0px; margin-left:1px; margin-right: 1px; margin-bottom: 3px;""")
        self.layout.addWidget(gb, alignment=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)

        line=QWidget()
        line.setStyleSheet("""border-left: 1px solid grey;""")
        line.setFixedSize(1, self.menu.height()+2 if self.menu.height()>=self.sw.currentWidget().sizeHint().height() else self.sw.currentWidget().sizeHint().height()+2)
        self.layout.addWidget(line, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        self.sw.setFixedSize(self.sw.currentWidget().sizeHint())
        self.sw.setStyleSheet("""
            margin-top: 0px;
""")
        self.layout.addWidget(self.sw, alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTop)

        self.update()
        self.set_cw()

    def create_first_line(self, text='', index=0, toggled=False):
        self.create_menu(toggled)

        self.search_field=LineEdit(10, 1, self, text)

        self.choose_field=Combobox(3, 1, self, ['All']+[self.settings.fields[self.settings.fields.index(i)] for i in self.settings.active_fields], index)

        self.search_button=PushButton(1, 1, self, '🔍︎')
        self.search_button.printing().clicked.connect(self.search)

        self.add_button=PushButton(1, 1, self, '+')
        self.add_button.printing().clicked.connect(self.add_button_clicked)

        self.view_all_button=PushButton(3, 1, self,'View all')
        self.view_all_button.printing().clicked.connect(self.show_all)

        self.first_line=[self.search_field, self.search_button, self.choose_field, self.add_button, self.view_all_button]

    def create_menu(self, toggled):
        self.menu=QVBoxLayout()
        self.menu.setContentsMargins(0, 2, 0, 2)
        self.menu_button=PushButton(2, 1, self, self)
        self.menu_button.set_image('./images/menu.png')
        self.menu.addWidget(self.menu_button.printing())
        self.menu_button.printing().setCheckable(True)
        self.menu_button.printing().setChecked(toggled)
        self.menu_button.printing().toggled.connect(self.open_close_menu)
        self.menu_icons=QVBoxLayout()
        for key in MainWindow.MENU_ICONS.keys():
            button=PushButton(7, 2, self, '')
            layout=QHBoxLayout()
            icon=QLabel()
            icon.setPixmap(QtGui.QPixmap(QtGui.QImage(MainWindow.MENU_ICONS[key])))
            layout.addWidget(icon, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
            text=QLabel(key)
            layout.addWidget(text, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
            button.printing().setLayout(layout)
            button.printing().clicked.connect(partial(self.change_mode, key, button))
            if key=='Home':
                self.mode=[key, button]
                button.printing().setObjectName('active_menu_button')
            else:
                button.printing().setObjectName('ordinary_menu_button')
            self.menu_icons.addWidget(button.printing())

        gb=QGroupBox()
        gb.setLayout(self.menu_icons)
        gb.setContentsMargins(0, 0, 0, 0)
        self.menu_icons=gb
        self.menu_icons.setVisible(False)
        self.menu.addWidget(self.menu_icons, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        gb=QWidget()
        gb.setLayout(self.menu)
        self.menu=gb

        self.menu.setFixedSize(self.menu_button.printing().size())

    def create_warning_message(self, parent, text, time):
        try:
            parent.messages.append(text)
        except:
            if isinstance(text, list):
                parent.messages=text
            else:
                parent.messages=[text]
        parent.contextMenuEvent(parent.printing().mapToGlobal(parent.printing().rect().bottomLeft()), time)
    
    def change_mode(self, mode, button):
        if mode!=self.mode[0]:
            if self.mode[0]=='Settings':
                self.settings_window.save()
            self.mode[0]=mode
            
            self.mode[1].printing().setObjectName('ordinary_menu_button')

            self.mode[1]=button

            self.mode[1].printing().setObjectName('active_menu_button')

            self.update()

    def open_close_menu(self):
        if self.menu_button.printing().isChecked():
            self.menu_icons.setVisible(True)
            self.menu_icons.setHidden(False)
            self.menu_icons.setFixedSize(self.menu_icons.sizeHint())
            self.menu.setFixedSize(self.menu.sizeHint())
        else:
            self.menu_icons.setVisible(False)
            self.menu_icons.setHidden(True)
            self.menu_icons.setFixedSize(0, 0)
            self.menu.setFixedSize(self.menu_button.printing().size())
        self.update()


    def closeEvent(self, event):
        self.save_data()
        sys.exit()
    
    def save_data(self):
        self.settings_window.save()
        with open('database.json', 'w') as file:
            json.dump([self.db, self.settings.fields, self.settings.active_fields, self.settings.themes,self.settings.app_language], file)

    def keyReleaseEvent(self, event:QtCore.QEvent):
        if event.key()==int(QtCore.Qt.Key.Key_S):
            if event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
                self.show_window(self.windows[1])
        elif event.key()==int(QtCore.Qt.Key.Key_H):
            if event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
                self.show_window(self.windows[0])

    def enter_pressed(self, object):
        for line in self.objects[SEARCH_RESULTS][self.settings.page]:
            if object in line.objects.values():
                self.change_button_clicked(line=line)

    def mousePressEvent(self, event):
        try:
            for line in self.objects[SEARCH_RESULTS][self.settings.page]:
                try:
                    line.objects['Theme'].menu.close()
                    del line.objects['Theme'].menu
                    line.objects['Theme'].menu=None
                except:
                    pass
        except:
            pass
        super().mousePressEvent(event)

    def hideEvent(self, event):
        for line in self.objects[SEARCH_RESULTS][self.settings.page]:
            try:
                line.objects['Theme'].menu.close()
            except:
                pass
        event.accept()
        
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
        else:
            self.write()

    def write(self):
        count=0
        for edit in self.objects[ADDING].objects.values():
            if not isinstance(edit, Combobox):
                count+=edit.check()
        if count!=(len(self.settings.active_fields)):
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
        #buttons=[PushButton(1, 1, self, '✎'), PushButton(1, 1, self)]
        buttons[0].printing().clicked.connect(partial(self.change_button_clicked, line=line))
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

        self.updateStackedWidget()
        self.layout.itemAt(1).widget().setFixedSize(1, self.menu.height()+2 if self.menu.height()>=self.sw.currentWidget().sizeHint().height() else self.sw.currentWidget().sizeHint().height()+2)
        self.style_objects()
        
        self.setFixedSize(self.menu.width()+self.sw.currentWidget().sizeHint().width()+38, self.menu.height()+17 if self.menu.height()>=self.sw.currentWidget().sizeHint().height() else self.sw.currentWidget().sizeHint().height()+17)
        

    def updateStackedWidget(self):
        if self.mode[0]=='Home':
            self.clearWidgetOfStackedWidget(0, self.home_mode_layout())
            self.sw.setCurrentIndex(0)
        elif self.mode[0]=='Settings':
            self.clearWidgetOfStackedWidget(1, self.settings_window.layout)
            self.sw.setCurrentIndex(1)
        elif self.mode[0]=='Help':
            self.clearWidgetOfStackedWidget(2, self.help_window.layout)
            self.sw.setCurrentIndex(2)
        elif self.mode[0]=='Exit':
            app.closeAllWindows()
        self.sw.setFixedSize(self.sw.currentWidget().sizeHint())

    def clearWidgetOfStackedWidget(self, index, layout):
        self.sw.setCurrentIndex(index)
        self.sw.removeWidget(self.sw.currentWidget())
        sw=QStackedWidget()
        sw.addWidget(widget_by_layout(layout))
        self.sw.insertWidget(index, sw)

    def set_cw(self):
        widget=QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

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
                self.objects[LABELS].objects[i].printing().setStyleSheet(
                    """border-style: outset;
                    border-width: 2px;
                    border-color: blue;
                    border-radius: 25%;
                    font-size: 20px;"""
                    )
        self.menu.setStyleSheet("""
            padding: 0px;
            margin-top: 3px;
            border: 0px;
        """)
        self.menu_icons.setStyleSheet("""
            QPushButton{
                border-radius: 10px;
                border: 0px;
            }
            #ordinary_menu_button:hover {
                background-color: #787575;
            }
            #ordinary_menu_button{
                background-color: white;
            }
            #active_menu_button{
                background-color: grey;
            }
        """)
        self.menu_button.printing().setStyleSheet("""
            border: 1px solid grey;
            padding: 1px;
            border-radius: 6px;
            margin-bottom: 2px;
""")
        
        
    def close_button_clicked(self, line):
        if line not in self.objects[LINES]:
            self.objects[ADDING]=Line([], [], self)
            self.adding=False
        else:
            self.objects[LINES].remove(line)
            try:
                line.objects['Theme'].menu.close()
                del line.objects['Theme'].menu
            except:
                pass
            del line
        self.update()

    def change_button_clicked(self, event=None, line=None):
        index=self.objects[LINES].index(line)
        if line not in self.objects[CHANGING].keys():
            #self.objects[CHANGING][line]='$'.join(self.objects[SEARCH_RESULTS][self.settings.page][index].objects[i].printing().text() for i in range(5))+"\n"
            self.objects[CHANGING][line]=line.get_list()
            objects=line.objects
            line.objects={}
            for field in self.settings.fields:
                self.objects[LINES][index].append(field, LineEdit(12, 1, self, objects[field].printing().text()))
        else:
            try:
                line.objects['Theme'].menu.close()
                del line.objects['Theme'].menu
                line.objects['Theme'].menu=None
            except:
                pass
            self.check_line(line)
            new_line=line.get_list()
            if new_line.count('Unrecorded')==len(self.settings.fields):
                self.db.remove(self.objects[CHANGING][line])
                self.objects[LINES].remove(line)
                del self.objects[CHANGING][line]
                del line
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
            adding_edits.append(i, LineEdit(12, 1, self))
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
        for line in self.objects[SEARCH_RESULTS][self.settings.page]:
            try:
                line['Theme'].menu.close()
                del line['Theme'].menu
                line['Theme'].menu=None
            except:
                pass
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


class SettingsWindow:
    def __init__(self, main_window:MainWindow):
        # Variables
        self.main_window=main_window
        self.settings=self.main_window.settings
        self.modes=['App language', 'Fields']
        self.fields_objects=[]
        self.mainbar_scroll=0
        
        self.update()
    
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

        try:
            self.main_window.update()
        except:
            print('Load of settings')

    @property
    def layout(self):
        return self.main_layout
    
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
        pass #todo update menu window
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
            line.objects={field:(line.objects[field] if field in line.objects.keys() else ((Label(12, 1, self, 'Unrecorded') if isinstance(line.objects[list(line.objects.keys())[0]], Label) else ((LineEdit(12, 1, self, 'Unrecorded') if field=='Theme' else LineEdit(12, 1, self, 'Unrecorded')))))) for field in new_fields}
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


        fields_overall_layout=QVBoxLayout()
        self.headers.append(Label(8, 2, self.main_window, self.modes[1]))
        fields_overall_layout.addWidget(self.headers[1].printing(), alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
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
                self.main_window.create_warning_message(line[1], 'You have only 1 field left', 5000)
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
        if self.fields_objects[-1][0].text():
            if self.fields_objects[-1][0].text() not in self.get_fields_list():
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
                self.main_window.create_warning_message(self.fields_objects[-1][0], "This name is already taken", 5000)
        else:
            self.main_window.create_warning_message(self.fields_objects[-1][0], 'Not able to add empty field', 5000)
    
    def get_fields_list(self, index=-1):
        if index!=-1:
            return [item[1].text() for item in self.fields_objects[:-1] if self.fields_objects.index(item)!=index]
        else:
            return [item[1].text() for item in self.fields_objects[:-1]]
        
    def delete_field(self, line):
        if len(self.fields_objects)>2:
            ask=QMessageBox.question(self, str(f'Delete {line[1].printing().text()}'), f'Are you sure about deleting "{line[1].printing().text()}"?', QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
            if ask==QMessageBox.StandardButton.Yes:
                index=self.fields_objects.index(line)
                delete=[self.main_window.db[i].pop(index) for i in range(len(self.main_window.db))]
                self.fields_objects.remove(line)
            self.update()
        else:
            self.main_window.create_warning_message(line[-1], 'You have a few fields', 5000)
    
    def change_field(self, line):
        index=self.fields_objects.index(line)
        if isinstance(line[1], Label):
            self.fields_objects[index][1]=LineEdit(6, 1, self.main_window, line[1].text())
        else:
            if line[1].text():
                if line[1].text() not in self.get_fields_list(index):
                    self.fields_objects[index][1]=Label(6, 1, self.main_window, line[1].text())
                else:
                    self.main_window.create_warning_message(line[1], 'The new name is already taken', 5000)
            else:
                self.main_window.create_warning_message(line[1], 'Not able to change to empty field', 5000)
        self.update()
    
    

      
                
app=QApplication(sys.argv)
app.setWindowIcon(QtGui.QIcon('./images/icon_dict.png'))
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(str(app.applicationPid()))

window=MainWindow()
window.move(0, 0)
window.show()

sys.exit(app.exec())   
