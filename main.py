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
import collections
import configparser

from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox
from PyQt5 import QtCore,uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread

class ThreadAsync(QThread):
    taskFinished = pyqtSignal()
    def __init__(self, func, *args):
        super(ThreadAsync, self).__init__()
        self.func = func
        self.args = args
    def run(self):
        try:
            self.func(*self.args)
        except Exception as e:
            pass
        self.taskFinished.emit()


def show_message():
    msg_box = QMessageBox(QMessageBox.Warning, 'Warning', 'Comming soon ...')
    msg_box.exec_()

# interface 
## Tool button
def app_btn_refresh_clicked():
    # show_message()
    print("helllo")
    pass

## Push button
def app_btn_DeviceConnect_clicked():
    show_message()
    print("app_btn_DeviceConnect_clicked")
    pass

def app_btn_fullErase_clicked():
    show_message()
    print("app_btn_fullErase_clicked")
    pass

def app_btn_lock_clicked():
    show_message()
    print("app_btn_lock_clicked")
    pass

def app_btn_unlock_clicked():
    show_message()
    print("app_btn_unlock_clicked")
    pass

def app_btn_download_clicked():
    show_message()
    print("app_btn_download_clicked")
    pass

def app_btn_netDownload_cliked():
    show_message()
    print("app_btn_netDownload_cliked")
    pass

def app_btn_open_clicked():
    show_message()
    print("app_btn_open_clicked")
    pass


""" static loading """
from mm32_ui import Ui_Programmer
from pyocd.probe import aggregator
from pyocd.coresight import dap, ap, cortex_m
class mainwindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui=Ui_Programmer()
        self.ui.setupUi(self)

        self.setMyUi()

        self.tmrDAP = QtCore.QTimer()
        self.tmrDAP.setInterval(1000)
        self.tmrDAP.timeout.connect(self.on_tmrDAP_timeout)
        self.tmrDAP.start()

    def setMyUi(self):
        if not os.path.exists('setting.ini'):
            open('setting.ini', 'w', encoding='utf-8')

        self.conf = configparser.ConfigParser()
        self.conf.read('setting.ini', encoding='utf-8')

        if not self.conf.has_section('globals'):
            self.conf.add_section('globals')
            self.conf.set('globals', 'DebugPort', 'SWD')
            self.conf.set('globals', 'Freq', '10MHz')
            self.conf.set('globals', 'ResetMode', 'HW RESET')
            self.conf.set('globals', 'link', '')
            # self.conf.set('globals', 'dllpath', '')
        
        self.ui.cbbPort.setCurrentIndex(self.ui.cbbPort.findText(self.conf.get('globals','DebugPort')))
        self.ui.cbbFreq.setCurrentIndex(self.ui.cbbFreq.findText(self.conf.get('globals', 'Freq')))
        self.ui.cbbResetMode.setCurrentIndex(self.ui.cbbResetMode.findText(self.conf.get('globals', 'ResetMode')))
        self.ui.cbbSerialNumber.addItem(" ")
        self.on_tmrDAP_timeout()

        index = self.ui.cbbSerialNumber.findText(self.conf.get('globals', 'link'))
        self.ui.cbbSerialNumber.setCurrentIndex(index if index != -1 else 0)

        # self.ui.btnReflash.clicked.connect(app_btn_refresh_clicked)
        self.ui.btnDeviceConnect.clicked.connect(app_btn_DeviceConnect_clicked)
        self.ui.btnFullErase.clicked.connect(app_btn_fullErase_clicked)
        self.ui.btnLock.clicked.connect(app_btn_lock_clicked)
        self.ui.btnUnlock.clicked.connect(app_btn_unlock_clicked)
        self.ui.btnDownload.clicked.connect(app_btn_download_clicked)
        self.ui.btnNetDownload.clicked.connect(app_btn_netDownload_cliked)
        self.ui.btnOpen.clicked.connect(app_btn_open_clicked)
        

    def on_tmrDAP_timeout(self):
        if not self.isEnabled():    # link working
            return
        try:
            from pyocd.probe import aggregator
            self.daplinks = aggregator.DebugProbeAggregator.get_all_connected_probes()
            if len(self.daplinks) != self.ui.cbbSerialNumber.count() - 1:
                for i in range(1, self.ui.cbbSerialNumber.count()):
                    self.ui.cbbSerialNumber.removeItem(i)
                    self.ui.lblFWVersion.setText("")
                for i, daplink in enumerate(self.daplinks):
                    self.ui.cbbSerialNumber.addItem(daplink.product_name[:7]+" No."+daplink.unique_id[3:11])
                    self.ui.lblFWVersion.setText(daplink.unique_id)
        except Exception as e:
            # self.cmbDLL.close()
            pass

    def connect(self):
        try:
            if self.cmbDLL.currentIndex() == 0:
                self.xlk = xlink.XLink(jlink.JLink(self.cmbDLL.currentText(), device.Devices[self.cmbMCU.currentText()].CHIP_CORE))

            else:
                from pyocd.coresight import dap, ap, cortex_m
                daplink = self.daplinks[self.cmbDLL.currentIndex() - 1]
                daplink.open()

                _dp = dap.DebugPort(daplink, None)
                _dp.init()
                _dp.power_up_debug()

                _ap = ap.AHB_AP(_dp, 0)
                _ap.init()

                self.xlk = xlink.XLink(cortex_m.CortexM(None, _ap))
            self.dev = device.Devices[self.cmbMCU.currentText()](self.xlk)
        except Exception as e:
            daplink.close()
            QMessageBox.critical(self, 'Connect Failed', 'Connect Failed\n' + str(e), QMessageBox.Yes)
            return False
        return True

    def closeEvent(self, evt):
        self.conf.set('globals', 'DebugPort',  self.ui.cbbPort.currentText())
        self.conf.set('globals', 'Freq', self.ui.cbbFreq.currentText())
        self.conf.set('globals', 'ResetMode', self.ui.cbbResetMode.currentText())
        self.conf.set('globals', 'link', self.ui.cbbSerialNumber.currentText())
        # self.conf.set('globals', 'dllpath', self.ui.cbbSerialNumber.itemText(0))
        # hexpath = [self.cmbHEX.currentText()] + [self.cmbHEX.itemText(i) for i in range(self.cmbHEX.count())]
        # self.conf.set('globals', 'hexpath', repr(list(collections.OrderedDict.fromkeys(hexpath))))    # 保留顺序去重
        self.conf.write(open('setting.ini', 'w', encoding='utf-8'))


# """ dynamic loading """
# def get_path():
#     if getattr(sys, 'frozen', False):
#         application_path = sys._MEIPASS
#     else:
#         application_path = os.path.dirname(os.path.abspath(__file__))
#     return application_path
#     # return os.path.realpath(os.path.dirname(sys.argv[0]))

# class mainwindow(QMainWindow):
#     def __init__(self):
#         super(mainwindow, self).__init__()
#         self.ui=uic.loadUi(get_path()+"\\UI\\mm32_ui.ui")
#         self.ui.show()
    

if __name__=="__main__":
    app=QApplication(sys.argv)
    window=mainwindow()
    window.show()
    sys.exit(app.exec_())
