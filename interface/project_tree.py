from PyQt5.QtWidgets import QHeaderView, QTreeWidget, QTreeWidgetItem, QFileDialog, QCheckBox, QLineEdit, QComboBox, QAction, QMenu
from PyQt5.QtGui import QFont, QIcon, QCursor, QRegExpValidator
from PyQt5.QtCore import QSettings, Qt, pyqtSignal, QRegExp
from interface.project_base_class import ProjectInfo
import bincopy, os
from intelhex import IntelHex

# 自定义控件，并提升为主界面的treewidget，相当于直接替换，也不需要布局引用等
class ProjectTree(QTreeWidget):
    sigSaveProject = pyqtSignal()
    sigSaveProjectAs = pyqtSignal()
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

        projectInfo = QTreeWidgetItem()
        projectInfo.setIcon(0, QIcon(":/icon/icon/project.png"))
        projectInfo.setText(0, "Project Info")
        projectInfo.setFont(0, font1)

        programmerInfo = QTreeWidgetItem()
        programmerInfo.setIcon(0, QIcon(":/icon/icon/programmer.png"))
        programmerInfo.setText(0, "Programmer Info")
        programmerInfo.setFont(0, font1)

        baseInfo = QTreeWidgetItem()
        baseInfo.setIcon(0, QIcon(":/icon/icon/chip.png"))
        baseInfo.setText(0, "Base")
        baseInfo.setFont(0, font1)

        option = QTreeWidgetItem()
        option.setIcon(0, QIcon(":/icon/icon/option.png"))
        option.setText(0, "Option")
        option.setFont(0, font1)

        self.sectors = QTreeWidgetItem()
        self.sectors.setIcon(0, QIcon(":/icon/icon/sector.png"))
        self.sectors.setText(0, "Sectors")
        self.sectors.setFont(0, font1)

        self.addTopLevelItems([projectInfo, programmerInfo, baseInfo, option, self.sectors])

        self.projectName = QTreeWidgetItem(projectInfo)
        self.projectName.setText(0,"Name")
        self.projectDesp = QTreeWidgetItem(projectInfo)
        self.projectDesp.setText(0,"Descript")
        self.programModel = QTreeWidgetItem(programmerInfo)
        self.programModel.setText(0, "Type")
        self.linkMode = QTreeWidgetItem(programmerInfo)
        self.linkMode.setText(0, "Link Mode")
        self.resetType = QTreeWidgetItem(programmerInfo)
        self.resetType.setText(0, "Reset Type")
        self.clockFrequcy = QTreeWidgetItem(programmerInfo)
        self.clockFrequcy.setText(0, "Frequence")
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
        data0 = QTreeWidgetItem(option)
        data0.setText(0, "Data0")
        data1 = QTreeWidgetItem(option)
        data1.setText(0, "Data1")
        watchDog = QTreeWidgetItem(option)
        watchDog.setText(0, "Watch Dog")

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

        self.optionRest = QTreeWidgetItem(option)
        self.optionRest.setText(0, "Reset")
        self.enterStandby = QTreeWidgetItem(self.optionRest)
        self.enterStandby.setText(0, "Enter standby")
        self.enterStop = QTreeWidgetItem(self.optionRest)
        self.enterStop.setText(0, "Enter stop")

        self.ck1 = QCheckBox()
        self.setItemWidget(self.enterStandby, 1, self.ck1)
        self.ck2 = QCheckBox()
        self.setItemWidget(self.enterStop, 1, self.ck2)

        self.setRootIsDecorated(False)
        # self.setItemsExpandable(False)
        self.expandAll()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.slotShowMenu)

    #右击菜单栏
    def slotShowMenu(self):
        act_save = QAction("Save")
        act_save.setIcon(QIcon(":/icon/icon/3.png"))
        act_saveas = QAction("Save Project As")
        act_saveas.setIcon(QIcon(":/icon/icon/4.png"))
        act_select_all = QAction("Select All Page")
        act_unselect_all = QAction("Unselcet All Page")
        act_invert_all = QAction("Invert All Page")
        act_close = QAction("Close")

        act_save.triggered.connect(self.actSave)
        act_saveas.triggered.connect(self.actSaveAs)
        act_select_all.triggered.connect(self.selectAll)
        act_unselect_all.triggered.connect(self.unselctAll)
        act_invert_all.triggered.connect(self.invertAll)
        act_close.triggered.connect(self.closeAll)

        menu = QMenu()
        menu.addAction(act_save)
        menu.addAction(act_saveas)
        menu.addSeparator()
        menu.addAction(act_select_all)
        menu.addAction(act_unselect_all)
        menu.addAction(act_invert_all)
        menu.addSeparator()
        menu.addAction(act_close)

        menu.exec_(QCursor.pos())

    def actSave(self):
        self.sigSaveProject.emit()

    def actSaveAs(self):
        self.sigSaveProjectAs.emit()

    def selectAll(self):
        # flashSize = self.flashSize.text(1)[:len(self.flashSize.text(1)) - 5]
        cnt = self.sectors.childCount()
        for i in range(cnt):
            ck = self.itemWidget(self.sectors.child(i), 1)
            ck.setChecked(True)

    def unselctAll(self):
        cnt = self.sectors.childCount()
        for i in range(cnt):
            ck = self.itemWidget(self.sectors.child(i), 1)
            ck.setChecked(False)

    def invertAll(self):
        cnt = self.sectors.childCount()
        for i in range(cnt):
            ck = self.itemWidget(self.sectors.child(i), 1)
            ck.setChecked(False if ck.isChecked() else True)

    def closeAll(self): # 清空tree
        info = ProjectInfo()
        self.showConfiguration(info)
        cnt = self.sectors.childCount()
        for i in range(cnt):
            item = self.sectors.child(0)
            self.sectors.removeChild(item)

    #返回option和sector部分的内容，该部分在tree可修改
    def getTreeInfo(self) -> ProjectInfo:
        info = ProjectInfo()
        info.data0 = self.data0Text.text()
        info.data1 = self.data1Text.text()
        info.watchDog = self.watchDogCB.currentText()
        info.standbyMode = self.ck1.isChecked()
        info.stopMode = self.ck2.isCheckable()
        info.sectors = self.getSectorsChoice()
        return info

    #新建项目在tree显示信息
    def showConfiguration(self, info: ProjectInfo):
        self.projectName.setText(1, info.projectName)
        self.projectDesp.setText(1, info.projectDesp)
        self.chipName.setText(1, info.partName)
        self.flashSize.setText(1, info.flashSize + "KByte")
        self.codeFile.setText(1, info.codeFile)
        self.programModel.setText(1, info.programmer)
        self.linkMode.setText(1, info.linkMode)
        self.resetType.setText(1, info.resetType)
        self.clockFrequcy.setText(1, info.frequence)
        self.chipCore.setText(1, info.core)

        # self.codeFile.setToolTip(1, info.codeFile)

        self.dataCK.setText(1, self.dataCheckSum(info.codeFile))
        self.fileCRC.setText(1, self.fileCalCRC(info.codeFile))

        self.data0Text.setText(info.data0)
        self.data1Text.setText(info.data1)
        self.ck1.setChecked(info.standbyMode)
        self.ck2.setChecked(info.stopMode)
        
        if info.hWatchDog:
            self.watchDogCB.setCurrentIndex(0)
        elif info.sWatchDog:
            self.watchDogCB.setCurrentIndex(1)
        else:
            self.watchDogCB.setCurrentIndex(-1)

        font = QFont()
        font.setPointSize(7)
        if info.flashSize == "":
            self.flashSize.setText(1, "")
        else:
            self.setSectorsChoice("", int(info.flashSize))

    #展示项目信息
    def openProject(self):
        filePath, _ = QFileDialog.getOpenFileName(None, "open project", "C:\\", 'MM Programmer Config File(*.ini)')
        if os.path.exists(filePath):
            settings = QSettings(filePath, QSettings.IniFormat)
            size = int(settings.value("Base/flashSize"))
            codeFile = str(settings.value("Base/filePath"))

            self.projectName.setText(1, settings.value("Base/projectName"))
            self.projectDesp.setText(1, settings.value("Base/descript"))
            self.chipCore.setText(1, settings.value("Base/core"))
            self.chipName.setText(1, settings.value("Base/partName"))
            self.flashSize.setText(1, str(settings.value("Base/flashSize")) + "KByte")
            self.codeFile.setText(1, codeFile)
            self.dataCK.setText(1, self.dataCheckSum(codeFile))
            self.fileCRC.setText(1, self.fileCalCRC(codeFile))

            self.programModel.setText(1, settings.value("Programmer/programmer"))
            self.linkMode.setText(1, settings.value("Programmer/connectType"))
            self.resetType.setText(1, settings.value("Programmer/resetType"))
            self.clockFrequcy.setText(1, settings.value("Programmer/frequence"))

            self.data0Text.setText(settings.value("Option/data0"))
            self.data1Text.setText(settings.value("Option/data1"))
            self.watchDogCB.setCurrentText(settings.value("Option/watchDog"))
            ck1 = settings.value("Option/standByReset")
            ck2 = settings.value("Option/stopReset")
            if ck1 == "true":
                self.ck1.setChecked(True)
            else:
                self.ck1.setChecked(False)
            if ck2 == "true":
                self.ck2.setChecked(True)
            else:
                self.ck2.setChecked(False)

            self.setSectorsChoice(settings.value("Sectors/Sector"), size)

            return filePath, codeFile, size
        else:
            return "", "", 0
    
    def getSectorsChoice(self):
        cnt = self.sectors.childCount()
        sectors = ""
        for i in range(cnt):
            ck = self.itemWidget(self.sectors.child(i), 1)
            sectors += "1" if ck.isChecked() else "0"
        return sectors
    
    def setSectorsChoice(self, sectors, size):
        font = QFont()
        font.setPointSize(8)
        cnt = 0
        for i in range(134217728, 134217728 + size * 1024, 4096):
            start = "0x{:08X}".format(i)
            end = "0x{:08X}".format(i + 4095)
            sector = QTreeWidgetItem(self.sectors)
            sector.setText(0, start + " - " + end)
            sector.setFont(0, font)
            ck = QCheckBox()
            if sectors == "":
                ck.setChecked(True)
            else:
                if cnt < len(sectors):
                    ck.setChecked(True if sectors[cnt] == "1" else False)
                else:
                    ck.setChecked(False)
            self.setItemWidget(sector, 1, ck)
            cnt += 1
    
    def dataCheckSum(self, filePath: str) -> str:
        if filePath == "":
            return ""
        checksum = 0
        suffix = os.path.splitext(filePath)[-1][1:]
        if suffix == "bin" or suffix == "hex":
            ih = IntelHex()
            ih.loadfile(filePath, suffix)
            minaddr = ih.minaddr()
            maxaddr = ih.maxaddr()
            for i in range(minaddr, maxaddr + 1, 1):
                checksum += ih[i]
        elif suffix == "s19":
            bc = bincopy.BinFile(filePath)
            minaddr = bc.minimum_address
            maxaddr = bc.maximum_address # bincopy的maxAddr实际等于maximum_address - 1
            for i in range(minaddr, maxaddr, 1):
                checksum += bc[i]

        return "0x{:08X}".format(checksum & 0xFFFFFFFF)

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