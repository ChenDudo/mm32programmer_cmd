# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    :   mm32program.py
@Time    :   2023/02/20 13:12:52
@Author  :   Chen Do
@Version :   1.0
@Desc    :   None
"""

import os
import argparse
import device

from pyocd.probe import aggregator
from pyocd.coresight import dap, ap, cortex_m


# os.environ['PATH'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libusb-1.0.24/MinGW64/dll') + os.pathsep + os.environ['PATH']

class LinkerObject:
    def __init__(self):
        self.linkers = []
        self.linkeridx = 0
        self.device = []
        self.isconnected = False
    
    def _getLinker(self):
        self.daplinks = aggregator.DebugProbeAggregator.get_all_connected_probes()
        print(self.daplinks)
        return self.daplinks

    def outputGetLinker(self):
        self._getLinker()

        linkerIdx = []
        linkerUniqueID = []
        linkerProductName = []
        linkerVendorName = []
        for i, daplink in enumerate(self.daplinks):
            linkerIdx.append(i)
            linkerUniqueID.append(daplink.unique_id)
            linkerProductName.append(daplink.product_name)
            linkerVendorName.append(daplink.vendor_name)
        dicUUID  = dict(zip(linkerIdx, linkerUniqueID))
        dicPName = dict(zip(linkerIdx, linkerProductName))
        dicVName = dict(zip(linkerIdx, linkerVendorName))
        print(dicUUID, dicPName, dicVName)
        

        return (dicUUID, dicPName, dicVName)
        

    def selectLinker(self, idx = 0):
        # daplink = self.linkers[idx]
        pass


def parse_args():
    parser = argparse.ArgumentParser(description = 'MM32-LINK basic programming operations')
    parser.add_argument('-G', '--get', metavar='', dest='reqGet', help="Get mm32link devices")
    parser.add_argument('-S', '--select', type = int, metavar='', dest='reqSelect', help="Select device to connect")
    parser.add_argument('-W', '--write', metavar='', dest='reqWrite', help="Operate: write chip")
    parser.add_argument('-R', '--read', metavar='', dest='reqRead', help="Operate: read chip")
    parser.add_argument('-E', '--earse', metavar='', dest='reqEarse', help="Operate: earse chip")
    print(parse_args)
    return parser.parse_args()


if __name__ == "__main__":
    # parse_args()
    linker = LinkerObject()
    linker.outputGetLinker()





# init parameter
# def initSetting():
#     if not os.path.exists('setting.ini'):
#         open('setting.ini', 'w', encoding='utf-8')

#     self.conf = configparser.ConfigParser()
#     self.conf.read('setting.ini', encoding='utf-8')

#     if not self.conf.has_section('globals'):
#         self.conf.add_section('globals')
#         self.conf.set('globals', 'mcu', 'MM32F0140')
#         self.conf.set('globals', 'addr', '0 K')
#         self.conf.set('globals', 'size', '64 K')
#         self.conf.set('globals', 'link', '')
#         self.conf.set('globals', 'dllpath', '')
#         self.conf.set('globals', 'hexpath', '[]')
'''
# Period Scan
def scan_debugger():
    try:
        daplinks = aggregator.DebugProbeAggregator.get_all_connected_probes()
        for daplink in daplinks:
            print(daplink.product_name)
            return daplink
    except Exception as e:
        pass

# connect
def connect():
    try:
        from pyocd.coresight import dap, ap, cortex_m
        daplink = self.daplinks[0]
        daplink.open()
        _dp = dap.DebugPort(daplink, None)
        _dp.init()
        _dp.power_up_debug()
        _ap = ap.AHB_AP(_dp, 0)
        _ap.init()
        self.dev = device.Devices[self.cmbMCU.currentText()](xlink.XLink(cortex_m.CortexM(None, _ap)))
    except Exception as e:
        daplink.close()
        return False
    return True

def on_btnErase_clicked(self):
    if self.connect():
        # self.threadErase = ThreadAsync(self.dev.sect_erase, self.addr, self.size)
        self.threadErase = ThreadAsync(self.dev.chip_erase)
        self.threadErase.taskFinished.connect(Erase_finished)
        self.threadErase.start()

def Erase_finished(self):
    QMessageBox.information(self, 'Erase Finish', '    Erase Done!        ', QMessageBox.Yes)
    self.xlk.reset()
    self.xlk.close()
    self.setEnabled(True)
    self.prgInfo.setVisible(False)

def on_btnWrite_clicked(self):
    if self.cmbHEX.currentText() == '':
        return
    if self.connect():
        self.setEnabled(False)
        self.prgInfo.setVisible(True)
        if self.cmbHEX.currentText().endswith('.hex'):
            data = parseHex(self.cmbHEX.currentText())
        else:
            data = open(self.cmbHEX.currentText(), 'rb').read()
        if len(data)%self.dev.PAGE_SIZE:
            data += b'\xFF' * (self.dev.PAGE_SIZE - len(data)%self.dev.PAGE_SIZE)

        self.threadWrite = ThreadAsync(self.dev.chip_write, self.addr, data)
        self.threadWrite.taskFinished.connect(Write_finished)
        self.threadWrite.start()

def Write_finished(self):
    QMessageBox.information(self, 'Program Finish', '    Program Done!        ', QMessageBox.Yes)
    self.xlk.reset()
    self.xlk.close()
    self.setEnabled(True)
    self.prgInfo.setVisible(False)

def on_btnRead_clicked(self):
    if self.connect():
        self.buff = []
        self.threadRead = ThreadAsync(self.dev.chip_read, self.addr, self.size, self.buff)
        self.threadRead.taskFinished.connect(Read_finished)
        self.threadRead.start()

def Read_finished(self):
    binpath, filter = QFileDialog.getSaveFileName(caption='Save memory file', filter='bin file (*.bin)')
    if binpath:
        with open(binpath, 'wb') as f:
            f.write(bytes(self.buff))
    self.xlk.reset()
    self.xlk.close()
    self.setEnabled(True)
    self.prgInfo.setVisible(False)

def addr(self):
    return int(self.cmbAddr.currentText().split()[0]) * 1024

def size(self):
    return int(self.cmbSize.currentText().split()[0]) * 1024

def closeEvent(self, evt):
    self.conf.set('globals', 'mcu',  self.cmbMCU.currentText())
    self.conf.set('globals', 'addr', self.cmbAddr.currentText())
    self.conf.set('globals', 'size', self.cmbSize.currentText())
    self.conf.set('globals', 'link', self.cmbDLL.currentText())
    self.conf.set('globals', 'dllpath', self.cmbDLL.itemText(0))
    hexpath = [self.cmbHEX.currentText()] + [self.cmbHEX.itemText(i) for i in range(self.cmbHEX.count())]
    self.conf.set('globals', 'hexpath', repr(list(collections.OrderedDict.fromkeys(hexpath))))    # 保留顺序去重
    self.conf.write(open('setting.ini', 'w', encoding='utf-8'))

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
    # 解析 .hex 文件，提取出程序代码，没有值的地方填充0xFF
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
'''