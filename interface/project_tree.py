from PyQt5.QtWidgets import QHeaderView, QTreeWidget, QTreeWidgetItem, QCheckBox, QLineEdit, QComboBox, QAction, QMenu
from PyQt5.QtGui import QFont, QIcon, QCursor, QRegExpValidator
from PyQt5.QtCore import QSettings, Qt, pyqtSignal, QRegExp
from interface.project_base_class import ProjectInfo
import bincopy, os
from intelhex import IntelHex

# 自定义控件，并提升为主界面的treewidget，相当于直接替换，也不需要布局引用等
class ProjectTree(QTreeWidget):

    sigNewProject = pyqtSignal()
    sigOpenProject = pyqtSignal()
    sigSaveProject = pyqtSignal()
    sigSaveProjectAs = pyqtSignal()
    sigCloseAll = pyqtSignal()
    sigTableIndex = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # 设置表头信息
        self.header().setVisible(False)
        self.setColumnCount(2)
        self.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.setMinimumWidth(200)
        self.setMaximumWidth(400)

        font1 = QFont()
        font1.setBold(True)

        # 创建节点
        projectInfo = QTreeWidgetItem()
        projectInfo.setIcon(0, QIcon(":/icon/icon/project.png"))
        projectInfo.setText(0, "Project Info")
        projectInfo.setFont(0, font1)

        baseInfo = QTreeWidgetItem()
        baseInfo.setIcon(0, QIcon(":/icon/icon/chip.png"))
        baseInfo.setText(0, "Base")
        baseInfo.setFont(0, font1)

        option = QTreeWidgetItem()
        option.setIcon(0, QIcon(":/icon/icon/option.png"))
        option.setText(0, "Option Byte")
        option.setFont(0, font1)

        self.sectors = QTreeWidgetItem()
        self.sectors.setIcon(0, QIcon(":/icon/icon/sector.png"))
        self.sectors.setText(0, "Operate")
        self.sectors.setFont(0, font1)

        self.lock = QTreeWidgetItem()
        self.lock.setIcon(0, QIcon(":/icon/icon/lock.png"))
        self.lock.setText(0, "Lock")
        self.lock.setFont(0, font1)

        sequence = QTreeWidgetItem()
        sequence.setIcon(0, QIcon(":/icon/icon/sequence.png"))
        sequence.setText(0, "Sequence")
        sequence.setFont(0, font1)

        self.addTopLevelItems([projectInfo, baseInfo, option, self.sectors, self.lock, sequence])

        self.projectName = QTreeWidgetItem(projectInfo)
        self.projectName.setText(0,"Name")
        self.projectDesp = QTreeWidgetItem(projectInfo)
        self.projectDesp.setText(0,"Descript")
        self.chipCore = QTreeWidgetItem(baseInfo)
        self.chipCore.setText(0, "Core")
        self.chipName = QTreeWidgetItem(baseInfo)
        self.chipName.setText(0, "Part No.")
        self.flashSize = QTreeWidgetItem(baseInfo)
        self.flashSize.setText(0, "Flash Size")
        self.codeFile = QTreeWidgetItem(baseInfo)
        self.codeFile.setText(0, "Data File")

        self.dataCK = QTreeWidgetItem(self.codeFile)
        self.dataCK.setText(0, "Data checksum")
        self.fileCRC = QTreeWidgetItem(self.codeFile)
        self.fileCRC.setText(0, "File CRC")
        self.dataCRC = QTreeWidgetItem(self.codeFile)
        self.dataCRC.setText(0, "Data CRC")
        data0 = QTreeWidgetItem(option)
        data0.setText(0, "Data0")
        data1 = QTreeWidgetItem(option)
        data1.setText(0, "Data1")
        watchDog = QTreeWidgetItem(option)
        watchDog.setText(0, "Watch Dog")
        self.nboot1 = QTreeWidgetItem(option)
        self.nboot1.setText(0, "nBoot1 Enable")
        self.pa10Rest = QTreeWidgetItem(option)
        self.pa10Rest.setText(0, "PA10 is used as rest pin")

        self.data0Text = QLineEdit()
        self.data0Text.setMaxLength(2)
        self.data0Text.setStyleSheet("border: 1px solid #A0A0A0;")
        self.setItemWidget(data0, 1, self.data0Text)
        self.data1Text = QLineEdit()
        self.data1Text.setStyleSheet("border: 1px solid #A0A0A0;")
        self.setItemWidget(data1, 1, self.data1Text)
        reHex2 = QRegExp("[A-Fa-f0-9]{2}")
        optionValid = QRegExpValidator(reHex2)
        self.data0Text.setValidator(optionValid)
        self.data1Text.setValidator(optionValid)

        self.watchDogCB = QComboBox()
        self.watchDogCB.addItems(["Hardware watchdog", "Software watchdog"])
        self.watchDogCB.setCurrentIndex(-1)
        self.setItemWidget(watchDog, 1, self.watchDogCB)
        nbootCk = QCheckBox()
        self.setItemWidget(self.nboot1, 1, nbootCk)
        pa10Ck = QCheckBox()
        self.setItemWidget(self.pa10Rest, 1, pa10Ck)

        optionRest = QTreeWidgetItem(option)
        optionRest.setText(0, "Generate reset event")
        enterStandby = QTreeWidgetItem(optionRest)
        enterStandby.setText(0, "Enter standby")
        enterStop = QTreeWidgetItem(optionRest)
        enterStop.setText(0, "Enter stop")
        self.enterShutDown = QTreeWidgetItem(optionRest)
        self.enterShutDown.setText(0, "Enter shutdown")
        self.enterShutDown.setHidden(False)

        self.stdCk = QCheckBox()
        self.setItemWidget(enterStandby, 1, self.stdCk)
        self.stopCk = QCheckBox()
        self.setItemWidget(enterStop, 1, self.stopCk)
        shutCk = QCheckBox()
        self.setItemWidget(self.enterShutDown, 1, shutCk)

        eraseChoic = QTreeWidgetItem(sequence)
        eraseChoic.setText(0, "Erase")
        programmeChoic = QTreeWidgetItem(sequence)
        programmeChoic.setText(0, "Write Data")
        verifyChoic = QTreeWidgetItem(sequence)
        verifyChoic.setText(0, "Verify")
        securityChoic = QTreeWidgetItem(sequence)
        securityChoic.setText(0, "Enable Readout Protection ")

        self.eraseCK = QCheckBox()
        self.setItemWidget(eraseChoic, 1, self.eraseCK)
        self.programmeCK = QCheckBox()
        self.setItemWidget(programmeChoic, 1, self.programmeCK)
        self.verifyCK = QCheckBox()
        self.setItemWidget(verifyChoic, 1, self.verifyCK)
        self.securityCK = QCheckBox()
        self.setItemWidget(securityChoic, 1, self.securityCK)

        # 初始隐藏部分节点
        self.nboot1.setHidden(True)
        self.pa10Rest.setHidden(True)
        self.enterShutDown.setHidden(True)

        # 节点展开
        self.setRootIsDecorated(False)
        self.setItemsExpandable(False)
        self.expandAll()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.slotShowMenu)
        self.addAction()
    
    # 添加动作
    def addAction(self):
        self.new_pro = QAction("New Project")
        self.new_pro.setIcon(QIcon(":/icon/icon/1.png"))
        self.open_pro = QAction("Open Project")
        self.open_pro.setIcon(QIcon(":/icon/icon/2.png"))
        self.act_save = QAction("Save")
        self.act_save.setIcon(QIcon(":/icon/icon/3.png"))
        self.act_saveas = QAction("Save Project As")
        self.act_saveas.setIcon(QIcon(":/icon/icon/4.png"))
        self.act_select_all = QAction("Select All Page")
        self.act_unselect_all = QAction("Unselcet All Page")
        self.act_invert_all = QAction("Invert All Page")
        self.act_close = QAction("Close")

    #右击菜单栏
    def slotShowMenu(self):
        self.new_pro.triggered.connect(self.actNewProject)
        self.open_pro.triggered.connect(self.actOpenProject)
        self.act_save.triggered.connect(self.actSave)
        self.act_saveas.triggered.connect(self.actSaveAs)
        self.act_select_all.triggered.connect(self.selectAll)
        self.act_unselect_all.triggered.connect(self.unselctAll)
        self.act_invert_all.triggered.connect(self.invertAll)
        self.act_close.triggered.connect(self.closeAll)

        menu = QMenu()
        menu.addAction(self.new_pro)
        menu.addAction(self.open_pro)
        menu.addSeparator()
        menu.addAction(self.act_save)
        menu.addAction(self.act_saveas)
        menu.addSeparator()
        menu.addAction(self.act_select_all)
        menu.addAction(self.act_unselect_all)
        menu.addAction(self.act_invert_all)
        menu.addSeparator()
        menu.addAction(self.act_close)

        menu.exec_(QCursor.pos())
    
    def enableMenu(self, state: bool):
        self.act_save.setEnabled(state)
        self.act_saveas.setEnabled(state)
        self.act_close.setEnabled(state)
        self.act_select_all.setEnabled(state)
        self.act_invert_all.setEnabled(state)
        self.act_unselect_all.setEnabled(state)
    
    def actNewProject(self):
        self.sigNewProject.emit()
        self.new_pro.triggered.disconnect()
    
    def actOpenProject(self):
        self.sigOpenProject.emit()
        self.open_pro.triggered.disconnect()

    def actSave(self):
        self.sigSaveProject.emit()
        self.act_save.triggered.disconnect()

    def actSaveAs(self):
        self.sigSaveProjectAs.emit()
        self.act_saveas.triggered.disconnect()

    def selectAll(self):
        self.setSectorCheckBox(0)
        self.act_select_all.triggered.disconnect()

    def unselctAll(self):
        self.setSectorCheckBox(1)
        self.act_unselect_all.triggered.disconnect()

    def invertAll(self):
        self.setSectorCheckBox(2)
        self.act_invert_all.triggered.disconnect()

    def setSectorCheckBox(self, state: int):
        cnt = self.sectors.childCount()
        for i in range(cnt):
            ck = self.itemWidget(self.sectors.child(i), 1)
            if state == 0:
                ck.setChecked(True)
            elif state == 1:
                ck.setChecked(False)
            else:
                ck.setChecked(False if ck.isChecked() else True)

    def closeAll(self): # 清空tree
        self.sigCloseAll.emit() # 清空flash存储信息

    #返回当前tree中显示的信息
    def getTreeInfo(self) -> ProjectInfo:
        info = ProjectInfo()
        info.projectName = self.projectName.text(1)
        info.projectDesp = self.projectDesp.text(1)
        info.core = self.chipCore.text(1)
        info.partName = self.chipName.text(1)
        info.flashSize = self.flashSize.text(1)[:-5]
        info.codeFile = self.codeFile.text(1)
        info.data0 = self.data0Text.text()
        info.data1 = self.data1Text.text()
        info.watchDog = self.watchDogCB.currentText()
        info.standbyMode = self.stdCk.isChecked()
        info.stopMode = self.stopCk.isChecked()
        info.erase = self.eraseCK.isChecked()
        info.program = self.programmeCK.isChecked()
        info.verify = self.verifyCK.isChecked()
        info.security = self.securityCK.isChecked()
        info.sectors = self.getSectorsChoice(self.sectors)
        info.lock = self.getSectorsChoice(self.lock)

        info.nboot = 0 if self.nboot1.isHidden() else 2 if self.itemWidget(self.nboot1, 1).isChecked() else 1
        info.pa10 = 0 if self.pa10Rest.isHidden() else 2 if self.itemWidget(self.pa10Rest, 1).isChecked() else 1
        info.shutMode = 0 if self.enterShutDown.isHidden() else 2 if self.itemWidget(self.enterShutDown, 1).isChecked() else 1
        return info

    # 在tree显示信息或清空tree， state表示是否删除原扇区，默认删除（False）
    def showConfiguration(self, info: ProjectInfo, state = False):
        self.projectName.setText(1, info.projectName)
        self.projectDesp.setText(1, info.projectDesp)
        self.chipName.setText(1, info.partName)
        self.flashSize.setText(1, info.flashSize + "KByte")
        self.codeFile.setText(1, info.codeFile)
        self.chipCore.setText(1, info.core)

        if os.path.exists(info.codeFile):
            self.dataCK.setText(1, self.dataCheck(info.codeFile))
            self.fileCRC.setText(1, self.fileCalCRC(info.codeFile))
            self.dataCRC.setText(1, self.dataCheck(info.codeFile, False))
        else:
            self.dataCK.setText(1, "")
            self.fileCRC.setText(1, "")
            self.dataCRC.setText(1, "")

        self.data0Text.setText(info.data0)
        self.data1Text.setText(info.data1)
        self.stdCk.setChecked(info.standbyMode)
        self.stopCk.setChecked(info.stopMode)
        self.setUseByte(info.nboot, self.nboot1)
        self.setUseByte(info.pa10, self.pa10Rest)
        self.setUseByte(info.shutMode, self.enterShutDown)

        self.eraseCK.setChecked(info.erase)
        self.programmeCK.setChecked(info.program)
        self.verifyCK.setChecked(info.verify)
        self.securityCK.setChecked(info.security)

        # 可悬浮显示内容
        self.chipName.setToolTip(1, info.partName)
        self.codeFile.setToolTip(1, info.codeFile)
        
        if info.hWatchDog:
            self.watchDogCB.setCurrentIndex(0)
        elif info.sWatchDog:
            self.watchDogCB.setCurrentIndex(1)
        else:
            self.watchDogCB.setCurrentIndex(-1)

        if state:
            pass
        else:
            # 清空sector内容
            self.clearSector(self.sectors)
            self.clearSector(self.lock)
            self.itemClicked.connect(self.clickAndJump)

            if info.flashSize == "": # 关闭项目时，清空内容
                self.flashSize.setText(1, "")
            else:
                if info.sectors != "":
                    self.setSectorsChoice(self.sectors, int(info.flashSize), info.sectors)
                else:
                    self.setSectorsChoice(self.sectors, int(info.flashSize))
                if info.lock != "":
                    self.setSectorsChoice(self.lock, int(info.flashSize), info.lock)
                else:
                    self.setSectorsChoice(self.lock, int(info.flashSize), sectors="False")
    
    # 设置是否影藏选项
    def setUseByte(self, state: int, item: QTreeWidgetItem):
        if state == 0:
            item.setHidden(True)
        else:
            item.setHidden(False)
            ck = self.itemWidget(item, 1)
            ck.setChecked(True if state == 2 else False)

    # 读取ini的信息，并展示到treewidget
    def openProject(self, filePath: str) -> ProjectInfo:
        info = ProjectInfo()
        # self.closeAll() # 装载项目前清空tree，或提示是否需要保存内容
        settings = QSettings(filePath, QSettings.IniFormat)
        info.projectName = settings.value("Base/projectName")
        info.projectDesp = settings.value("Base/descript")
        info.partName = settings.value("Base/partName")
        info.core = settings.value("Base/core")
        info.flashSize = settings.value("Base/flashSize")
        info.codeFile = settings.value("Base/filePath")

        info.data0 = settings.value("Option/data0")
        info.data1 = settings.value("Option/data1")
        info.watchDog = settings.value("Option/watchDog")
        info.hWatchDog = True if info.watchDog == "Hardware watchdog" else False
        info.sWatchDog = True if info.watchDog == "Software watchdog" else False
        info.standbyMode = True if str(settings.value("Option/standByReset")).lower() == "true" else False
        info.stopMode = True if str(settings.value("Option/stopReset")).lower() == "true" else False

        info.nboot = int(settings.value("Option/nBoot1")) if settings.value("Option/nBoot1") else 0
        info.pa10 = int(settings.value("Option/PA10Rest")) if settings.value("Option/PA10Rest") else 0
        info.shutMode = int(settings.value("Option/shutdownByRest")) if settings.value("Option/shutdownByRest") else 0

        info.erase = True if str(settings.value("Sequence/erase")).lower() == "true" else False
        info.program = True if str(settings.value("Sequence/programme")).lower() == "true" else False
        info.verify = True if str(settings.value("Sequence/verify")).lower() == "true" else False
        info.security = True if str(settings.value("Sequence/security")).lower() == "true" else False

        info.sectors = settings.value("Sectors/Sector")
        info.lock = settings.value("Lock/Sector") if settings.value("Lock/Sector") else ""

        self.showConfiguration(info)

        return info
    
    # 获取sequence的勾选状态
    def getSequenceState(self) -> list:
        state = []
        eraseState = self.eraseCK.isChecked()
        state.append(eraseState)
        writeState = self.programmeCK.isChecked()
        state.append(writeState)
        verifyState = self.verifyCK.isChecked()
        state.append(verifyState)
        securityState = self.securityCK.isChecked()
        state.append(securityState)

        return state

    # 获取当前option byte的信息，并转为相应的数据，硬件高位自动取反，不需要手动；特殊的userbyte可以判断是否存在节点，且是否勾选
    def getOptionByteData(self) -> list:
        data = []
        rdp = self.securityCK.isChecked()
        if rdp: # security勾选)
            rdpData = 0xDE21 # 设置读保护，只能全片擦除才能解除读保护
        else:
            rdpData = 0x5AA5 # 不设置读保护，默认解除0x5AA5
        data.append(rdpData) # add rdp

        wdogIndex = self.watchDogCB.currentIndex()
        if wdogIndex == 0: # 硬件
            wdog = 0xFE
        elif wdogIndex == 1: # 软件
            wdog = 0xFF
        stdby = 0xFB if self.stdCk.isChecked() else 0xFF # 勾选则写0
        stop = 0xFD if self.stopCk.isChecked() else 0xFF
        shut = 0xFF if self.enterShutDown.isHidden() else 0xF7 if self.itemWidget(self.enterShutDown, 1).isChecked() else 0xFF
        nboot1 = 0xFF if self.nboot1.isHidden() else 0xEF if self.itemWidget(self.nboot1, 1).isChecked() else 0xFF
        PA10Rest = 0xFF if self.pa10Rest.isHidden() else 0xDF if self.itemWidget(self.pa10Rest, 1).isChecked() else 0xFF

        userByte = 0xFF & stdby & stop & wdog & shut & nboot1 & PA10Rest
        data.append(userByte) # add user

        data0 = int(self.data0Text.text(), 16)
        data.append(data0) # add data0

        data1 = int(self.data1Text.text(), 16)
        data.append(data1) # add data1

        # 写保护，将写保护勾选的扇区转为实际写入的值，勾选为0
        lockSectors = self.getSectorsChoice(self.lock)
        if "1" in lockSectors:
            for i in range(0, len(lockSectors), 8):
                tmp8bit = lockSectors[i: i + 8]
                tmpRever = []
                for ck in list(tmp8bit):
                    rever = "0" if ck == "1" else "1"
                    tmpRever.insert(0, rever)
                data.append(int("".join(tmpRever), 2))
        else:
            pass

        print(data)
        return data
    
    # 获取tree的扇区勾选情况，state为真表示选择扇区则为1，反之为零
    def getSectorsChoice(self, item: QTreeWidgetItem):
        cnt = item.childCount()
        sectors = ""
        for i in range(cnt):
            ck = self.itemWidget(item.child(i), 1)
            sectors += "1" if ck.isChecked() else "0"
        return sectors
    
    # 清空节点
    def clearSector(self, item: QTreeWidgetItem):
        for _ in range(item.childCount()):
            childItem = item.child(0)
            item.removeChild(childItem)
    
    # 向tree写入扇区的勾选情况
    def setSectorsChoice(self, item: QTreeWidgetItem, size: int, sectors = ""):
        cnt = 0
        for i in range(134217728, 134217728 + size * 1024, 4096):
            start = "0x{:08X}".format(i)
            end = "0x{:08X}".format(i + 4095)
            sector = QTreeWidgetItem(item)
            sector.setText(0, start + " - " + end + "  ")
            ck = QCheckBox()
            if sectors == "":
                ck.setChecked(True)
            elif sector == "False":
                ck.setChecked(False)
            else:
                if cnt < len(sectors):
                    ck.setChecked(True if sectors[cnt] == "1" else False)
                else:
                    ck.setChecked(False)
            self.setItemWidget(sector, 1, ck)
            cnt += 1

    # 确定点击的是哪个扇区
    def clickAndJump(self, item: QTreeWidgetItem, column: int):
        if item.parent() and (item.parent().text(0) == "Operate" or item.parent().text(0) == "Lock"):
            sector = item.text(0)[:10]
            self.sigTableIndex.emit(int(sector, 16) - 0x08000000)
        else:
            pass
    
    # code file data checksum or data crc
    def dataCheck(self, filePath: str, state = True) -> str:
        if filePath == "":
            return ""
        result = 0
        suffix = os.path.splitext(filePath)[-1][1:]
        if suffix == "bin" or suffix == "hex":
            ih = IntelHex()
            ih.loadfile(filePath, suffix)
            minaddr = ih.minaddr()
            maxaddr = ih.maxaddr()
            if state: # 计算checksum
                for i in range(minaddr, maxaddr + 1, 1):
                    result += ih[i]
            else: # 计算data crc
                for i in range(minaddr, maxaddr + 1, 1):
                    result ^= ih[i]
                    for j in range(8):
                        if (result & 1):
                            result = (result >> 1) ^ 0xEDB88320
                        else:
                            result >>= 1
        elif suffix == "s19":
            bc = bincopy.BinFile(filePath)
            minaddr = bc.minimum_address
            maxaddr = bc.maximum_address # bincopy的maxAddr实际等于maximum_address - 1
            if state:
                for i in range(minaddr, maxaddr, 1):
                    result += bc[i]
            else: 
                for i in range(minaddr, maxaddr, 1):
                    result ^= bc[i]
                    for j in range(8):
                        if (result & 1):
                            result = (result >> 1) ^ 0xEDB88320
                        else:
                            result >>= 1

        return "0x{:08X}".format(result & 0xFFFFFFFF)

    # code file crc
    def fileCalCRC(self, filePath: str) -> str:
        if filePath == "":
            return ""
        content = bytes('', encoding="UTF-8")
        with open(filePath, "rb") as f:
            content = f.read()

        crc = 0x00000000
        for i in range(len(content)):
            crc ^= content[i]
            for j in range(8):
                if (crc & 1):
                    crc = (crc >> 1) ^ 0xEDB88320
                else:
                    crc >>= 1
        return "0x{:08X}".format(crc & 0xFFFFFFFF)

# 样式设计，tooltip设置