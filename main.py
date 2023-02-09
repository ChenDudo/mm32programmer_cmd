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

import device
import xlink

from pyocd.probe import aggregator
from pyocd.coresight import dap, ap, cortex_m

from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox,QFileDialog
from PyQt5 import QtCore,uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread

# os.environ['PATH'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libusb-1.0.24/MinGW64/dll') + os.pathsep + os.environ['PATH']

'''
""" static loading """

from mm32_ui import Ui_Programmer
class mainwindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui=Ui_Programmer()
        self.ui.setupUi(self)
'''

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

def parseHex(file):
    ''' Parse the .hex file, extract the program code, and populate the 0xFF where there are no values '''
    data = ''
    currentAddr = 0
    extSegAddr  = 0     # 扩展段地址
    for line in open(file, 'rb').readlines():
        line = line.strip()
        if len(line) == 0: continue

        len_ = int(line[1:3],16)
        addr = int(line[3:7],16) + extSegAddr
        type = int(line[7:9],16)
        if type == 0x00:
            if currentAddr != addr:
                if currentAddr != 0:
                    data += '\xFF' * (addr - currentAddr)
                currentAddr = addr
            for i in range(len_):
                data += chr(int(line[9+2*i:11+2*i], 16))
            currentAddr += len_
        elif type == 0x02:
            extSegAddr = int(line[9:9+4], 16) * 16
        elif type == 0x04:
            extSegAddr = int(line[9:9+4], 16) * 65536
    return data.encode('latin')

def show_message():
    msg_box = QMessageBox(QMessageBox.Warning, 'Warning', 'Comming soon ...', QMessageBox.Yes)
    msg_box.exec_()

""" dynamic loading """
def get_path():
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    return application_path
    # return os.path.realpath(os.path.dirname(sys.argv[0]))

class mainwindow(QMainWindow):
    def __init__(self):
        super(mainwindow, self).__init__()
        self.ui=uic.loadUi(get_path()+"\\UI\\mm32_ui.ui")
        self.ui.show()
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
            self.conf.set('globals', 'mcu', 'MM32F0140')
            self.conf.set('globals', 'addr', '0 K')
            self.conf.set('globals', 'size', '64 K')
            self.conf.set('globals', 'hexpath', '[]')
        
        self.ui.cbbPort.setCurrentIndex(self.ui.cbbPort.findText(self.conf.get('globals','DebugPort')))
        self.ui.cbbFreq.setCurrentIndex(self.ui.cbbFreq.findText(self.conf.get('globals', 'Freq')))
        self.ui.cbbResetMode.setCurrentIndex(self.ui.cbbResetMode.findText(self.conf.get('globals', 'ResetMode')))
        self.ui.cbbSerialNumber.setCurrentIndex(self.ui.cbbSerialNumber.findText(self.conf.get('globals', 'link')))
        self.ui.cmbMCU.addItems(device.Devices.keys())
        self.ui.cmbMCU.setCurrentIndex(self.ui.cmbMCU.findText(self.conf.get('globals', 'mcu')))
        self.ui.cmbAddr.setCurrentIndex(self.ui.cmbAddr.findText(self.conf.get('globals', 'addr')))
        self.ui.cmbSize.setCurrentIndex(self.ui.cmbSize.findText(self.conf.get('globals', 'size')))
        self.ui.cmbHEX.addItems(eval(self.conf.get('globals', 'hexpath')))

        self.on_tmrDAP_timeout()
        
        # self.ui.btnReflash.clicked.connect(app_btn_refresh_clicked)
        # self.ui.btnDeviceConnect.clicked.connect(app_btn_DeviceConnect_clicked)
        # self.ui.btnFullErase.clicked.connect(app_btn_fullErase_clicked)
        # self.ui.btnLock.clicked.connect(app_btn_lock_clicked)
        # self.ui.btnUnlock.clicked.connect(app_btn_unlock_clicked)
        # self.ui.btnDownload.clicked.connect(app_btn_download_clicked)
        # self.ui.btnOpen.clicked.connect(app_btn_open_clicked)

    def on_tmrDAP_timeout(self):
        if not self.isEnabled():    # link working
            return
        try:
            from pyocd.probe import aggregator
            self.daplinks = aggregator.DebugProbeAggregator.get_all_connected_probes()
            if len(self.daplinks) != self.ui.cbbSerialNumber.count():
                self.ui.cbbSerialNumber.clear()
                for i,daplink in enumerate(self.daplinks):
                    print(i, daplink.unique_id)
                    if (daplink.product_name[:4] == 'MM32'):
                        debuggername = "MM32LINK "
                    else:
                        debuggername = "UNKNOWN  "
                    showname = debuggername + daplink.unique_id[:3] + "_" + daplink.unique_id[7:11] + " " + daplink.product_name[5:7]
                    self.ui.cbbSerialNumber.addItem(showname)
        except Exception as e:
            self.ui.cbbSerialNumber.close()
            pass

    def logOutput(self, text):
        self.ui.txtLog.appendPlainText(text)

    @pyqtSlot()
    def on_btnDeviceConnect_clicked(self):
        # self.logOutput("Device Connect clicked.")
        print("[info]:\tDevice connecting ...")
        self.connect()

    @property
    def addr(self):
        return int(self.ui.cmbAddr.currentText().split()[0]) * 1024

    @property
    def size(self):
        return int(self.ui.cmbSize.currentText().split()[0]) * 1024

    @pyqtSlot(str)
    def on_cmbMCU_currentIndexChanged(self, str):
        dev = device.Devices[self.ui.cmbMCU.currentText()]

        self.ui.cmbAddr.clear()
        self.ui.cmbSize.clear()
        for i in range(dev.CHIP_SIZE//dev.SECT_SIZE):
            if (dev.SECT_SIZE * i) % 1024 == 0:
                self.ui.cmbAddr.addItem('%d K'  %(dev.SECT_SIZE * i    // 1024))
            if (dev.SECT_SIZE * (i+1)) % 1024 == 0:
                self.ui.cmbSize.addItem('%d K' %(dev.SECT_SIZE * (i+1) // 1024))

        self.ui.cmbAddr.setCurrentIndex(self.ui.cmbAddr.findText(self.conf.get('globals', 'addr')))
        self.ui.cmbSize.setCurrentIndex(self.ui.cmbSize.findText(self.conf.get('globals', 'size')))

    @pyqtSlot()
    def on_btnOpen_clicked(self):
        hexpath, filter = QFileDialog.getOpenFileName(caption='Image file path', filter='Image File (*.bin *.hex)', directory=self.ui.cmbHEX.currentText())
        if hexpath:
            self.ui.cmbHEX.insertItem(0, hexpath)
            self.ui.cmbHEX.setCurrentIndex(0)
            
    def connect(self):
        try:
            from pyocd.coresight import dap, ap, cortex_m
            daplink = self.daplinks[self.ui.cbbSerialNumber.currentIndex()]
            daplink.open()
            _dp = dap.DebugPort(daplink, None)
            _dp.init()
            _dp.power_up_debug()
            _ap = ap.AHB_AP(_dp, 0)
            _ap.init()
            self.xlk = xlink.XLink(cortex_m.CortexM(None, _ap))

            # self.dev = device.Devices[self.ui.cmbMCU.currentText()](self.xlk)
        except Exception as e:
            print("[Err]:\tConnect Failed")
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
        hexpath = [self.ui.cmbHEX.currentText()] + [self.ui.cmbHEX.itemText(i) for i in range(self.ui.cmbHEX.count())]
        self.conf.set('globals', 'hexpath', repr(list(collections.OrderedDict.fromkeys(hexpath))))    # 保留顺序去重
        self.conf.write(open('setting.ini', 'w', encoding='utf-8'))

if __name__=="__main__":
    app=QApplication(sys.argv)
    window=mainwindow()
    sys.exit(app.exec_())
