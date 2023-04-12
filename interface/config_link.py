from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from UI.Ui_linkConfig import Ui_Dialog
import os
import psutil

class ConfigLink(QDialog, Ui_Dialog):
    signalSpeed = pyqtSignal(int)

    def __init__(self, parent:None, speed: int):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.showDia(speed)

    @pyqtSlot()
    def on_ok_clicked(self):
        self.cfgLink()

    # 查找U盘下的文件并修改
    def findDETAILSFile(self): # 查找到的第一个
        diskInfo: list = psutil.disk_partitions()
        for disk in diskInfo:
            drive = disk.mountpoint
            file = os.path.join(drive, "DETAILS.TXT")
            if os.path.exists(file): 
                return file
            else:
                pass
    
    # 读取问电压和蜂鸣器状态信息
    def showDia(self, speed: int):
        file = self.findDETAILSFile()
        if file == None:
            self.close()
        else:
            with open(file, "r") as f:
                for line in f:
                    if "Target Power output: " in line:
                        self.setVoltage(line)
                    if "Beep Mode: " in line:
                        self.setBeepState(line)
            speedDict = {200000: 0, 500000: 1, 1000000: 2, 5000000: 3, 10000000: 4}
            self.comboBox.setCurrentIndex(speedDict[speed])

    # 修改link配置
    def cfgLink(self):
        file = self.findDETAILSFile()
        state = self.checkLinkInfo()
        if not state: # link信息未修改
            pass
        else:
            (path, name) = os.path.split(file)
            voltageFile = self.getVoltageState()
            beepFile = self.getBeepState()
            open(os.path.join(path, voltageFile), "a")
            open(os.path.join(path, beepFile), "a")
        speedDict = {0: 200000, 1: 500000, 2: 1000000, 3: 5000000, 4: 10000000}
        index = self.comboBox.currentIndex()
        self.signalSpeed.emit(speedDict[index])
        self.close()
    
    # 检查信息是否修改
    def checkLinkInfo(self) -> bool:
        if self.beepCK.isChecked() != self.oldBeep:
            return True
        if self.vNone.isChecked() and (self.oldVoltage != 0):
            return True
        if self.v3.isChecked() and (self.oldVoltage != 1):
            return True
        if self.v5.isChecked() and (self.oldVoltage != 2):
            return True
        return False

    # 获取电压状态
    def getVoltageState(self):
        if self.vNone.isChecked():
            return "VT_OFF.CFG"
        elif self.v3.isChecked():
            return "VT_3V3.CFG"
        elif self.v5.isChecked():
            return "VT_5V.CFG"
    
    # 设置电压
    def setVoltage(self, line: str):
        if "5V" in line:
            self.oldVoltage = 2
            self.v5.setChecked(True)
        elif "3V" in line:
            self.oldVoltage = 1
            self.v3.setChecked(True)
        elif "OFF" in line:
            self.oldVoltage = 0
            self.vNone.setChecked(True)
    
    # 设置蜂鸣器
    def setBeepState(self, line: str):
        if "ON" in line:
            self.oldBeep = True
            self.beepCK.setChecked(True)
        elif "OFF" in line:
            self.oldBeep = False
            self.beepCK.setChecked(False)
    
    # 获取蜂鸣器状态
    def getBeepState(self):
        if self.beepCK.isChecked():
            return "BEEP_ON.CFG"
        else:
            return "BEEP_OFF.CFG"
    



