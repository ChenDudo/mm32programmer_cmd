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

from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox,QFileDialog,QWidget
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
        self.setupUi(self)
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

# class mainwindow(QMainWindow):
#     def __init__(self):
#         super(mainwindow, self).__init__()
#         self.ui=uic.loadUi(get_path()+"\\UI\\mm32_ui")
#         self.show()
#         self.setMyUi()
class mainwindow(QMainWindow):
    def __init__(self):
        super(mainwindow, self).__init__()
        uic.loadUi(get_path()+"\\UI\\mm32_ui.ui", self)

        self.show()
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
        
        self.cbbPort.setCurrentIndex(self.cbbPort.findText(self.conf.get('globals','DebugPort')))
        self.cbbFreq.setCurrentIndex(self.cbbFreq.findText(self.conf.get('globals', 'Freq')))
        self.cbbResetMode.setCurrentIndex(self.cbbResetMode.findText(self.conf.get('globals', 'ResetMode')))
        self.cbbSerialNumber.setCurrentIndex(self.cbbSerialNumber.findText(self.conf.get('globals', 'link')))
        self.cmbMCU.addItems(device.Devices.keys())
        self.cmbMCU.setCurrentIndex(self.cmbMCU.findText(self.conf.get('globals', 'mcu')))
        self.cmbAddr.setCurrentIndex(self.cmbAddr.findText(self.conf.get('globals', 'addr')))
        self.cmbSize.setCurrentIndex(self.cmbSize.findText(self.conf.get('globals', 'size')))
        self.cmbHEX.addItems(eval(self.conf.get('globals', 'hexpath')))

        self.on_tmrDAP_timeout()

    def on_tmrDAP_timeout(self):
        if not self.isEnabled():    # link working
            return
        try:
            from pyocd.probe import aggregator
            self.daplinks = aggregator.DebugProbeAggregator.get_all_connected_probes()
            if len(self.daplinks) != self.cbbSerialNumber.count():
                self.cbbSerialNumber.clear()
                for i,daplink in enumerate(self.daplinks):
                    print(i, daplink.product_name, daplink.unique_id)
                    if (daplink.product_name[:7] == 'MM32_V1'):
                        showname = "MM32LINK_V1 " + daplink.unique_id[:3] + "_" + daplink.unique_id[7:11]
                    else:
                        showname = "Unkown CMSIS-DAP " + daplink.unique_id[:3]
                    self.cbbSerialNumber.addItem(showname)
        except Exception as e:
            self.cbbSerialNumber.close()
            pass

    def logOutput(self, text):
        self.txtLog.append(text)

    def connect(self):
        try:
            from pyocd.coresight import dap, ap, cortex_m
            daplink = self.daplinks[self.cbbSerialNumber.currentIndex()]
            daplink.open()
            _dp = dap.DebugPort(daplink, None)
            _dp.init()
            _dp.power_up_debug()
            _ap = ap.AHB_AP(_dp, 0)
            _ap.init()
            self.xlk = xlink.XLink(cortex_m.CortexM(None, _ap))

            self.dev = device.Devices[self.cmbMCU.currentText()](self.xlk)
        except Exception as e:
            print("[Err]:\tConnect Failed")
            daplink.close()
            QMessageBox.critical(self, 'Connect Failed', 'Connect Failed\n' + str(e), QMessageBox.Yes)
            return False
        return True

    @pyqtSlot()
    def on_btnDeviceConnect_clicked(self):
        self.logOutput("Device Connect clicked.")
        print("[info]:\tDevice connecting ...")
        self.connect()

    @property
    def addr(self):
        return int(self.cmbAddr.currentText().split()[0]) * 1024

    @property
    def size(self):
        return int(self.cmbSize.currentText().split()[0]) * 1024

    # @pyqtSlot(str)
    # def on_cbbSerialNumber_activated(self, str):
    #     print("on_cbbSerialNumber_currentIndexChanged")
    #     index = self.cbbSerialNumber.currentIndex()
    #     self.lblFWVersion.setText(self.daplinks[index].unique_id[:20])
    #     self.lblFWVersion.repaint()

    @pyqtSlot(str)
    def on_cbbSerialNumber_currentIndexChanged(self, str):
        print("on_cbbSerialNumber_currentIndexChanged")
        index = self.cbbSerialNumber.currentIndex()
        self.lblFWVersion.setText(self.daplinks[index].unique_id[:20])
        self.lblFWVersion.repaint()

    @pyqtSlot(str)
    def on_cmbMCU_currentIndexChanged(self, str):
        print("on_cmbMCU_currentIndexChanged")
        dev = device.Devices[self.cmbMCU.currentText()]

        self.cmbAddr.clear()
        self.cmbSize.clear()
        for i in range(dev.CHIP_SIZE//dev.SECT_SIZE):
            if (dev.SECT_SIZE * i) % 1024 == 0:
                self.cmbAddr.addItem('%d K'  %(dev.SECT_SIZE * i    // 1024))
            if (dev.SECT_SIZE * (i+1)) % 1024 == 0:
                self.cmbSize.addItem('%d K' %(dev.SECT_SIZE * (i+1) // 1024))

        self.cmbAddr.setCurrentIndex(self.cmbAddr.findText(self.conf.get('globals', 'addr')))
        self.cmbSize.setCurrentIndex(self.cmbSize.findText(self.conf.get('globals', 'size')))

    @pyqtSlot()
    def on_btnOpen_clicked(self):
        hexpath, filter = QFileDialog.getOpenFileName(caption='Image file path', filter='Image File (*.bin *.hex)', directory=self.cmbHEX.currentText())
        if hexpath:
            self.cmbHEX.insertItem(0, hexpath)
            self.cmbHEX.setCurrentIndex(0)

    @pyqtSlot()
    def on_btnDownload_clicked(self):
        print("Download begin ...")
        if self.cmbHEX.currentText() == '':
            return

        if self.connect():
            self.setEnabled(False)

            if self.cmbHEX.currentText().endswith('.hex'):
                data = parseHex(self.cmbHEX.currentText())
            else:
                data = open(self.cmbHEX.currentText(), 'rb').read()

            if len(data)%self.dev.PAGE_SIZE:
                data += b'\xFF' * (self.dev.PAGE_SIZE - len(data)%self.dev.PAGE_SIZE)

            self.threadWrite = ThreadAsync(self.dev.chip_write, self.addr, data)
            self.threadWrite.taskFinished.connect(self.Write_finished)
            self.threadWrite.start()

    def Write_finished(self):
        QMessageBox.information(self, 'Program Finish', '    Program Done!        ', QMessageBox.Yes)
        self.xlk.reset()
        self.xlk.close()
        self.setEnabled(True)

    @pyqtSlot()
    def on_btnRead_clicked(self):
        if self.connect():
            self.setEnabled(False)

            self.buff = []      # bytes 无法 extend，因此用 list
            self.threadRead = ThreadAsync(self.dev.chip_read, self.addr, self.size, self.buff)
            self.threadRead.taskFinished.connect(self.Read_finished)
            self.threadRead.start()

    def Read_finished(self):
        binpath, filter = QFileDialog.getSaveFileName(caption='Save memory file', filter='bin file (*.bin)')
        if binpath:
            with open(binpath, 'wb') as f:
                f.write(bytes(self.buff))

    @pyqtSlot()
    def on_btnFullErase_clicked(self):
        if self.connect():
            self.setEnabled(False)
            # self.threadErase = ThreadAsync(self.dev.sect_erase, self.addr, self.size)
            self.threadErase = ThreadAsync(self.dev.chip_erase)
            self.threadErase.taskFinished.connect(self.Erase_finished)
            self.threadErase.start()

    def Erase_finished(self):
        QMessageBox.information(self, 'Erase Finish', '    Erase Done!        ', QMessageBox.Yes)
        self.xlk.reset()
        self.xlk.close()
        self.setEnabled(True)

    def closeEvent(self, evt):
        self.conf.set('globals', 'DebugPort',  self.cbbPort.currentText())
        self.conf.set('globals', 'Freq', self.cbbFreq.currentText())
        self.conf.set('globals', 'ResetMode', self.cbbResetMode.currentText())
        self.conf.set('globals', 'link', self.cbbSerialNumber.currentText())
        # self.conf.set('globals', 'dllpath', self.cbbSerialNumber.itemText(0))
        hexpath = [self.cmbHEX.currentText()] + [self.cmbHEX.itemText(i) for i in range(self.cmbHEX.count())]
        self.conf.set('globals', 'hexpath', repr(list(collections.OrderedDict.fromkeys(hexpath))))    # 保留顺序去重
        self.conf.write(open('setting.ini', 'w', encoding='utf-8'))

if __name__=="__main__":
    app=QApplication(sys.argv)
    window=mainwindow()
    sys.exit(app.exec_())
