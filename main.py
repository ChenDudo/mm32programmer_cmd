# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    :   main.py
@Time    :   2023/02/06 21:13:51
@Author  :   Chen Do
@Version :   1.0
@Desc    :   None
"""
import os
import sys
from PyQt5.QtWidgets import QApplication,QMainWindow
from PyQt5 import uic
from mm32_ui import Ui_Programmer

def get_path():
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app
        # path into variable _MEIPASS'.
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath("."))
        # application_path = os.path.dirname(os.path.abspath(__file__))
    return application_path
    # return os.path.realpath(os.path.dirname(sys.argv[0]))

# dynamic loading
class mainwindow(QMainWindow):
    def __init__(self):
        self.ui=uic.loadUi(get_path()+"\\UI\\mm32_ui.ui")
        self.ui.show()

    def on_btnReflash_clicked(self):
        QMessageBox.information(self, 'Erase Finish', '    Erase Done!        ', QMessageBox.Yes)

# static loading
class __mainwindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui=Ui_Programmer()
        self.ui.setupUi(self)
        self.show()

if __name__=="__main__":
    app=QApplication(sys.argv)
    window=mainwindow()
    sys.exit(app.exec_())
