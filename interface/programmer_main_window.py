import os
import UI.resource_rc
from UI.Ui_mm32program import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLabel, QMessageBox
from PyQt5.QtCore import pyqtSlot, QSettings
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
        self.splitter.setStretchFactor(0, 4)
        self.splitter.setStretchFactor(1, 10)
        self.splitter_2.setStretchFactor(0, 8)
        self.splitter_2.setStretchFactor(1, 2)

        # 展示初始状态栏
        self.showStatue()

        # 其他控件触发的动作同主界面
        self.flash.sigOpenFileDia.connect(self.on_loadProgrammingFile_triggered)
        self.flash.sigSaveFile.connect(self.on_saveProgrammingFile_triggered)
        self.treeWidget.sigSaveProject.connect(self.on_saveProject_triggered)
        self.treeWidget.sigSaveProjectAs.connect(self.on_saveProjectAs_triggered)
        self.treeWidget.sigCloseAll.connect(self.restoreFlashDefault)

    @pyqtSlot()
    def on_openProject_triggered(self): # 装载项目的槽函数(函数名固定)，装载ini信息到treewidget
        filePath, _ = QFileDialog.getOpenFileName(None, "open project", "C:\\", 'MM Programmer Config File(*.ini)')
        if os.path.exists(filePath):
            info = self.treeWidget.openProject(filePath)
            if os.path.exists(info.codeFile): # 谨防装载项目的code file已不存在
                self.loadProgrammerFile(info.codeFile, int(info.flashSize))
            else:
                self.treeWidget.codeFile.setText(1, "")
                self.textBrowser.append(f"data file does not exist--->{info.codeFile} Fail")
            self.textBrowser.append(f"load project--->{filePath} Success")
        else:
            pass

    @pyqtSlot()
    def on_newProject_triggered(self): # 新建项目，展示项目信息到treewidget
        #QMessageBox.question(self, 'TIPS', 'Whether to save the current project?', QMessageBox.Yes | QMessageBox.No)
        newPro = NewProjectDia(self)
        while newPro.exec_():
            if newPro.state:
                info = newPro.getProjectInfo()
                self.treeWidget.showConfiguration(info)
                self.loadProgrammerFile(info.codeFile, int(info.flashSize))
                break
            else:
                pass
    
    @pyqtSlot()
    def on_modifyProject_triggered(self): # 修改项目，打开新建项目的弹框，并将treewidget展示的项目信息填入
        if self.treeWidget.projectName.text(1) != "":
            treeInfo = self.treeWidget.getTreeInfo()
            srcPartName = treeInfo.partName
            srcCodeFile = treeInfo.codeFile

            newPro = NewProjectDia(self)
            newPro.setProjectInfo(treeInfo)
            while newPro.exec_():
                if newPro.state:
                    newInfo = newPro.getProjectInfo()
                    # 修改了flash文件
                    if newInfo.codeFile != srcCodeFile:
                        self.loadProgrammerFile(newInfo.codeFile, int(newInfo.flashSize))
                    else:
                        pass
                    # 修改了part
                    if newInfo.partName != srcPartName:
                        self.treeWidget.showConfiguration(newInfo)
                    else:
                        self.treeWidget.showConfiguration(newInfo, True)
                    break
                else:
                    pass
        else:
            pass
            # self.modifyProject.setDisabled(True)

    @pyqtSlot()
    def on_saveProject_triggered(self): # 保存项目，将treewidget展示的项目信息保存
        filePath, _ = QFileDialog.getSaveFileName(None, "save project", "C:\\", "ini file(*.ini)")
        if filePath != "": # 谨防点击保存，但项目名为空或直接关闭页面的情况
            info = self.treeWidget.getTreeInfo()
            self.saveConfigInfo(filePath, info)
            self.textBrowser.append(f"save project--->{filePath} Success")
        else:
            pass
    
    @pyqtSlot()
    def on_saveProjectAs_triggered(self): # 项目另存为 (目前和保存项目功能一致)
        filePath, _ = QFileDialog.getSaveFileName(None, "save project", "C:\\", "ini file(*.ini)")
        if filePath != "": # 谨防点击保存，但项目名为空或直接关闭页面的情况
            info = self.treeWidget.getTreeInfo()
            self.saveConfigInfo(filePath, info)
            self.textBrowser.append(f"save project--->{filePath} Success")
        else:
            pass

    @pyqtSlot()
    def on_loadProgrammingFile_triggered(self): # 装载编程文件(hex,bin,s19)，选择文件，并展示文件信息到flash
        if self.treeWidget.projectName.text(1) != "":
            filename, _ = QFileDialog.getOpenFileName(self, "seclect file", 'C:\\', "Inter Hex files(*.hex);;Binary files(*.bin);;Motorola files(*.s19)")
            if os.path.exists(filename): # 谨防并未打开文件的情况
                self.loadOrDropShowFile(filename)
            else:
                pass
        else:
            QMessageBox.warning(self, 'Warning', 'Please create a new or open project first!', QMessageBox.Yes)

    @pyqtSlot()
    def on_saveProgrammingFile_triggered(self): # 将数据保存为编码文件
        filePath, _ = QFileDialog.getSaveFileName(self, "save file", "C:\\", "Inter Hex files(*.hex);;Binary files(*.bin);;Motorola files(*.s19)") 
        if filePath != "":
            data = self.flash.saveTableData()
            self.flash.saveCodeFile(filePath, data)
            self.textBrowser.append(f"save data file--->{filePath} Success")
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

    # 将flash恢复为默认值
    def restoreFlashDefault(self):
        self.flash.file = ""
        self.flash.flashSize = 64
        self.flash.act_bit8.setChecked(True)
        self.flash.act_bit16.setChecked(False)
        self.flash.act_bit32.setChecked(False)
        self.flash.insertTable()

    # 保存tree信息为ini文件
    def saveConfigInfo(self, path: str, info: ProjectInfo):
        settings = QSettings(path, QSettings.IniFormat)
        settings.beginGroup("Info")
        settings.setValue("design4", "MM32 Programmer")
        settings.setValue("Version", "1.00")
        settings.setValue("Company", "MindMotion Co., Ltd")
        settings.endGroup()

        settings.beginGroup("Base")
        settings.setValue("projectName", info.projectName)
        settings.setValue("core", info.core)
        settings.setValue("partName", info.partName)
        settings.setValue("flashSize", info.flashSize)
        settings.setValue("filePath", info.codeFile)
        settings.setValue("descript", info.projectDesp)
        settings.endGroup()

        settings.beginGroup("Programmer")
        settings.setValue("programmer", info.programmer)
        settings.setValue("connectType", info.linkMode)
        settings.setValue("resetType", info.resetType)
        settings.setValue("frequence", info.frequence)
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

    # 拖动事件, 不能是管理员模式
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            filepath = urls[0].toLocalFile()
            self.loadOrDropShowFile(filepath)
            event.accept()
    
    # 装载或推拽烧录文件
    def loadOrDropShowFile(self, filePath: str):
        if self.treeWidget.projectName.text(1) != "": # 必须先装载项目或新建项目后才能装载或拖拽code file
            flashSize = int(self.treeWidget.flashSize.text(1)[:len(self.treeWidget.flashSize.text(1)) - 5])
            if filePath.endswith(".hex") or filePath.endswith(".s19") or filePath.endswith(".bin"):
                self.loadProgrammerFile(filePath, flashSize)
                self.textBrowser.append(f"show data file --->{filePath} Success")
            else:
                self.textBrowser.append(f"not supported to show this type of file --->{filePath} Fail")
        else:
            QMessageBox.warning(self, 'Warning', 'Please create a new or open project first!', QMessageBox.Yes)

    # 将烧录文件的内容(addr:data)展示在flash
    def loadProgrammerFile(self, filePath: str, flashSize: int):
        # 更新flash界面的当前装载文件和大小
        self.flash.file = filePath 
        self.flash.flashSize = flashSize
        # 当前为几字节显示
        state = self.flash.getCurrentState()
        if filePath.endswith(".bin"):
            binLoad = OpenBinFile(flashSize, self)
            if binLoad.exec_():
                start = binLoad.start.text()
                end = binLoad.end.text()
                ck = "FF" if binLoad.checkBox.isChecked() else "00"
                data = self.flash.parseFile(filePath, binStart = int(start, 16), binEnd = int(end, 16), size = self.flash.flashSize, state = state, defalut = ck)
                self.flash.insertTable(data, state = state, default = ck)
        else:
            data = self.flash.parseFile(filePath, size = self.flash.flashSize, state = state)
            self.flash.insertTable(data, state = state)


# todo: 
#   1.当新建项目或装载其他项目时，监测当前装载的项目是否改动，若改动则提示是否保存；
#   2.修改项目后，如果芯片型号没变则之前的扇区选择不变，否则扇区全选；
#   3.保存项目，如果是装载项目，并且没有改变则保存项目功能为灰色，若修改了装载的项目
#     和新建项目，可以点保存功能，并且替换其他需要提示是否保存；（线程监测？）