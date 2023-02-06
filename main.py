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

def get_path():
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app
        # path into variable _MEIPASS'.
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    return application_path

class mainwindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # PyQt5
        self.ui=uic.loadUi(get_path()+"\\UI\\mm32_ui.ui")
        # 这里与静态载入不同，使用 self.ui.show()
        # 如果使用 self.show(),会产生一个空白的 MainWindow
        self.ui.show()

if __name__=="__main__":
    app=QApplication(sys.argv)
    window=mainwindow()
    sys.exit(app.exec_())
