import os
import UI.resource_rc
from UI.Ui_mm32program import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLabel, QMessageBox
from PyQt5.QtCore import pyqtSlot, QSettings, QDateTime, Qt
from PyQt5.QtGui import QPixmap, QDropEvent, QDragEnterEvent
from interface.new_project import NewProjectDia
from interface.open_binfile import OpenBinFile
from interface.project_base_class import ProjectInfo


# 主窗口，主要由treewidget(项目树视图)、flash(显示flash信息的控件)、textBrowser(信息输出台)以及statusBar(状态栏)组成
class Programmer(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Programmer, self).__init__(parent)
        self.setupUi(self)
        self.setMinimumSize(1000,650)
        self.setAcceptDrops(True)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 8)
        self.splitter_2.setStretchFactor(0, 8)
        self.splitter_2.setStretchFactor(1, 2)

        # 装载项目或新建项目在tree展示的项目信息，方便保存项目和用户再新建项目提示保存
        self.info = ProjectInfo()
        # 记录打开的项目，判断是否修改，提示是否需要保存
        self.ini = ""

        # 展示初始状态栏
        self.showStatue()

        # 其他控件触发的动作同主界面
        self.flash.sigOpenFileDia.connect(self.on_loadProgrammingFile_triggered)
        self.flash.sigSaveFile.connect(self.on_saveProgrammingFile_triggered)
        self.treeWidget.sigSaveProject.connect(self.on_saveProject_triggered)
        self.treeWidget.sigSaveProjectAs.connect(self.on_saveProjectAs_triggered)

    @pyqtSlot()
    def on_openProject_triggered(self): # 打开项目的槽函数(函数名固定)，装载ini信息到treewidget
        filePath, _ = QFileDialog.getOpenFileName(None, "open project", "C:\\", 'MM Programmer Config File(*.ini)')
        if os.path.exists(filePath):
            self.info = self.treeWidget.openProject(filePath)
            self.loadProgrammerFile(self.info.codeFile, int(self.info.flashSize))
            self.textBrowser.append(f"load project--->{filePath} Success")
        else:
            pass

    @pyqtSlot()
    def on_newProject_triggered(self): # 新建项目，展示项目信息到treewidget
        #QMessageBox.question(self, 'TIPS', 'Whether to save the current project?', QMessageBox.Yes | QMessageBox.No)
        newPro = NewProjectDia(self)
        while newPro.exec_():
            if newPro.state:
                self.info = newPro.getProjectInfo()
                self.loadProgrammerFile(self.info.codeFile)
                self.treeWidget.showConfiguration(self.info)
                break
            else:
                pass
    
    @pyqtSlot()
    def on_modifyProject_triggered(self): # 修改项目，打开新建项目的弹框，并将treewidget展示的项目信息填入
        self.updataProjectInfo()
        if self.info.projectName != "":
            newPro = NewProjectDia(self)
            newPro.setProjectInfo(self.info)
            while newPro.exec_():
                if newPro.state:
                    self.info = newPro.getProjectInfo()
                    self.loadProgrammerFile(self.info.codeFile)
                    self.treeWidget.showConfiguration(self.info)
                    break
                else:
                    pass

    @pyqtSlot()
    def on_saveProject_triggered(self): # 保存项目，将treewidget展示的项目信息保存
        self.updataProjectInfo()
        path = self.saveConfigInfo()
        if path != "":
            self.textBrowser.append(f"save project--->{path} Success")
        else:
            pass
    
    @pyqtSlot()
    def on_saveProjectAs_triggered(self): # 项目另存为 (目前和保存项目功能一致)
        self.updataProjectInfo()
        path = self.saveConfigInfo()
        if path != "":
            self.textBrowser.append(f"save project--->{path} Success")
        else:
            pass

    @pyqtSlot()
    def on_loadProgrammingFile_triggered(self): # 装载编程文件(hex,bin,s19)，选择文件，并展示文件信息到flash
        filename, _ = QFileDialog.getOpenFileName(self, "seclect file", 'C:\\', "Inter Hex files(*.hex);;Binary files(*.bin);;Motorola files(*.s19)")
        if os.path.exists(filename): # 谨防并未打开文件的情况
            self.loadOrDropShowFile(filename)
        else:
            pass

    @pyqtSlot()
    def on_saveProgrammingFile_triggered(self): # 将数据保存为编码文件
        filePath, _ = QFileDialog.getSaveFileName(self, "save file", "C:\\", "Inter Hex files(*.hex);;Binary files(*.bin);;Motorola files(*.s19)") 
        if filePath != "":
            data = self.flash.save_table_data()
            self.flash.save_code_file(filePath, data)
            self.textBrowser.append(f"save file--->{filePath} Success")
        else:
            pass

    # 状态栏显示
    def showStatue(self):
        link = QLabel()
        link.setText("Programmer: MM32LinkDAP-V1 ")
        linkIcon = QLabel()
        linkIcon.setPixmap(QPixmap(":/icon/icon/disConnect.png"))

        chip = QLabel()
        chip.setText("Part No.: MM32F0100C3P ")
        chipIcon = QLabel()
        chipIcon.setPixmap(QPixmap(":/icon/icon/noChip.png"))

        lockIcon = QLabel()
        lockIcon.setPixmap(QPixmap(":/icon/icon/unlock.png"))

        self.statusBar().addPermanentWidget(linkIcon, stretch=0)
        self.statusBar().addPermanentWidget(link, stretch=2)
        self.statusBar().addPermanentWidget(chipIcon, stretch=0)
        self.statusBar().addPermanentWidget(chip, stretch=2)
        self.statusBar().addPermanentWidget(lockIcon, stretch=6)

    def saveConfigInfo(self) -> str:
        filePath, _ = QFileDialog.getSaveFileName(None, "save project", "C:\\", "ini file(*.ini)")
        if filePath != "":
            settings = QSettings(filePath, QSettings.IniFormat)
            settings.beginGroup("Info")
            settings.setValue("design4", "MM32 Programmer")
            settings.setValue("Version", "1.00")
            settings.setValue("Company", "MindMotion Co., Ltd")
            settings.endGroup()

            settings.beginGroup("Base")
            settings.setValue("projectName", self.info.projectName)
            settings.setValue("core", self.info.core)
            settings.setValue("familyName", self.info.series)
            settings.setValue("partName", self.info.partName)
            settings.setValue("flashSize", self.info.flashSize)
            settings.setValue("filePath", self.info.codeFile)
            settings.setValue("descript", self.info.projectDesp)
            settings.setValue("dateTime", QDateTime.currentDateTime().toString(Qt.ISODate))
            settings.endGroup()

            settings.beginGroup("Programmer")
            settings.setValue("programmer", self.info.programmer)
            settings.setValue("connectType", self.info.linkMode)
            settings.setValue("resetType", self.info.resetType)
            settings.setValue("frequence", self.info.frequence)
            settings.endGroup()

            settings.beginGroup("Option")
            settings.setValue("data0", self.info.data0)
            settings.setValue("data1", self.info.data1)
            settings.setValue("watchDog", self.info.watchDog)
            settings.setValue("stopReset", self.info.stopMode)
            settings.setValue("standByReset", self.info.standbyMode)
            settings.endGroup()

            settings.beginGroup("Sectors")
            settings.setValue("Sector", self.info.sectors)
            settings.endGroup()

        return filePath

    #拖动事件, 不能是管理员模式
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            filepath = urls[0].toLocalFile()
            self.loadOrDropShowFile(filepath)
            event.accept()
    
    def loadOrDropShowFile(self, filepath: str):
        if self.treeWidget.projectName.text(1) != "":
            if filepath.endswith(".hex") or filepath.endswith(".s19") or filepath.endswith(".bin"):
                self.loadProgrammerFile(filepath)
                self.textBrowser.append(f"load or drag and show file --->{filepath} Success")
            else:
                self.textBrowser.append(f"not supported to show this type of file --->{filepath} Fail")
        else:
            QMessageBox.warning(self, 'Warning', 'Please create a new or open project first!', QMessageBox.Yes)

    # 将烧录文件的内容(addr:data)展示在flash
    def loadProgrammerFile(self, filepath: str, flashSize = 0):
        if filepath != "" and os.path.exists(filepath):
            self.flash.file = filepath
            if flashSize != 0: # 读取项目的情况
                self.flash.flashSize = flashSize
            else:
                self.flash.flashSize = int(self.info.flashSize)
            state = self.flash.getCurrentState()
            if filepath.endswith(".bin"):
                binLoad = OpenBinFile(int(self.info.flashSize), self)
                if binLoad.exec_():
                    start = binLoad.start.text()
                    end = binLoad.end.text()
                    ck = "FF" if binLoad.checkBox.isChecked() else "00"
                    data = self.flash.parse_file(filepath, binStart = int(start, 16), binEnd = int(end, 16), size = self.flash.flashSize, state = state, defalut = ck)
                    self.flash.insert_table(data, state = state, default = ck)
            else:
                data = self.flash.parse_file(filepath, size = self.flash.flashSize, state = state)
                self.flash.insert_table(data, state = state)
        else:
            # self.textBrowser.append(f"file path not exit--->{filepath} failed")
            pass

    # tree部分的项目信息由两部分组成，self.info存储不可修改部分内容；opInfo是可修改部分，获取当前内容；再存储给self.info
    # 使用情景：保存项目，修改项目
    def updataProjectInfo(self):
        opInfo = self.treeWidget.getTreeInfo() # 主要获取option和sector
        self.info.data0 = opInfo.data0
        self.info.data1 = opInfo.data1
        self.info.watchDog = opInfo.watchDog
        self.info.standbyMode = opInfo.standbyMode
        self.info.stopMode = opInfo.stopMode
        self.info.sectors = opInfo.sectors


# todo: 
#   1.当新建项目或装载其他项目时，监测当前装载的项目是否改动，若改动则提示是否保存；
#   2.修改项目后，如果芯片型号没变则之前的扇区选择不变，否则扇区全选；