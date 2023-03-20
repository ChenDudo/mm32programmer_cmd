import os
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from PyQt5.QtGui import QRegExpValidator, QKeyEvent
from PyQt5.QtCore import QRegExp, Qt, pyqtSlot
from UI.Ui_newProject import Ui_Dialog
from interface.access_dll import AccessDll
from interface.project_base_class import ProjectInfo


class NewProjectDia(QDialog, Ui_Dialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.state = False
        self.proName.setFocus() # 指定焦点(光标)，防止回车关闭页面
        self.filePath.setReadOnly(True)

        # 获取数据库芯片信息
        dataCenter = AccessDll("Temp/dataCenter.dll")
        self.info = dataCenter.getSeriesAndPart()
        series = list(self.info)
        parts = list(self.info[series[0]]["part"])
        core = self.info[series[0]]["core"]
        flash = int(int(self.info[series[0]]["part"][parts[0]]) / 1024)

        # 设置默认值
        self.seriesName.addItems(series)
        self.core.setText(core)
        self.partModel.addItems(parts)
        self.memorySize.setText(str(flash))
        self.timeFrequency.setCurrentIndex(1)
        self.resetModel.setCurrentIndex(2)
        self.data0.setText("FF")
        self.data1.setText("FF")
        self.sfDog.setChecked(True)
        self.standby.setChecked(True)
        self.stop.setChecked(True)

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

    @pyqtSlot()
    def on_selectFile_clicked(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "select code file", "C:\\", "Inter Hex files(*.hex);;Binary files(*.bin);;Motorola files(*.s19)")
        if os.path.exists(fileName):
            self.filePath.setText(fileName)
        else:
            pass

    @pyqtSlot()
    def on_ok_clicked(self):
        if self.proName.text() != "" and self.filePath.text() != "":
            self.state = True
            self.accept()
        else:
            self.state = False
            QMessageBox.warning(self, 'Warning', 'The project name and code file cannot be empty!', QMessageBox.Yes)
            self.proName.setFocus()
    
    @pyqtSlot()
    def on_cancel_clicked(self):
        self.close()

    # 由系列变化影响partname的combx选项和core
    def showPartName(self): 
        series = self.seriesName.currentText() # 不要直接比较
        core = self.info[series]["core"]
        parts = list(self.info[series]["part"])

        self.partModel.clear()
        self.partModel.addItems(parts)

        self.core.clear()
        self.core.setText(core)
    
    # 由part变化影响flashsize变化
    def showFlashSize(self):
        series = self.seriesName.currentText()
        part = self.partModel.currentText()
        if part == "": # 切换series导致的part改变，还没来得及设置part
            part = list(self.info[series]["part"])[0]
        flash = int(int(self.info[series]["part"][part]) / 1024)

        self.memorySize.clear()
        self.memorySize.setText(str(flash))

    # 获取新建项目的信息
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
    
    # 修改项目，将treewidget的信息展示到新建项目界面
    def setProjectInfo(self, info: ProjectInfo):
        self.proName.setText(info.projectName)
        self.textEdit.setText(info.projectDesp)
        self.programPart.setCurrentText(info.programmer)
        self.chipLink.setCurrentText(info.linkMode)
        self.resetModel.setCurrentText(info.resetType)
        self.timeFrequency.setCurrentText(info.frequence)
        self.filePath.setText(info.codeFile)

        # tree没有series的信息，需要处理获取
        series = self.getSeriesFromChip(info.partName)
        self.seriesName.setCurrentText(series)
        self.partModel.setCurrentText(info.partName)
        # self.core.setText(info.core) # combx变化信号会自动填写core和size
        # self.memorySize.setText(info.flashSize)

        self.data0.setText(info.data0)
        self.data1.setText(info.data1)
        self.hdDog.setChecked(True if info.watchDog == "Hardware watchdog" else False)
        self.sfDog.setChecked(True if info.watchDog == "Software watchdog" else False)
        self.standby.setChecked(info.standbyMode)
        self.stop.setChecked(info.stopMode)
    
    # 根据芯片获取系列
    def getSeriesFromChip(self, partName: str) -> str:
        series = ""
        for key, value in self.info.items():
            partsList = list(value["part"])
            if partName in partsList:
                series = key
            else:
                pass
        return series

    # 键盘事件(pyqt自带)，防止回车影响确定选项
    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key_Enter or key == Qt.Key_Return:
            return
    
    # def closeEvent(self, event):
    #     reply = QMessageBox.question(self, 'Warning', '确认退出？', QMessageBox.Yes, QMessageBox.No)
    #     if reply == QMessageBox.Yes:
    #         event.accept()
    #     else:
    #         event.ignore()