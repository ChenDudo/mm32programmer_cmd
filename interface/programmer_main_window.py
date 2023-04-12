import re
import os
import json
import typing
import UI.resource_rc
from UI.Ui_mm32program import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLabel, QMessageBox, QTabBar, QMenu, QAction
from PyQt5.QtCore import pyqtSlot, QSettings, QSize, Qt
from PyQt5.QtGui import QPixmap, QDropEvent, QDragEnterEvent, QIcon, QFont, QCursor
from interface.new_project import NewProjectDia
from interface.read_flash import NewTable
from interface.open_binfile import OpenBinFile
from interface.project_base_class import ProjectInfo
from interface.new_thread import WriteThread, EraseThread, ReadThread, BlankThread, VerityThread, OptByteThread
from interface.merge_file import MergeFile
from interface.progress_dialog import ProgressDialog
from interface.config_link import ConfigLink
import interface.pyocd_api as api

# 主窗口，主要由treewidget(项目树视图)、flash(显示flash信息的控件)、textBrowser(信息输出台)以及statusBar(状态栏)组成
class Programmer(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(Programmer, self).__init__(parent)
        self.setupUi(self)
        self.setMinimumSize(1000,650)
        self.setAcceptDrops(True)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)
        self.splitter_2.setStretchFactor(0, 8)
        self.splitter_2.setStretchFactor(1, 2)

        # 信息和状态
        self.info = ProjectInfo() # 装载项目内容
        self.ini = "" # 记录装载的项目名
        self.state = False # 是否装载项目是否修改
        self.speed = 1000000 # link speed，目前默认1M，后期改为配置信息存储，读取

        self.setFont(QFont("Courier New",9))
        self.textBrowser.setContextMenuPolicy(Qt.CustomContextMenu)
        self.textBrowser.customContextMenuRequested.connect(self.slotShowMenu)

        self.tabWidget.setTabsClosable(True) # 设置table页面可关闭
        self.tabWidget.tabBar().setTabButton(0, QTabBar.RightSide, None) # flash页面不能关闭
        self.tabWidget.tabCloseRequested.connect(self.tabClose)

        # 展示初始状态栏和工具栏icon大小设置
        self.chipLink.setIcon(QIcon(":/icon/icon/chipNotMatch.png"))
        self.toolBar.setIconSize(QSize(18, 18))
        self.showState()

        # 动作初始状态
        self.checkLink.setIcon(QIcon(":/icon/icon/connect.png"))
        self.enableAction(False)

        self.flash.sigOpenFileDia.connect(self.on_loadProgrammingFile_triggered)
        self.flash.sigSaveFile.connect(self.on_saveProgrammingFile_triggered)
        self.flash.sigReadData.connect(self.on_readChip_triggered)
        self.flash.sigWriteData.connect(self.on_writeChip_triggered)
        self.treeWidget.sigSaveProject.connect(self.on_saveProject_triggered)
        self.treeWidget.sigSaveProjectAs.connect(self.on_saveProjectAs_triggered)
        self.treeWidget.sigCloseAll.connect(self.on_closeProject_triggered)
        self.treeWidget.sigNewProject.connect(self.on_newProject_triggered)
        self.treeWidget.sigOpenProject.connect(self.on_openProject_triggered)
        self.treeWidget.sigTableIndex.connect(self.clickShowTable)
        self.tabWidget.currentChanged.connect(self.selectFlashTab)

    @pyqtSlot()
    def on_openProject_triggered(self): # 装载项目的槽函数(函数名固定)，装载ini信息到treewidget
        self.judgeToSave(self.openProjectSolt)

    def openProjectSolt(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Open Project", "C:\\", 'MM Programmer Config File(*.ini)')
        if os.path.exists(filePath):
            self.enableChip(False)
            info = self.treeWidget.openProject(filePath)
            self.clearTab()
            self.clearFlash(int(info.flashSize))
            self.ini = filePath
            self.info = info
            if os.path.exists(info.codeFile): # 谨防装载项目的code file已不存在
                self.loadProgrammerFile(info.codeFile, int(info.flashSize))
                self.successOutput(f"Load Project ---> {info.projectName}@{filePath} Success")
            else:
                self.treeWidget.codeFile.setText(1, "")
                self.successOutput(f"Load Project ---> {info.projectName}@{filePath} Success")
                self.failureOutput(f"\u00a0\u00a0\u00a0\u00a0data file({info.codeFile}) does not exist and file loading Failure")
            self.enableAction(True) # 右击菜单
        else:
            pass

    @pyqtSlot()
    def on_newProject_triggered(self): # 新建项目，展示项目信息到treewidget
        self.judgeToSave(self.newProjectSolt)

    def newProjectSolt(self):
        newPro = NewProjectDia(self)
        while newPro.exec_():
            if newPro.state:
                info = newPro.getProjectInfo()
                self.treeWidget.showConfiguration(info)
                self.clearTab()
                self.clearFlash(int(info.flashSize))
                self.loadProgrammerFile(info.codeFile, int(info.flashSize))
                self.enableAction(True)
                self.ini = ""
                self.info = ProjectInfo()
                self.state = False
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
            newPro.setWindowTitle("Modify Project")
            newPro.setProjectInfo(treeInfo)
            while newPro.exec_():
                if newPro.state:
                    newInfo = newPro.getProjectInfo()
                    # 修改了part
                    if newInfo.partName != srcPartName: # flash清空 和 tab页删除，重新加载data file
                        self.clearFlash(int(newInfo.flashSize))
                        self.clearTab()
                        self.loadProgrammerFile(newInfo.codeFile, int(newInfo.flashSize))
                        self.treeWidget.showConfiguration(newInfo)
                    else:
                        self.treeWidget.showConfiguration(newInfo, True)
                    # 修改了data file文件
                    if newInfo.codeFile != srcCodeFile:
                        self.loadProgrammerFile(newInfo.codeFile, int(newInfo.flashSize))
                    else:
                        pass
                    break
                else:
                    pass
        else:
            pass

    @pyqtSlot()
    def on_saveProject_triggered(self): # 保存项目，将treewidget展示的项目信息保存
        if os.path.exists(self.ini):
            info = self.treeWidget.getTreeInfo()
            self.saveConfigInfo(self.ini, info)
            self.info = info
            self.successOutput(f"Save Project ---> {info.projectName}@{self.ini} Success")
        else:
            filePath, _ = QFileDialog.getSaveFileName(None, "Save Project", "C:\\", "ini file(*.ini)")
            if filePath != "": # 谨防点击保存，但项目名为空或直接关闭页面的情况
                info = self.treeWidget.getTreeInfo()
                self.saveConfigInfo(filePath, info)
                # 保存后，相当于当前装载项目
                self.ini = filePath
                self.info = info
                self.successOutput(f"Save Project ---> {info.projectName}@{filePath} Success")
            else:
                pass
    
    @pyqtSlot()
    def on_saveProjectAs_triggered(self): # 项目另存为 (目前和保存项目功能一致)
        filePath, _ = QFileDialog.getSaveFileName(None, "Save Project As", "C:\\", "ini file(*.ini)")
        if filePath != "": # 谨防点击保存，但项目名为空或直接关闭页面的情况
            info = self.treeWidget.getTreeInfo()
            self.saveConfigInfo(filePath, info)
            self.successOutput(f"Save Project As ---> {info.projectName}@{filePath} Success")
        else:
            pass

    @pyqtSlot()
    def on_loadProgrammingFile_triggered(self): # 装载编程文件(hex,bin,s19)，选择文件，并展示文件信息到flash
        if self.treeWidget.projectName.text(1) != "":
            filename, _ = QFileDialog.getOpenFileName(self, "Select Data File", 'C:\\', "Inter Hex files(*.hex);;Binary files(*.bin);;Motorola files(*.s19)")
            if os.path.exists(filename): # 谨防并未打开文件的情况
                self.loadOrDropShowFile(filename)
            else:
                pass
        else:
            QMessageBox.warning(self, 'Warning', 'Please create a new or open project first!', QMessageBox.Yes)

    @pyqtSlot()
    def on_saveProgrammingFile_triggered(self): # 将数据保存为编码文件，检查是tabwidget哪个页面发出的信号
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Data File", "C:\\", "Inter Hex files(*.hex);;Binary files(*.bin);;Motorola files(*.s19)") 
        if filePath != "":
            index = self.tabWidget.currentIndex()
            (path, name) = os.path.split(filePath)
            if index == 0:
                data = self.flash.saveTableDataAsDict(self.flash.table)
                self.flash.saveCodeFile(filePath, data)
            else:
                table = self.tabWidget.currentWidget()
                dataDict = table.dataToDict()
                table.saveCodeFile(filePath, dataDict)
            self.successOutput(f"Save Data File ---> {name}@{filePath} Success")
        else:
            pass
    
    @pyqtSlot()
    def on_checkLink_triggered(self): # 检测linker连接状态
        state = self.checkLinkSolt()
        if state:
            self.successOutput("Connect Programmer ---> Success")
        else:
            self.failureOutput("Connect Programmer ---> Failure")
    
    def checkLinkSolt(self):
        state = api.checkLink(self.speed)
        if state:
            linkName = self.getLinkName()
            self.link.setText(f"Programmer: {linkName}")
            self.linkIcon.setPixmap(QPixmap(":/icon/icon/disConnect.png"))
            self.checkLink.setIcon(QIcon(":/icon/icon/disConnect.png"))
            self.chipLink.setEnabled(True)
        else:
            self.link.setText("Programmer: No connect")
            self.linkIcon.setPixmap(QPixmap(":/icon/icon/connect.png"))
            self.checkLink.setIcon(QIcon(":/icon/icon/connect.png"))
            self.chipLink.setEnabled(False)

        return state

    # 识别link名，连接link的下标，先默认为第一个link(0)
    def getLinkName(self, index = 0):
        scanlist = os.path.join(os.getcwd(), "scanlist.json")
        scanName = ""
        with open(scanlist, "r") as f:
            scanInfo = json.load(f)
            scanName = scanInfo[str(index)].split(",")[1]
        return scanName

    @pyqtSlot()
    def on_chipLink_triggered(self): # 获取link连接的单片机系列
        series = self.chipLinkSolt()
        if series != None:
            self.successOutput(f"Connect Chip ---> {series} Success")
        else:
            pass
    
    def chipLinkSolt(self):
        state = self.checkLinkSolt()
        if state:
            partName = self.treeWidget.chipName.text(1)
            if partName == "":
                QMessageBox.warning(self, "Warning", "Please create or load project first!", QMessageBox.Yes)
            else:
                newPro = NewProjectDia(self)
                series = newPro.getSeriesFromChip(partName)
                mcu = api.recognizeMCU(self.speed)
                if isinstance(mcu, list):
                    if series in mcu:
                        self.chip.setText(f"Part No. : {series} ")
                        self.enableChip(True)
                        self.chipIcon.setPixmap(QIcon(":/icon/icon/chip.png").pixmap(19, 19))
                        self.chipLink.setIcon(QIcon(":/icon/icon/chip.png"))
                        return series
                    else:
                        self.failureOutput(f"Connect Chip ---> the connect chip in ({str(mcu)[1:-1]}) mismatch project chip@{series} Failure")
                        self.enableChip(False)
                        self.chip.setText(f"Part No. : {mcu[0]}")
                        self.chipIcon.setPixmap(QIcon(":/icon/icon/chipNotMatch.png").pixmap(19, 19))
                        self.chipLink.setIcon(QIcon(":/icon/icon/chipNotMatch.png"))
                else:
                    if mcu == 1:
                        self.failureOutput("Connect Chip ---> not connected to any chip Failure")
                    elif mcu == 2:
                        self.failureOutput("Connect Chip ---> not supported to project chip Failure")
                    self.enableChip(False)
                    self.chip.setText("Part No. : No Detect")
                    self.chipIcon.setPixmap(QIcon(":/icon/icon/chipNotMatch.png").pixmap(19, 19))
                    self.chipLink.setIcon(QIcon(":/icon/icon/chipNotMatch.png"))
        else:
            self.failureOutput("Connect Programmer ---> Failure")

    @pyqtSlot()
    def on_readChip_triggered(self): 
        precedentInfo = self.checkPrecedentConnect("Read Chip ---> Failure")
        if precedentInfo == None:
            pass
        else:
            self.tabWidget.setCurrentIndex(0)
            series = precedentInfo[0]
            sectorsDict = precedentInfo[1]
            steps = precedentInfo[2]
            fsize = int(self.treeWidget.flashSize.text(1)[:-5])
            self.readDataSlot(series, fsize, sectorsDict, steps)

    def readDataSlot(self, series: str, fsize: int, sectors: dict, length: int):
        self.successOutput(f"Read Chip ---> Start, Size:{length}Bytes")
        # 进度条弹窗
        progressDia = ProgressDialog(self, length)
        progressDia.sigOutPut.connect(self.failureOutput)
        # 线程按扇区读取芯片
        self.ReadThread = ReadThread(series, sectors, fsize, self.speed)
        self.ReadThread.signalData.connect(self.loadFlashData)
        self.ReadThread.signalOutPut.connect(self.successOutput)
        self.ReadThread.signalProgress.connect(progressDia.updataProgress)
        self.ReadThread.signalFail.connect(progressDia.errorAndClose)
        self.ReadThread.start() 
        if progressDia.exec_():
            pass

    @pyqtSlot()
    def on_eraseChip_triggered(self): # 整片擦除
        series = self.chipLinkSolt() 
        if series is None:
            self.enableChip(False)
            self.failureOutput("Erase Chip ---> Failure")
        else:
            flashSize = int(self.treeWidget.flashSize.text(1)[:-5])
            self.eraseSectorSlot(series, {}, flashSize, flashSize * 1024)
    
    @pyqtSlot()
    def on_eraseSector_triggered(self): 
        precedentInfo = self.checkPrecedentConnect("Erase Chip ---> Failure")
        if precedentInfo == None:
            pass
        else:
            series = precedentInfo[0]
            sectorsDict = precedentInfo[1]
            steps = precedentInfo[2]
            fsize = int(self.treeWidget.flashSize.text(1)[:-5])
            self.eraseSectorSlot(series, sectorsDict, fsize, steps)
    
    def eraseSectorSlot(self, series: str, sectors: dict, fsize: int, length: int):
        if len(sectors):
            self.successOutput(f"Erase Chip Sector ---> Start, Size:{length}Bytes")
        # 进度条弹窗
        progressDia = ProgressDialog(self, length)
        progressDia.sigOutPut.connect(self.failureOutput)
        # 线程按扇区擦除芯片
        self.EraseThread = EraseThread(series, sectors, fsize, self.speed)
        self.EraseThread.signalProgress.connect(progressDia.updataProgress)
        self.EraseThread.signalOutPut.connect(self.successOutput)
        self.EraseThread.signalFail.connect(progressDia.errorAndClose)
        self.EraseThread.start() 
        if progressDia.exec_():
            pass

    @pyqtSlot()
    def on_writeChip_triggered(self): # 按扇区读取，连续的扇区会一起读
        precedentInfo = self.checkPrecedentConnect("Write Chip ---> Failure")
        if precedentInfo == None:
            pass
        else:
            series = precedentInfo[0]
            sectorsDict = precedentInfo[1]
            steps = precedentInfo[2]
            curIndex = self.tabWidget.currentIndex()
            codeFile = self.treeWidget.codeFile.text(1)
            if curIndex == 0 and not os.path.exists(codeFile):
                QMessageBox.warning(self, "Warning", "There is no file to write chip ! (current data file does not exist)")
            else:
                if curIndex != 0:
                    table = self.tabWidget.currentWidget()
                    data = table.fdata
                    file = self.tabWidget.tabText(curIndex)
                else:
                    flashSize = int(self.treeWidget.flashSize.text(1)[:-5])
                    self.loadProgrammerFile(codeFile, flashSize) # table存在则更新，不存在则新建
                    data = self.tabWidget.currentWidget().fdata
                    file = codeFile
                # 开始写flash
                self.writeDataSlot(series, sectorsDict, data, file, steps)

    def writeDataSlot(self, series: str, sectors: dict, data: list, file: str, length: int):
        self.successOutput(f"Write Chip ---> Start, Write data file:{file}, Size:{length}Bytes")
        # 进度条弹窗
        progressDia = ProgressDialog(self, length)
        progressDia.sigOutPut.connect(self.failureOutput)
        # 开启读芯片的线程
        self.writeThread = WriteThread(series, sectors, data, self.speed)
        self.writeThread.signalProgress.connect(progressDia.updataProgress)
        self.writeThread.signalOutPut.connect(self.successOutput)
        self.writeThread.sigalFail.connect(progressDia.errorAndClose)
        self.writeThread.start() # run, 运行结束后进程会自行退出
        if progressDia.exec_():
            pass

    @pyqtSlot()
    def on_mergeFile_triggered(self):
        length = int(self.treeWidget.flashSize.text(1)[:-5]) * 1024
        mergeDia = MergeFile(self, length)
        mergeDia.sigMergeFile.connect(self.flash.saveCodeFile) 
        mergeDia.sigSaveFile.connect(self.successOutput)
        if mergeDia.exec_():
            pass

    @pyqtSlot()
    def on_reloadFile_triggered(self):
        index = self.tabWidget.currentIndex()
        filePath = self.tabWidget.tabText(index)
        if os.path.exists(filePath):
            flashSize = int(self.treeWidget.flashSize.text(1)[:-5])
            self.loadProgrammerFile(filePath, flashSize)
            self.successOutput(f"Reload Data From File ---> {filePath} Success")
        else:
            self.failureOutput(f"Reload Data From File ---> file@{filePath} does not exist Failure")

    @pyqtSlot()
    def on_linkCfg_triggered(self):
        linkCfgDia = ConfigLink(self, self.speed)
        linkFile = linkCfgDia.findDETAILSFile()
        if linkFile == None:
            QMessageBox.warning(self, "Warning", "Please check that linker is connected!", QMessageBox.Yes)
        else:
            linkCfgDia.signalSpeed.connect(self.updataSpeed)
            if linkCfgDia.exec_():
                pass

    def updataSpeed(self, speed: int):
        self.speed = speed

    @pyqtSlot()
    def on_chipBlank_triggered(self): # 检查是否为空白片子
        series = self.chipLinkSolt() 
        if series is None:
            self.enableChip(False)
            self.failureOutput("Chip Blank ---> Failure")
        else:
            length = int(self.treeWidget.flashSize.text(1)[:-5]) * 1024
           # 进度条弹窗
            progressDia = ProgressDialog(self, length)
            progressDia.sigOutPut.connect(self.failureOutput)
            progressDia.sigNormalOutPut.connect(self.successOutput)
            # 线程按扇区读取芯片
            self.BlankThread = BlankThread(series, length, self.speed)
            self.BlankThread.signalProgress.connect(progressDia.updataProgress)
            self.BlankThread.signalClose.connect(progressDia.normalAndClose)
            self.BlankThread.signalFail.connect(progressDia.errorAndClose)
            self.BlankThread.start() 
            if progressDia.exec_():
                pass

    @pyqtSlot()
    def on_verifyChip_triggered(self): # 验证芯片的数据和当前页的数据是否一致
        series = self.chipLinkSolt() # 检查芯片是否连接
        if series is None:
            self.enableChip(False)
            self.failureOutput("Chip Verify ---> Failure")
        else:
            length = int(self.treeWidget.flashSize.text(1)[:-5]) * 1024
            index = self.tabWidget.currentIndex()
            if index == 0:
                data = self.flash.flashData
            else:
                table = self.tabWidget.currentWidget()
                data = table.fdata
            self.verifyChipSlot(series, length, data)
    
    def verifyChipSlot(self, series: str, length: int, data: list):
        # 进度条弹窗
        progressDia = ProgressDialog(self, length)
        progressDia.sigOutPut.connect(self.failureOutput)
        progressDia.sigNormalOutPut.connect(self.successOutput)
        # 线程按扇区读取芯片
        self.VerityThread = VerityThread(series, length, data, self.speed)
        self.VerityThread.signalFail.connect(progressDia.errorAndClose)
        self.VerityThread.signalProgress.connect(progressDia.updataProgress)
        self.VerityThread.signalClose.connect(progressDia.normalAndClose)
        self.VerityThread.start() 
        if progressDia.exec_():
            pass

    @pyqtSlot()
    def on_programmeChip_triggered(self): # 综合功能，与sequence的勾选有关
        precedentInfo = self.checkPrecedentConnect("Program Chip ---> Failure")
        if precedentInfo == None:
            pass
        else:
            series = precedentInfo[0]
            sectorsDict = precedentInfo[1]
            steps = precedentInfo[2]
            state = self.treeWidget.getSequenceState()
            if True in state:
                self.successOutput("Program Chip ---> Start")
                if state[3] and (not state[0]) and (not state[1]) and (not state[2]): # 只设置读安全锁
                    if series == "MM32F0130":
                        optAddr = 0x1FFE0000
                        optData = [0x7F80, 0xFF00]
                    else:
                        optAddr = 0x1FFFF800
                        optData = [0xDE21]
                    self.optByteSlot(optAddr, optData) # f0130 api.optWrite(0x1FFE0000, [0x7F80, 0xFF00])
                else:
                    if state[1] or state[2]: # 需要数据
                        curIndex = self.tabWidget.currentIndex()
                        codeFile = self.treeWidget.codeFile.text(1)
                        if curIndex == 0 and not os.path.exists(codeFile):
                            QMessageBox.warning(self, "Warning", "There is no data file to write or verity chip ! (current data file does not exist)")
                            return
                        else:
                            if curIndex != 0:
                                table = self.tabWidget.currentWidget()
                                data = table.fdata
                                file = self.tabWidget.tabText(curIndex)
                            else:
                                flashSize = int(self.treeWidget.flashSize.text(1)[:-5])
                                self.loadProgrammerFile(codeFile, flashSize) # table存在则更新，不存在则新建
                                data = self.tabWidget.currentWidget().fdata
                                file = codeFile
                    else:
                        pass
                    flashSize = int(self.treeWidget.flashSize.text(1)[:-5])
                    if state[0]: # 擦除
                        sectorStr = self.treeWidget.getSectorsChoice(self.treeWidget.sectors)
                        if "0" in sectorStr: 
                            self.eraseSectorSlot(series, sectorsDict, flashSize, steps)
                        else:
                            self.eraseSectorSlot(series, {}, flashSize, flashSize * 1024)
                    if state[1]: # 写
                        self.writeDataSlot(series, sectorsDict, data, file, steps)
                        optData = self.treeWidget.getOptionByteData()
                        if series == "MM32F0130":
                            optData[0] = 0xFFFF
                        api.optWrite(0x1FFFF800, optData, self.speed)
                    if state[2]: # 验证
                        self.verifyChipSlot(series, flashSize * 1024, data)
                    if state[3]: # 加读保护
                        if series == "MM32F0130":
                            optAddr = 0x1FFE0000
                            optData = [0x7F80, 0xFF00]
                        else:
                            optAddr = 0x1FFFF800
                            optData = [0xDE21]
                        self.optByteSlot(optAddr, optData)
                self.successOutput("Program Chip ---> End")
            else:
                QMessageBox.warning(self, "Warning", "please select operation in sequence!", QMessageBox.Yes)
    
    def optByteSlot(self, addr: int, data: list):
        # 进度条弹窗
        progressDia = ProgressDialog(self, 100)
        progressDia.label.setText("write option byte")
        progressDia.progressBar.setFormat("%v%")
        progressDia.sigOutPut.connect(self.failureOutput)
        progressDia.sigNormalOutPut.connect(self.successOutput)
        # 线程按扇区读取芯片
        self.OptByteThread = OptByteThread(addr, data, self.speed)
        self.OptByteThread.signalFail.connect(progressDia.errorAndClose)
        self.OptByteThread.signalProgress.connect(progressDia.updataProgress)
        self.OptByteThread.signalClose.connect(progressDia.normalAndClose)
        self.OptByteThread.start() 
        if progressDia.exec_():
            pass

    @pyqtSlot()
    def on_about_triggered(self): # 解除读保护 66846975, 16711935
        print("----------------------------------")
        api.readAnyMemory(0x1FFE0000, 10, self.speed)
        api.readAnyMemory(0x1FFFF800, 10, self.speed)
        self.treeWidget.getOptionByteData()
        print("----------------------------------")
        

    # 状态栏显示
    def showState(self):
        self.link = QLabel()
        self.link.setText("Programmer: No connect")
        self.linkIcon = QLabel()
        self.linkIcon.setPixmap(QPixmap(":/icon/icon/connect.png"))

        self.chip = QLabel()
        self.chip.setText("Part No. : No Detect")
        self.chipIcon = QLabel()
        self.chipIcon.setPixmap(QIcon(":/icon/icon/chipNotMatch.png").pixmap(20,20))

        self.statusBar().addPermanentWidget(self.linkIcon, stretch=0)
        self.statusBar().addPermanentWidget(self.link, stretch=2)
        self.statusBar().addPermanentWidget(self.chipIcon, stretch=0)
        self.statusBar().addPermanentWidget(self.chip, stretch=8)

    @pyqtSlot()
    def on_closeProject_triggered(self): # 关闭项目
        self.flash.flashData = [0xff for _ in range(32768)]
        self.flash.flashSize = 32
        self.flash.optData = ["FF" for _ in range(64)]
        self.flash.act_bit8.setChecked(True)
        self.flash.act_bit16.setChecked(False)
        self.flash.act_bit32.setChecked(False)
        self.flash.insertTable(self.flash.table)
        self.flash.insertOptData()

        # 清空装载的内容
        self.ini = ""
        self.info = ProjectInfo()
        self.state = False

        # 清空除了flash的页
        self.clearTab()

        # 清空treewidget
        self.treeWidget.showConfiguration(self.info)
        self.treeWidget.dataCK.setText(1, "")
        self.treeWidget.fileCRC.setText(1, "")
        self.treeWidget.dataCRC.setText(1, "")

        # 清除状态栏读取的芯片
        self.chip.setText("Part No. : No Detect")
        self.chipLink.setIcon(QIcon(":/icon/icon/chipNotMatch.png"))
        self.chipIcon.setPixmap(QIcon(":/icon/icon/chipNotMatch.png").pixmap(19, 19))

        self.enableAction(False)

    # textbrower右击菜单
    def slotShowMenu(self):
        actClear = QAction("Clear")
        actSaveLog = QAction("Save Log")
        actClear.triggered.connect(self.textBrowser.clear)
        actSaveLog.triggered.connect(self.saveAsLog)
        menu = QMenu(self.textBrowser)
        menu.addAction(actClear)
        menu.addAction(actSaveLog)
        menu.exec_(QCursor.pos())
    
    # 保存日志
    def saveAsLog(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Log", "C:\\", "Log files(*.log)")
        if filePath != "":
            logData = self.textBrowser.toPlainText()
            with open(filePath, "w") as f:
                f.write(logData)
            self.successOutput(f"Save Log ---> file@{filePath} Success")
        else:
            pass
    
    # 扇区单击，tablewidget展示相应行数
    def clickShowTable(self, row):
        index = self.tabWidget.currentIndex()
        if index == 0:
            state = self.flash.getCurrentState()
            self.flash.table.verticalScrollBar().setSliderPosition(int(row/16/state))
        elif index > 0:
            table = self.tabWidget.widget(index)
            state = table.getCurrentState()
            table.verticalScrollBar().setSliderPosition(int(row/16/state))
        else:
            pass

    # 页面切换到flash的信号
    def selectFlashTab(self):
        index = self.tabWidget.currentIndex()
        if index == 0:
            self.reloadFile.setEnabled(False)
        else:
            self.reloadFile.setEnabled(True)

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

        settings.beginGroup("Option")
        settings.setValue("data0", info.data0)
        settings.setValue("data1", info.data1)
        settings.setValue("watchDog", info.watchDog)
        settings.setValue("stopReset", info.stopMode)
        settings.setValue("standByReset", info.standbyMode)
        settings.setValue("nBoot1", info.nboot)
        settings.setValue("PA10Rest", info.nboot)
        settings.setValue("shutdownByRest", info.nboot)
        settings.endGroup()

        settings.beginGroup("Sequence")
        settings.setValue("erase", info.erase)
        settings.setValue("programme", info.program)
        settings.setValue("verify", info.verify)
        settings.setValue("security", info.security)
        settings.endGroup()

        settings.beginGroup("Sectors")
        settings.setValue("Sector", info.sectors)
        settings.endGroup()

        settings.beginGroup("Lock")
        settings.setValue("Sector", info.lock)
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
            flashSize = int(self.treeWidget.flashSize.text(1)[:-5])
            if filePath.endswith(".hex") or filePath.endswith(".s19") or filePath.endswith(".bin"):
                self.loadProgrammerFile(filePath, flashSize)
                self.successOutput(f"Load Data File ---> {filePath} Success")
            else:
                suffix = os.path.splitext(filePath)[-1]
                self.failureOutput(f"Load Data File ---> suffix@{suffix} of file@{filePath} is not supported Failure")
        else:
            QMessageBox.warning(self, 'Warning', 'Please create a new or open project first!', QMessageBox.Yes)

    # 将烧录文件的内容(addr:data)展示在flash
    def loadProgrammerFile(self, filePath: str, flashSize: int):
        if os.path.exists(filePath):
            tablesDict = self.getTabWidgetChildren()
            if filePath in list(tablesDict): # 存在则更新数据
                index = tablesDict[filePath]
                table = self.tabWidget.widget(index)
                state = table.getCurrentState()
                table.parseData() # 更新数据
                data = table.processTableData(state) # 按字节处理数据
                table.insertTable(table, data, state = state) # 重新插入
                self.tabWidget.setCurrentIndex(index)
            else: # 不存在则重新创建
                table = NewTable(self.tabWidget, filePath, flashSize)
                table.sigTableOpenFileDia.connect(self.on_loadProgrammingFile_triggered)
                table.sigTableSaveFile.connect(self.on_saveProgrammingFile_triggered)
                table.sigReloadDataFile.connect(self.on_reloadFile_triggered)
                state = table.getCurrentState()
                if filePath.endswith(".bin"):
                    binLoad = OpenBinFile(flashSize, self)
                    if binLoad.exec_():
                        start = binLoad.start.text()
                        end = binLoad.end.text()
                        ck = "FF" if binLoad.checkBox.isChecked() else "00"
                        table.parseData(int(start, 16), int(end, 16), int(ck, 16))
                        data = table.processTableData(state)
                        table.insertTable(table, data, state = state)
                        self.tabWidget.addTab(table, filePath)
                        self.tabWidget.setCurrentWidget(table)
                else:
                    table.parseData()
                    data = table.processTableData(state)
                    table.insertTable(table, data, state = state)
                    self.tabWidget.addTab(table, filePath)
                    self.tabWidget.setCurrentWidget(table)
        else: # 新建项目时没有选择code file
            state = self.flash.getCurrentState()
            self.flash.insertTable(self.flash.table, state = state)
            self.flash.insertOptData(state = state)

    # 读取单片机的内容， 目前只能按字节读取
    def loadFlashData(self, flashData: list, optData: list, size = 32):
        self.flash.flashData = flashData
        self.flash.flashSize = size
        state = self.flash.getCurrentState()
        flash = self.flash.parseFlash(flashData, size=size, state=state)
        self.flash.insertTable(self.flash.table, flash, state=state)
        self.flash.processOptData(optData)
        self.flash.insertOptData(state)

    # 监测装载的项目是否被修改，在关闭tree，新建项目，关闭整个窗口，监测是否变化，弹窗是否保存
    def monitorLoadProject(self) -> ProjectInfo:
        info = self.treeWidget.getTreeInfo()
        if info.projectName != self.info.projectName:
            self.state = True
        elif info.projectDesp != self.info.projectDesp:
            self.state = True
        elif info.partName != self.info.partName:
            self.state = True
        elif info.codeFile != self.info.codeFile:
            self.state = True
        elif info.data0 != self.info.data0:
            self.state = True
        elif info.data1 != self.info.data1:
            self.state = True
        elif info.watchDog != self.info.watchDog:
            self.state = True
        elif info.standbyMode != self.info.standbyMode:
            self.state = True
        elif info.stopMode != self.info.stopMode:
            self.state = True
        elif info.erase != self.info.erase:
            self.state = True
        elif info.program != self.info.program:
            self.state = True
        elif info.verify != self.info.verify:
            self.state = True
        elif info.security != self.info.security:
            self.state = True
        elif info.sectors != self.info.sectors:
            self.state = True
        else:
            self.state = False
        
        return info

    # 动作使能
    def enableAction(self, state: bool):
        self.loadProgrammingFile.setEnabled(state)
        self.saveProgrammingFile.setEnabled(state)
        self.flash.enableMenu(state)
        self.saveProject.setEnabled(state)
        self.saveProjectAs.setEnabled(state)
        self.closeProject.setEnabled(state)
        self.modifyProject.setEnabled(state)
        self.reloadFile.setEnabled(state)
        self.enableChip(state)
        self.treeWidget.enableMenu(state)
    
    # 当点击新建项目、装载项目时，判断当前项目是否需要保存；参数func为函数(无参数)Callable[[arg, ...], result]
    def judgeToSave(self, func: typing.Callable[[], None]):
        if self.ini != "": # 当装载项目
            moInfo = self.monitorLoadProject()
            if self.state: # 装载项目被修改
                reply = QMessageBox.question(self, 'Hint', 'Whether to save the current loading project?', QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes: # 保存修改的项目
                    self.saveConfigInfo(self.ini, moInfo)
                    self.info = moInfo
                    self.successOutput(f"Save Modified Project ---> {moInfo.projectName}@{self.ini} Success")
                else: # 不保存，继续其他操作
                    func()
            else: # 没有被修改，继续其他操作
                func()
        elif self.ini == "" and self.treeWidget.projectName.text(1) != "": # 有新建项目时
            reply = QMessageBox.question(self, 'Hint', 'Whether to save the current new project?', QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes: # 保存新建项目
                self.on_saveProject_triggered()
            else: # 不保存，继续其他操作
                func()
        else: # 当前没有装载项目也没有新建项目，继续其他操作
            func()

    # 关闭tabWidget页的槽函数
    def tabClose(self, index):
        self.tabWidget.removeTab(index)

    # 芯片的操作使能
    def enableChip(self, state: bool):
        self.readChip.setEnabled(state)
        self.flash.readFlash.setEnabled(state)
        self.writeChip.setEnabled(state)
        self.flash.writeFlash.setEnabled(state)
        self.eraseChip.setEnabled(state)
        self.eraseSector.setEnabled(state)
        self.programmeChip.setEnabled(state)
        self.mergeFile.setEnabled(state)
        self.chipBlank.setEnabled(state)
        self.verifyChip.setEnabled(state)
        self.programmeChip.setEnabled(state)
        index = self.tabWidget.currentIndex()
        if index == 0:
            self.reloadFile.setEnabled(False)
        else:
            self.reloadFile.setEnabled(state)
        if not state:
            self.chipLink.setIcon(QIcon(":/icon/icon/chipNotMatch.png"))

    # 查找tabwidget的children
    def getTabWidgetChildren(self) -> dict[str, int]:
        tableDict = {}
        tablesList = self.tabWidget.findChildren(NewTable)
        length = len(tablesList)
        for i in range(length):
            index = self.tabWidget.indexOf(tablesList[i])
            if index < 0:
                self.tabWidget.removeTab(index)
            else:
                tableDict[tablesList[i].fpath] = self.tabWidget.indexOf(tablesList[i])
        
        return tableDict

    # 检查连接情况和扇区选择
    def checkPrecedentConnect(self, output: str):
        series = self.chipLinkSolt() # 检查芯片是否连接
        if series is None:
            self.enableChip(False)
            self.failureOutput(output)
        else:
            sectors = self.treeWidget.getSectorsChoice(self.treeWidget.sectors)
            if "1" in sectors: 
                sectorsDict = {} # 筛选连续存储的扇区
                sectorList = re.split("(1+)", sectors)
                key = 0
                stepLength = 0
                for i in range(len(sectorList)):
                    if sectorList[i] == "":
                        pass
                    else:
                        length = len(sectorList[i])
                        if "1" in sectorList[i]:
                            sectorsDict[key] = length * 4096
                            stepLength += length * 4096
                        else:
                            pass
                        key += length * 4096

                return series, sectorsDict, stepLength
            else: # 没有扇区被勾选
                QMessageBox.warning(self, "warning", "Please select at least one sector!")

    # 清空页
    def clearTab(self):
        # self.tabWidget.setCurrentIndex(0)
        # cnt = self.tabWidget.count()
        # for i in range(1, cnt): # 有的index不是正数，很奇怪，修改当前页面还是有负数索引号的页
        #     self.tabWidget.removeTab(i)
        tablesList = self.tabWidget.findChildren(NewTable)
        length = len(tablesList)
        for i in range(length):
            index = self.tabWidget.indexOf(tablesList[i])
            if index != 0:
                self.tabWidget.removeTab(index)

    # 将flash页设为指定size的初始状态
    def clearFlash(self, fsize: int):
        self.flash.flashSize = fsize
        self.flash.flashData = [0xff for i in range(fsize * 1024)]
        fDict = self.flash.parseFlash(self.flash.flashData, size = fsize)
        self.flash.insertTable(self.flash.table, fDict)

    # 正确输出
    def successOutput(self, outPut: str):
        self.textBrowser.append(outPut)
    
    # 失败输出
    def failureOutput(self, outPut: str):
        self.textBrowser.append("<font color='red'>" + outPut)
    


