import os
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox, QCheckBox
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
        path = os.getcwd()
        dataCenter = AccessDll(os.path.join(path, "dataCenter.dll"))
        self.info = dataCenter.getSeriesAndPart()
        series = list(self.info)
        parts = list(self.info[series[0]]["part"])
        core = self.info[series[0]]["core"]
        flash = int(int(self.info[series[0]]["part"][parts[0]]) / 1024)
        self.newOptionByte(series[0])

        # 设置默认值
        self.tabWidget.setCurrentIndex(0)
        self.seriesName.addItems(series)
        self.core.setText(core)
        self.partModel.addItems(parts)
        self.memorySize.setText(str(flash))
        self.data0.setText("FF")
        self.data1.setText("FF")
        self.sfDog.setChecked(True)
        self.standby.setChecked(False)
        self.stop.setChecked(False)

        self.bootCk.setChecked(True)
        self.pa10Ck.setChecked(True)
        self.shutdown.setChecked(False)

        self.eraseck.setChecked(True)
        self.programck.setChecked(True)
        self.verifyck.setChecked(True)
        self.securityck.setChecked(False)

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
        if self.proName.text() != "":
            self.state = True
            self.accept()
        else:
            self.state = False
            QMessageBox.warning(self, 'Warning', 'The project name cannot be empty!', QMessageBox.Yes)
            self.proName.setFocus()
    
    @pyqtSlot()
    def on_cancel_clicked(self):
        self.close()

    # 由系列变化影响partname的combx选项和core，以及optionByte部分
    def showPartName(self): 
        series = self.seriesName.currentText() # 不要直接比较
        core = self.info[series]["core"]
        parts = list(self.info[series]["part"])

        self.partModel.clear()
        self.partModel.addItems(parts)

        self.core.clear()
        self.core.setText(core)
        
        self.newOptionByte(series)

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

        info.erase = self.eraseck.isChecked()
        info.program = self.programck.isChecked()
        info.verify = self.verifyck.isChecked()
        info.security = self.securityck.isChecked()

        # 0 表示无该属性不显示，1表示有该属性但未勾选，2表示勾选
        info.nboot = 0 if self.bootCk.isHidden() else 2 if self.bootCk.isChecked() else 1
        info.pa10 = 0 if self.pa10Ck.isHidden() else 2 if self.pa10Ck.isChecked() else 1
        info.shutMode = 0 if self.shutdown.isHidden() else 2 if self.shutdown.isChecked() else 1

        return info
    
    # 修改项目，将treewidget的信息展示到新建项目界面
    def setProjectInfo(self, info: ProjectInfo):
        self.proName.setText(info.projectName)
        self.textEdit.setText(info.projectDesp)
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

        # 添加特殊的userbyte选项
        self.setUserByte(info.nboot, self.bootCk)
        self.setUserByte(info.pa10, self.pa10Ck)
        self.setUserByte(info.shutMode, self.shutdown)

        self.eraseck.setChecked(info.erase)
        self.programck.setChecked(info.program)
        self.verifyck.setChecked(info.verify)
        self.securityck.setChecked(info.security)
    
    # userByte属性设置
    def setUserByte(self, state: int, ck: QCheckBox):
        if state == 0:
            ck.setHidden(True)
        else:
            ck.setHidden(False)
            ck.setChecked(True if state == 2 else False)
    
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
    
    # 根据系列设置不同的opt属性
    def newOptionByte(self, series: str):
        if series in ["MM32F0010", "MM32F3270"]:
            self.bootCk.setHidden(True)
            self.pa10Ck.setHidden(True)
            self.shutdown.setHidden(True)
        elif series in ["MM32F0130","MM32F0140", "MM32F0270"]:
            self.bootCk.setHidden(False)
            self.pa10Ck.setHidden(True)
            self.shutdown.setHidden(True)
        elif series in ["MM32L0130"]:
            self.bootCk.setHidden(False)
            self.pa10Ck.setHidden(True)
            self.shutdown.setHidden(False)
        elif series in ["MM32F0020"]:
            self.bootCk.setHidden(False)
            self.pa10Ck.setHidden(False)
            self.shutdown.setHidden(True)


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