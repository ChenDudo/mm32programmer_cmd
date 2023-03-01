import os
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from PyQt5.QtGui import QRegExpValidator, QKeyEvent
from PyQt5.QtCore import QRegExp, Qt
from UI.Ui_newProject import Ui_Dialog
from interface.access_dll import AccessDll
from interface.project_base_class import ProjectInfo

class NewProjectDia(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.timeFrequency.setCurrentIndex(1)
        self.resetModel.setCurrentIndex(2)
        self.proName.setFocus() # 指定焦点(光标)，防止回车关闭页面

        # 从dll获取芯片信息
        self.info = self.getSeriesAndPart()
        series = []
        currentPart = []
        for key in self.info.keys():
            series.append(key)
        for key in self.info[series[0]]["part"].keys():
            currentPart.append(key)
        currentCore = self.info[series[0]]["core"]
        currentSize = int(int(self.info[series[0]]["part"][currentPart[0]]) / 1024)
        self.seriesName.addItems(series)
        self.core.setText(currentCore)
        self.partModel.addItems(currentPart)
        self.memorySize.setText(str(currentSize))
        
        # 设置默认值
        self.data0.setText("FF")
        self.data1.setText("FF")
        self.sfDog.setChecked(True)
        self.standby.setChecked(True)
        self.stop.setChecked(True)
        self.filePath.setReadOnly(True)

        # 验证输入
        reHex2 = QRegExp("[A-Fa-f0-9]{2}")
        optionValid = QRegExpValidator(reHex2)
        self.data0.setValidator(optionValid)
        self.data1.setValidator(optionValid)
        reName = QRegExp("^[A-Za-z0-9]+$")
        nameValid = QRegExpValidator(reName)
        self.proName.setValidator(nameValid)

        self.seriesName.currentIndexChanged.connect(self.showPartName)
        self.partModel.currentIndexChanged.connect(self.showFlashSize)
        self.selectFile.clicked.connect(self.openFile)

    def getSeriesAndPart(self) -> dict: # 系列确定开发板型号和内核，开发板型号确定flash大小(算法不好，系列不能重复出现，否则会覆盖之前的数据)
        seriesInfo = {}
        dataCenter = AccessDll("Temp/dataCenter.dll")
        allSeries = dataCenter.print_json_to_str(dataCenter.get_series_list())
        seriesList = allSeries["data"]
        for i in range(len(seriesList)): # 获取全系列名
            seriesInfo[seriesList[i]["seriesName"]] = {} # core,part

        allChips = dataCenter.print_json_to_str(dataCenter.get_chip_list_for_all())
        chipsList = allChips["data"]
        length = len(chipsList)
        chips = {} #partname:flashsize
        tempSeries = chipsList[0]["seriesName"]
        for i in range(length):
            series = chipsList[i]["seriesName"]
            if tempSeries != series:
                seriesInfo[tempSeries]["core"] = chipsList[i-1]["core"]
                seriesInfo[tempSeries]["part"] = chips
                chips = {} 
            tempSeries = series
            partName = chipsList[i]["partName"]
            flashSize = chipsList[i]["flashSize"]
            chips[partName] = flashSize
        #将最后的芯片信息填入
        seriesInfo[tempSeries]["core"] = chipsList[length - 1]["core"]
        seriesInfo[tempSeries]["part"] = chips
        #处理没有part的series
        info = {}
        for key, value in seriesInfo.items():
            if len(value) != 0:
                info[key] = value
            else:
                pass
        return info

    def showPartName(self): # 数值校验，不能为空，非法字符等
        series = self.seriesName.currentText() # 不要直接比较
        parts = []
        core = self.info[series]["core"]
        for key in self.info[series]["part"].keys():
            parts.append(key)

        self.partModel.clear()
        self.partModel.addItems(parts)

        self.core.clear()
        self.core.setText(core)
    
    def showFlashSize(self):
        series = self.seriesName.currentText()
        part = self.partModel.currentText()
        if part == "": # 切换series导致的part改变，还没来得及设置part
            part = list(self.info[series]["part"])[0]
        flash = int(int(self.info[series]["part"][part]) / 1024)
        self.memorySize.clear()
        self.memorySize.setText(str(flash))

    def openFile(self):
        options = QFileDialog().Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "select file", "C:\\", "Inter Hex files(*.hex);;Binary files(*.bin);;Motorola files(*.s19);;All files(*.*)")
        if os.path.exists(fileName):
            self.filePath.setText(fileName)
        else:
            pass

    def getProjectInfo(self) -> ProjectInfo:
        info = ProjectInfo()
        info.projectName = self.proName.text()
        info.projectDesp = self.textEdit.toPlainText()
        info.programmer = self.programPart.currentText()
        info.linkMode = self.chipLink.currentText()
        info.resetType = self.resetModel.currentText()
        info.frequence = self.timeFrequency.currentText()
        info.series = self.seriesName.currentText()
        info.partName = self.partModel.currentText()
        info.core = self.core.text()
        info.flashSize = self.memorySize.text()
        info.codeFile = self.filePath.text()
        
        info.data0 = self.data0.text()
        info.data1 = self.data1.text()
        info.hWatchDog = self.hdDog.isChecked()
        info.sWatchDog = self.sfDog.isChecked()
        info.standbyMode = self.standby.isChecked()
        info.stopMode = self.stop.isChecked()

        return info

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key_Enter or key == Qt.Key_Return:
            return
    
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Warning', '确认退出？', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()