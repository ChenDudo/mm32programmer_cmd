from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QAbstractItemView, QGridLayout, QAction, QMenu
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QIcon, QBrush, QColor, QFont
from intelhex import IntelHex
import os
import typing
import bincopy
from io import StringIO


ROW_HEIGHT = 15

class ReadFlash(QWidget):

    sigOpenFileDia = pyqtSignal()
    sigSaveFile = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        self.table = QTableWidget(self)
        layout.addWidget(self.table)
        self.setLayout(layout)
        layout.setContentsMargins(0,0,0,0)

        # 记录当前读取的文件
        self.file = "" # 为了记住flash当前展示的是那个文件，主界面加载或拖拽文件时，也会更新该参数，方便各字节显示
        self.flashSize = 64 # 同上，方便flash开内存(最大地址)显示

        self.table.verticalHeader().setVisible(False) #隐藏列表头
        self.table.horizontalHeader().setVisible(False) #隐藏行表头
        self.table.setShowGrid(False) #隐藏表格线
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers) #只读不可修改
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus) #选中表格数据不着重显示

        self.table.setColumnCount(33)
        self.table.setColumnWidth(0, 85)
        self.table.verticalHeader().setMinimumSectionSize(ROW_HEIGHT)

        # 初始值
        self.insert_table()

        # 右击菜单
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.slotShowMenu)
        self.actAction()
    
    def set_row_height(self):
        rowcount = self.table.rowCount()
        for i in range(rowcount):
            self.table.setRowHeight(i, ROW_HEIGHT)
        self.table.viewport().update()

    def actAction(self):
        self.act_bit8 = QAction("Byte")
        self.act_bit8.setCheckable(True) #设置actoion可选中
        self.act_bit8.setChecked(True) #设置为当前选中状态
        self.act_bit16 = QAction("Word")
        self.act_bit16.setCheckable(True)
        self.act_bit32 = QAction("DWord")
        self.act_bit32.setCheckable(True)
        self.act_bit8.triggered.connect(self.act8BitWidth)
        self.act_bit16.triggered.connect(self.act16BitWidth)
        self.act_bit32.triggered.connect(self.act32BitWidth)

    # 右击菜单栏
    def slotShowMenu(self):
        act_load_file = QAction("Load Programer File")
        act_load_file.setIcon(QIcon(":/icon/icon/6.png"))
        act_saveas_file = QAction("Save As File")
        act_saveas_file.setIcon(QIcon(":/icon/icon/5.png"))
        act_fill_FF = QAction("Fill Data->$FF")
        act_fill_00 = QAction("Fill Data->$00")
        menuShow = QMenu("DataWidth")

        menuShow.addAction(self.act_bit8)
        menuShow.addAction(self.act_bit16)
        menuShow.addAction(self.act_bit32)

        act_load_file.triggered.connect(self.actLoadFile)
        act_saveas_file.triggered.connect(self.acSaveAs)
        act_fill_FF.triggered.connect(self.fillDataFF)
        act_fill_00.triggered.connect(self.fillData00)

        menu = QMenu()
        menu.addAction(act_load_file)
        menu.addAction(act_saveas_file)
        menu.addSeparator()
        menu.addAction(act_fill_FF)
        menu.addAction(act_fill_00)
        menu.addSeparator()
        menu.addMenu(menuShow)
        menu.exec_(QCursor.pos())

    def actLoadFile(self):
        self.sigOpenFileDia.emit()

    def acSaveAs(self):
        self.sigSaveFile.emit()

    def fillDataFF(self):
        self.insert_table()

    def fillData00(self):
        self.insert_table(default="00")

    def act8BitWidth(self):
        self.act_bit8.setChecked(True)
        self.act_bit16.setChecked(False)
        self.act_bit32.setChecked(False)
        if self.file == "":
            self.insert_table()
        else:
            data = self.parse_file(self.file, size=self.flashSize)
            self.insert_table(data)

    def act16BitWidth(self):
        self.act_bit8.setChecked(False)
        self.act_bit16.setChecked(True)
        self.act_bit32.setChecked(False)
        if self.file == "":
            self.insert_table(state = 2)
        else:
            data = self.parse_file(self.file, size=self.flashSize, state = 2)
            self.insert_table(data, state = 2)

    def act32BitWidth(self):
        self.act_bit8.setChecked(False)
        self.act_bit16.setChecked(False)
        self.act_bit32.setChecked(True)
        if self.file == "":
            self.insert_table(state = 4)
        else:
            data = self.parse_file(self.file, size=self.flashSize, state = 4)
            self.insert_table(data, state = 4)

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

    def parse_file(self, file: str, binStart = 0x08000000, binEnd = 0x08007FFF, size = 64, state = 1, defalut = "FF") -> dict: 
        self.file = file
        # 根据size大小，新建dict，key值存放地址，value存放数据（长度为16的列表）
        flashDict = {}
        flashMaxAddr = 0x08000000 + size * 1024 - 1
        for l in range(0, size * 1024, state * 16):
            flashDict["0x0800{:04X}".format(l)] = []
        # 获取数据，根据地址和需要展示的长度塞进flashDict
        ih = IntelHex()
        if file.endswith(".hex"):
            ih.fromfile(file, "hex") 
        elif file.endswith(".bin"):
            ih.loadbin(file, offset = binStart)
        elif file.endswith(".s19"):
            bc = bincopy.BinFile(file)
            ih.loadhex(StringIO(bc.as_ihex())) # 数据读写不一定是文件对象，也可以在内存中读写（临时缓冲）
        
        ih.padding = int(defalut, 16)
        minaddr = ih.minaddr()
        maxaddr = ih.maxaddr()

        # 处理超出flash地址范围的情况
        if maxaddr > flashMaxAddr:
            maxaddr = flashMaxAddr
        if minaddr < 0x08000000: # 如果是这种情况，根本就没值
            minaddr = 0x08000000
            maxaddr = minaddr + maxaddr

        # 加载bin文件的结束地址
        if file.endswith(".bin"): 
            maxaddr = binEnd

        # 处理初始地址不是正好0x10倍数的情况
        if "0x{:08X}".format(minaddr) in flashDict.keys():
            pass
        else:
            addrList = ih.addresses()[0 : 16 * state]
            for i in range(0, len(addrList)):
                if "0x{:08X}".format(addrList[i]) in flashDict.keys():
                    minaddr = addrList[i] - 16 * state

        # 按字节获取所有数据
        data = []
        for i in range(minaddr, maxaddr + 1, state): # 切记for循环遍历不到__stop的值，比如range(0, 10, 1) 循环十次，i=10结束
            if state == 1:
                data.append("{:02X}".format(ih[i]))
            elif state == 2:
                data.append("{:02X}".format(ih[i+1]) + "{:02X}".format(ih[i]))
            elif state == 4:
                data.append("{:02X}".format(ih[i+3]) + "{:02X}".format(ih[i+2]) + "{:02X}".format(ih[i+1]) + "{:02X}".format(ih[i]))

        # 每个列表放16个数据
        cnt = 0
        for i in range(0, len(data), 16):
            key = "0x{:08X}".format(minaddr + 16 * state * cnt)
            flashDict[key] = data[i: i + 16]
            cnt += 1

        return flashDict

    def insert_table(self, data: typing.Optional[dict[str, list]] = None, state = 1, default = "FF"):
        #清空列表，并根据state重新划分列宽
        self.table.setRowCount(0)
        self.table.clearContents()
        # font = QFont()
        # font.setPointSize(8)

        for i in range(1, 33):
            if i > 16:
                self.table.setColumnWidth(i, 10 * state) # ascii
            else:
                self.table.setColumnWidth(i, 19 * state) # data

        if data is None: # 初始界面默认64k，全FF
            flashDict = {}
            for l in range(0, 65536, state * 16):
                flashDict["0x0800{:04X}".format(l)] = []
            data = flashDict

        for key, value in data.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            addrItem = QTableWidgetItem(key)
            addrItem.setTextAlignment(Qt.AlignCenter)
            addrItem.setForeground(QBrush(QColor(248,248,255)))
            addrItem.setBackground(QBrush(QColor(128,128,128)))
            addrItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)
            self.table.setItem(row, 0, addrItem)
            if len(value) != 16:
                value.extend([default * state] * (16 - len(value)))
            value = self.translate_ascii(value)
            for j in range(0, len(value)):
                newItem = QTableWidgetItem(value[j])
                newItem.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, j + 1, newItem)
            # self.table.resizeColumnsToContents()
        self.set_row_height()

    def translate_ascii(self, hexData: list) -> list:
        asciiData = []
        for i in range(len(hexData)):
            asciiData.append((bytearray.fromhex(hexData[i])).decode('utf-8', 'ignore'))
        return hexData + asciiData

    def save_table_data(self) -> dict[int, int]:
        flashDict = {}
        row = self.table.rowCount() # 行，与flashsize有关
        for i in range(row): # 行
            address = int(self.table.item(i, 0).text(), 16)
            for j in range(1, 17): # 列， 从第一列开始，到后16列
                itemData = self.table.item(i, j).text()
                length = len(itemData)
                while(length > 0):
                    flashDict[address] = int(itemData[length - 2 : length], 16)
                    length -= 2
                    address += 1
        return flashDict
    
    def save_code_file(self, file: str, data: dict[int, int]):
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

# 只有bin文件可以指定是00填充或者FF填充，以及起始地址和结束地址
# hex和s19文件默认以FF填充数据
# 拖拽文件必须有新建项目(tree有数据显示)，读数据开大小跟项目的flashsize有关
# 样式设计，tooltip莫名出现的问题
