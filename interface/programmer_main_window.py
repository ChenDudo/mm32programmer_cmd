import os
import UI.resource_rc
from UI.Ui_mm32program import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLabel, QMessageBox
from PyQt5.QtCore import pyqtSlot, QSettings, QDateTime, Qt
from PyQt5.QtGui import QPixmap, QDropEvent, QDragEnterEvent
from interface.new_project import NewProjectDia
from interface.open_binfile import OpenBinFile
from interface.project_base_class import ProjectInfo

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

        # 获取新建项目的信息，展示在tree，方便保存项目和用户再新建项目提示保存
        self.info = ProjectInfo()
        # 记录打开的项目，判断是否修改，提示是否需要保存
        self.ini = ""

        self.showStatue()
        self.flash.sigOpenFileDia.connect(self.on_loadProgrammingFile_triggered)
        self.flash.sigSaveFile.connect(self.on_saveProgrammingFile_triggered)
        self.treeWidget.sigSaveProject.connect(self.on_saveProject_triggered)
        self.treeWidget.sigSaveProjectAs.connect(self.on_saveProjectAs_triggered)

    @pyqtSlot()
    def on_openProject_triggered(self): # 当点击打开项目，装载ini信息到tree
        self.treeWidget.closeAll() # 装载项目前情况tree，或提示是否需要保存内容
        info = self.treeWidget.openProject()
        if os.path.exists(info[0]):
            self.loadProgrammerFile(info[1], info[2])
            self.textBrowser.append(f"load project--->{info[0]} Success")
        else:
            pass

    @pyqtSlot()
    def on_newProject_triggered(self): # 当点击新建项目
        newPro = NewProjectDia(self)
        while newPro.exec_():
            if newPro.proName.text() != "" and newPro.filePath.text() != "":
                self.info = newPro.getProjectInfo()
                self.loadProgrammerFile(self.info.codeFile)
                self.treeWidget.showConfiguration(self.info)
                break
            else:
                QMessageBox.warning(newPro, 'Warning', 'The project name and code file cannot be empty!', QMessageBox.Yes)
    
    @pyqtSlot()
    def on_modifyProject_triggered(self): # 修改项目
        self.info.projectName != ""
        pass

    @pyqtSlot()
    def on_saveProject_triggered(self): # 保存项目
        info = self.treeWidget.getTreeInfo() # 主要获取option和sector
        path = self.saveConfigInfo(info)
        if path != "":
            self.textBrowser.append(f"save project--->{path} Success")
        else:
            pass
    
    @pyqtSlot()
    def on_saveProjectAs_triggered(self): # 项目另存为 (目前和保存项目功能一致)
        info = self.treeWidget.getTreeInfo() # 主要获取option和sector
        path = self.saveConfigInfo(info)
        if path != "":
            self.textBrowser.append(f"save project--->{path} Success")
        else:
            pass

    @pyqtSlot()
    def on_loadProgrammingFile_triggered(self): # 装载编程文件(hex,bin,s19)，选择文件，并展示文件信息到flash
        options = QFileDialog().Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, "seclect file", 'C:\\', "Inter Hex files(*.hex);;Binary files(*.bin);;Motorola files(*.s19);;All files(*.*)")

        if os.path.exists(filename): # 谨防并未打开文件的情况
            self.loadProgrammerFile(filename)
        self.textBrowser.append(f"load data--->{filename} Success")

    @pyqtSlot()
    def on_saveProgrammingFile_triggered(self): # 将数据保存为编码文件
        filePath, _ = QFileDialog.getSaveFileName(self, "save file", "C:\\", "Inter Hex files(*.hex);;Binary files(*.bin);;Motorola files(*.s19);;All files(*.*)") 
        if filePath != "":
            data = self.flash.save_table_data()
            self.flash.save_code_file(filePath, data)
            self.textBrowser.append(f"save file--->{filePath} Success")
        else:
            pass

    def showStatue(self):# 状态栏显示
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

    def saveConfigInfo(self, info: ProjectInfo) -> str:
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
            settings.setValue("data0", info.data0)
            settings.setValue("data1", info.data1)
            settings.setValue("watchDog", info.watchDog)
            settings.setValue("stopReset", info.stopMode)
            settings.setValue("standByReset", info.standbyMode)
            settings.endGroup()

            settings.beginGroup("Sectors")
            settings.setValue("Sector", info.sectors)
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
            self.dropAndShowFile(filepath)
            event.accept()
    
    def dropAndShowFile(self, filepath: str):
        if self.treeWidget.projectName.text(1) != "":
            if filepath.endswith(".hex") or filepath.endswith(".s19") or filepath.endswith(".bin"):
                self.loadProgrammerFile(filepath)
                self.textBrowser.append(f"drag and show file --->{filepath} Success")
            else:
                self.textBrowser.append(f"not supported to show this type of file --->{filepath} Fail")
        else:
            QMessageBox.warning(self, 'Warning', 'Please create a new or open project first!', QMessageBox.Yes)

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
