from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QAbstractItemView, QGridLayout, QAction, QMenu, QHeaderView
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QIcon, QBrush, QColor, QFont
from intelhex import IntelHex
import os
import string
import typing
import bincopy
from io import StringIO


ROW_HEIGHT = 15

class BaseTable():


    def __init__(self):
        pass

    def styleTable(self, table: QTableWidget):
        table.verticalHeader().setVisible(False) #隐藏列表头
        table.horizontalHeader().setVisible(False) #隐藏行表头
        table.setShowGrid(False) #隐藏表格线
        table.setEditTriggers(QAbstractItemView.NoEditTriggers) #只读不可修改
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus) #选中表格数据不着重显示

        table.setColumnCount(33)
        table.verticalHeader().setMinimumSectionSize(ROW_HEIGHT)

    # 添加动作
    def actAction(self):
        self.act_load_file = QAction("Load Data File")
        self.act_load_file.setIcon(QIcon(":/icon/icon/6.png"))
        self.act_saveas_file = QAction("Save Data File")
        self.act_saveas_file.setIcon(QIcon(":/icon/icon/5.png"))
        self.act_bit8 = QAction("Byte")
        self.act_bit8.setCheckable(True) #设置actoion可选中
        self.act_bit8.setChecked(True) #设置为当前选中状态
        self.act_bit16 = QAction("Word")
        self.act_bit16.setCheckable(True)
        self.act_bit32 = QAction("DWord")
        self.act_bit32.setCheckable(True)

    # 获取当前为几字节显示
    def getCurrentState(self) -> int:
        state = 1
        bit8 = self.act_bit8.isChecked()
        bit16 = self.act_bit16.isChecked()
        bit32 = self.act_bit32.isChecked()
        if bit8:
            state = 1
        elif bit16:
            state = 2
        elif bit32:
            state = 4
        return state

    # 将flash信息插入表格
    def insertTable(self, table: QTableWidget, data: typing.Optional[dict[str, list]] = None, state = 1):
        #清空列表
        table.setRowCount(0)
        table.clearContents()

        if data is None: # 初始界面默认32k，全FF
            flashDict = {}
            for l in range(0, 32768, state * 16):
                flashDict["0x{:08X}".format(0x08000000 + l)] = ["FF" for i in range(16 * state)]
            data = flashDict

        for key, value in data.items():
            row = table.rowCount()
            table.insertRow(row)
            table.setRowHeight(row, ROW_HEIGHT)
            addrItem = QTableWidgetItem(key)
            addrItem.setTextAlignment(Qt.AlignCenter)
            addrItem.setForeground(QBrush(QColor(248,248,255)))
            addrItem.setBackground(QBrush(QColor(128,128,128)))
            addrItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)
            table.setItem(row, 0, addrItem)
            value = self.translateAscii(value)
            for j in range(0, len(value)):
                newItem = QTableWidgetItem(value[j])
                newItem.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, j + 1, newItem)

        self.setCellSize(table, state)

    # 十六进制转ASCII
    def translateAscii(self, hexData: list) -> list:
        asciiData = []
        for i in range(len(hexData)):
            length = len(hexData[i])
            tempStr = ""
            for j in range(0, length, 2):
                temp = chr(int(hexData[i][j : j+2], 16))
                if temp in string.whitespace or temp == "\x00" or temp == "\x08":
                    temp = "."
                tempStr += temp
            asciiData.append(tempStr)
            # asciiData.append((bytearray.fromhex(hexData[i])).decode('utf-8', 'ignore'))
        return hexData + asciiData

    # 保存flash表的数据
    def saveTableDataAsDict(self, table: QTableWidget) -> dict[int, int]:
        flashDict = {}
        row = table.rowCount() # 行，与flashsize有关
        for i in range(row): # 行
            address = int(table.item(i, 0).text(), 16)
            for j in range(1, 17): # 列， 从第一列开始，到后16列
                itemData = table.item(i, j).text()
                length = len(itemData)
                while(length > 0): # ***
                    flashDict[address] = int(itemData[length - 2 : length], 16)
                    length -= 2
                    address += 1
        return flashDict
    
    # 将数据保存为data file，支持bin、hex、s19
    def saveCodeFile(self, file: str, data: dict[int, int]):
        suffix = os.path.splitext(file)[-1][1:]
        ih = IntelHex(data)
        if suffix == "bin":
            ih.tobinfile(file)
        elif suffix == "hex":
            ih.write_hex_file(file)
        elif suffix == "s19":
            ih.write_hex_file(file)
            bc = bincopy.BinFile(file)
            content = bc.as_srec()
            with open(file, "w") as f:
                f.write(content)
    
    # 设置行高列宽
    def setCellSize(self, table: QTableWidget, state: int):
        width = [20, 15]
        if state == 2:
            width = [36, 25]
        elif state == 4:
            width = [63, 35]
        
        for i in range(0, 33):
            if i == 0:
                table.setColumnWidth(i, 81)
            elif i < 17:
                table.setColumnWidth(i, width[0])
            else:
                table.setColumnWidth(i, width[1])
        #table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents) # 动态分配大小会导致页面卡顿

    # 设置右击菜单使能
    def enableMenu(self, state: bool):
        self.act_load_file.setEnabled(state)
        self.act_saveas_file.setEnabled(state)

# 该类用于查看code file
class NewTable(QTableWidget, BaseTable):

    sigTableOpenFileDia = pyqtSignal()
    sigTableSaveFile = pyqtSignal()
    sigReloadDataFile = pyqtSignal()

    def __init__(self, parent: QWidget, filePath: str, flashSize: int):
        super().__init__(parent)
        self.fpath = filePath
        self.fsize = flashSize
        self.fdata = []
        self.initUI()
    
    def initUI(self):
        self.styleTable(self)
        # 右击菜单
        self.actAction()
        self.addTableAction()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.slotShowMenu)

    # 右击菜单栏
    def slotShowMenu(self):
        menuShow = QMenu("Display")
        menuShow.addAction(self.act_bit8)
        menuShow.addAction(self.act_bit16)
        menuShow.addAction(self.act_bit32)
        self.act_bit8.triggered.connect(self.act8BitWidth)
        self.act_bit16.triggered.connect(self.act16BitWidth)
        self.act_bit32.triggered.connect(self.act32BitWidth)

        self.act_load_file.triggered.connect(self.actLoadFile)
        self.act_saveas_file.triggered.connect(self.acSaveAs)
        self.reloadDataFile.triggered.connect(self.reloadDataFileSolt)

        menu = QMenu()
        menu.addAction(self.act_load_file)
        menu.addAction(self.act_saveas_file)
        menu.addSeparator()
        menu.addAction(self.reloadDataFile)
        menu.addSeparator()
        menu.addMenu(menuShow)
        menu.exec_(QCursor.pos())
    
    def addTableAction(self):
        self.reloadDataFile = QAction("Reload Data From File")
        self.reloadDataFile.setIcon(QIcon(":/icon/icon/reload.png"))

    def actLoadFile(self):
        self.sigTableOpenFileDia.emit()
        self.act_load_file.triggered.disconnect()

    def acSaveAs(self):
        self.sigTableSaveFile.emit()
        self.act_saveas_file.triggered.disconnect()
    
    def reloadDataFileSolt(self):
        self.sigReloadDataFile.emit()
        self.reloadDataFile.triggered.disconnect()

    def act8BitWidth(self):
        self.act_bit8.setChecked(True)
        self.act_bit16.setChecked(False)
        self.act_bit32.setChecked(False)
        data = self.processTableData()
        self.insertTable(self, data)
        self.act_bit8.triggered.disconnect()

    def act16BitWidth(self):
        self.act_bit8.setChecked(False)
        self.act_bit16.setChecked(True)
        self.act_bit32.setChecked(False)
        data = self.processTableData(state = 2)
        self.insertTable(self, data, state = 2)
        self.act_bit16.triggered.disconnect()

    def act32BitWidth(self):
        self.act_bit8.setChecked(False)
        self.act_bit16.setChecked(False)
        self.act_bit32.setChecked(True)
        data = self.processTableData(state = 4)
        self.insertTable(self, data, state = 4)
        self.act_bit32.triggered.disconnect()

    # 解析文件信息，保存到构造函数的fdata中
    def parseData(self, binStart = 0x08000000, binEnd = 0x08007FFF, defalut = 0xff):
        file = self.fpath
        size = self.fsize
        flashMaxAddr = 0x08000000 + size * 1024 - 1

        ih = IntelHex()
        if file.endswith(".hex"):
            ih.fromfile(file, "hex") 
        elif file.endswith(".bin"):
            ih.loadbin(file, offset = binStart)
        elif file.endswith(".s19"):
            bc = bincopy.BinFile(file)
            ih.loadhex(StringIO(bc.as_ihex()))

        ih.padding = defalut
        minaddr = ih.minaddr()
        maxaddr = ih.maxaddr()
        difference = maxaddr - minaddr

        if minaddr < 0x08000000: 
            minaddr = 0x08000000
            maxaddr = minaddr + difference
        if maxaddr > flashMaxAddr:
            maxaddr = flashMaxAddr
        if file.endswith(".bin"): 
            maxaddr = binEnd

        flist = [ih[i] for i in range(0x08000000, maxaddr + 1)]
        slist = [defalut for i in range(maxaddr + 1, flashMaxAddr + 1)]

        self.fdata = flist + slist
    
    def processTableData(self, state = 1): 
        size = self.fsize
        data = self.fdata

        flashDict = {}
        for l in range(0, size * 1024, state * 16):
            flashDict["0x{:08X}".format(0x08000000 + l)] = []
        
        hexData = []
        for i in range(0, len(data), state):
            if state == 1:
                hexData.append("{:02X}".format(data[i]))
            elif state == 2:
                hexData.append("{:02X}".format(data[i+1]) + "{:02X}".format(data[i]))
            elif state == 4:
                hexData.append("{:02X}".format(data[i+3]) + "{:02X}".format(data[i+2]) + "{:02X}".format(data[i+1]) + "{:02X}".format(data[i]))
        
        for i in range(0, len(hexData), 16):
            key = "0x{:08X}".format(0x08000000 + i * state)
            flashDict[key] = hexData[i: i + 16]
        
        return flashDict

    # 将table数据转为地址和数据的形式
    def dataToDict(self) -> dict[int, int]:
        fdata = self.fdata

        dataDict = {}
        cnt = 0
        for data in fdata:
            dataDict[0x08000000 + cnt] = data
            cnt += 1
        return dataDict


# 只用于flash
class ReadFlash(QWidget, BaseTable):

    sigOpenFileDia = pyqtSignal()
    sigSaveFile = pyqtSignal()
    sigReadData = pyqtSignal()
    sigWriteData = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        self.table = QTableWidget(self)
        self.optTable = QTableWidget(self)
        layout.addWidget(self.table)
        layout.addWidget(self.optTable)
        layout.setRowStretch(0, 15)
        layout.setRowStretch(1, 1)
        self.setLayout(layout)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(1)
        # self.setMaximumWidth(800) #与tree设置的最大最小太绝对，导致窗口变大变小无法适应

        self.styleTable(self.table)
        self.styleTable(self.optTable)

        # 初始值
        self.flashData = [0xff for _ in range(32768)]
        self.flashSize = 32
        self.optData = ["FF" for _ in range(64)]
        self.insertTable(self.table)
        self.insertOptData()

        # 右击菜单
        self.actAction()
        self.addFlashAction()
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.slotShowMenu)
        
    def addFlashAction(self):
        self.readFlash = QAction("Read Data")
        self.readFlash.setIcon(QIcon(":/icon/icon/read.png"))
        self.writeFlash = QAction("Write Data")
        self.writeFlash.setIcon(QIcon(":/icon/icon/write.png"))

    # 右击菜单栏
    def slotShowMenu(self):
        self.act_fill_FF = QAction("Fill Data->$FF")
        self.act_fill_00 = QAction("Fill Data->$00")
        menuShow = QMenu("Display")

        menuShow.addAction(self.act_bit8)
        menuShow.addAction(self.act_bit16)
        menuShow.addAction(self.act_bit32)
        self.act_bit8.triggered.connect(self.act8BitWidth)
        self.act_bit16.triggered.connect(self.act16BitWidth)
        self.act_bit32.triggered.connect(self.act32BitWidth)

        self.act_load_file.triggered.connect(self.actLoadFile)
        self.act_saveas_file.triggered.connect(self.acSaveAs)
        self.act_fill_FF.triggered.connect(self.fillDataFF)
        self.act_fill_00.triggered.connect(self.fillData00)
        self.readFlash.triggered.connect(self.actReadFlashSolt)
        self.writeFlash.triggered.connect(self.actWriteFlashSolt)

        menu = QMenu()
        menu.addAction(self.act_load_file)
        menu.addAction(self.act_saveas_file)
        menu.addSeparator()
        menu.addAction(self.act_fill_FF)
        menu.addAction(self.act_fill_00)
        menu.addSeparator()
        menu.addAction(self.readFlash)
        menu.addAction(self.writeFlash)
        menu.addSeparator()
        menu.addMenu(menuShow)
        menu.exec_(QCursor.pos())

    def actLoadFile(self):
        self.sigOpenFileDia.emit()
        self.act_load_file.triggered.disconnect()

    def acSaveAs(self):
        self.sigSaveFile.emit()
        self.act_saveas_file.triggered.disconnect()

    def fillDataFF(self):
        self.act_bit8.setChecked(True)
        self.act_bit16.setChecked(False)
        self.act_bit32.setChecked(False)
        self.flashData = [0xff for i in range(32768)]
        self.flashSize = 32
        data = self.parseFlash(self.flashData)
        self.insertTable(self.table, data)
        self.act_fill_FF.triggered.disconnect()

    def fillData00(self):
        self.act_bit8.setChecked(True)
        self.act_bit16.setChecked(False)
        self.act_bit32.setChecked(False)
        self.flashData = [0x00 for i in range(32768)]
        self.flashSize = 32
        data = self.parseFlash(self.flashData, default= 0x00)
        self.insertTable(self.table, data)
        self.act_fill_00.triggered.disconnect()

    def act8BitWidth(self):
        self.act_bit8.setChecked(True)
        self.act_bit16.setChecked(False)
        self.act_bit32.setChecked(False)
        data = self.parseFlash(self.flashData, size=self.flashSize)
        self.insertTable(self.table, data)
        self.insertOptData()
        self.act_bit8.triggered.disconnect()

    def act16BitWidth(self):
        self.act_bit8.setChecked(False)
        self.act_bit16.setChecked(True)
        self.act_bit32.setChecked(False)
        data = self.parseFlash(self.flashData, size=self.flashSize, state = 2)
        self.insertTable(self.table, data, state = 2)
        self.insertOptData(state = 2)
        self.act_bit16.triggered.disconnect()

    def act32BitWidth(self):
        self.act_bit8.setChecked(False)
        self.act_bit16.setChecked(False)
        self.act_bit32.setChecked(True)
        data = self.parseFlash(self.flashData, size=self.flashSize, state = 4)
        self.insertTable(self.table, data, state = 4)
        self.insertOptData(state = 4)
        self.act_bit32.triggered.disconnect()
    
    def actReadFlashSolt(self):
        self.sigReadData.emit()
        self.readFlash.triggered.disconnect()
    
    def actWriteFlashSolt(self):
        self.sigWriteData.emit()
        self.writeFlash.triggered.disconnect()

    # 处理从单片机获取的代码
    def parseFlash(self, flash: list, addr = 0x08000000, size = 32, state = 1, default = 0xff):
        if len(flash) == 0:
            flash = [default for i in range(size * 1024)]
        flashDict = {}
        for l in range(0, size * 1024, state * 16):
            flashDict["0x{:08X}".format(0x08000000 + l)] = []

        minAddr = addr
        maxAddr = addr + 1024 * size - 1

        data = []
        for i in range(minAddr, maxAddr + 1, state):
            index = i - minAddr
            if state == 1:
                data.append("{:02X}".format(flash[index]))
            elif state == 2:
                data.append("{:02X}".format(flash[index+1]) + "{:02X}".format(flash[index]))
            elif state == 4:
                data.append("{:02X}".format(flash[index+3]) + "{:02X}".format(flash[index+2]) + "{:02X}".format(flash[index+1]) + "{:02X}".format(flash[index]))

        cnt = 0
        for i in range(0, len(data), 16):
            key = "0x{:08X}".format(minAddr + 16 * state * cnt)
            flashDict[key] = data[i: i + 16]
            cnt += 1

        return flashDict

    # 处理opt信息
    def processOptData(self, data: list):
        optList = []
        if len(data) == 0: # 默认值
            optList = ["FF" for _ in range(64)]
        else:
            for i in data:
                tmp = "{:08X}".format(i)
                for j in range(len(tmp), 0, -2):
                    optList.append(tmp[j - 2: j])
        self.optData = optList

    # 填入opt信息
    def insertOptData(self, state = 1):
        optDict = {}
        optList = self.optData
        for i in range(0x1FFFF800, 0x1FFFF831, 16 * state):
            tmp = i - 0x1FFFF800
            if state == 1:
                optDict["0x{:08X}".format(i)] = optList[tmp: tmp + 16]
            elif state == 2:
                tmpData = optList[tmp: tmp + 32]
                tmpList = []
                for j in range(0, len(tmpData), 2):
                    tmpList.append(tmpData[j + 1] + tmpData[j])
                optDict["0x{:08X}".format(i)] = tmpList
            elif state == 4:
                tmpList = []
                for j in range(0, len(optList), 4):
                    tmpList.append(optList[j + 3] + optList[j + 2] + optList[j + 1] + optList[j])
                optDict["0x{:08X}".format(i)] = tmpList

        self.insertTable(self.optTable, optDict, state)

    # 将flash信息插入表格
    def insertTable(self, table: QTableWidget, data: typing.Optional[dict[str, list]] = None, state = 1):
        #清空列表
        table.setRowCount(0)
        table.clearContents()

        if data is None: # 初始界面默认32k，全FF
            flashDict = {}
            for l in range(0, 32768, state * 16):
                flashDict["0x{:08X}".format(0x08000000 + l)] = ["FF" for i in range(16 * state)]
            data = flashDict

        for key, value in data.items():
            row = table.rowCount()
            table.insertRow(row)
            table.setRowHeight(row, ROW_HEIGHT)
            addrItem = QTableWidgetItem(key)
            addrItem.setTextAlignment(Qt.AlignCenter)
            addrItem.setForeground(QBrush(QColor(248,248,255)))
            addrItem.setBackground(QBrush(QColor(128,128,128)))
            addrItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)
            table.setItem(row, 0, addrItem)
            value = self.translateAscii(value)
            for j in range(0, len(value)):
                newItem = QTableWidgetItem(value[j])
                newItem.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, j + 1, newItem)

        self.setCellSize(table, state)