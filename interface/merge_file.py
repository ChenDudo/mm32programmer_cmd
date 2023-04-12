from PyQt5.QtWidgets import QDialog, QFileDialog, QTableWidgetItem
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from UI.Ui_mergeFile import Ui_Dialog
from interface.open_binfile import OpenBinFile
from intelhex import IntelHex
import os
import bincopy
from io import StringIO


class MergeFile(QDialog, Ui_Dialog):

    sigMergeFile = pyqtSignal(str, dict)
    sigSaveFile = pyqtSignal(str)

    def __init__(self, parent: None, length: int):
        QDialog.__init__(self, parent)
        self.length = length
        self.setupUi(self)
        self.initSet()
    
    def initSet(self):
        self.infoList = [] # 存储表格的文件的信息
        self.tableWidget.setColumnWidth(0, 40) # id
        self.tableWidget.setColumnWidth(1, 120) # file
        self.tableWidget.setColumnWidth(2, 80) # addr
        self.tableWidget.setColumnWidth(3, 80) # length
        
        self.setUpDownEnable(False, False)
        self.setBtnEnable(False)
        self.tableWidget.currentCellChanged.connect(self.upDownEnable)

    @pyqtSlot()
    def on_addBtn_clicked(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "select data file", "C:\\", "Inter Hex files(*.hex);;Binary files(*.bin);;Motorola files(*.s19)")
        if os.path.exists(filePath):
            self.setBtnEnable(True)
            self.loadFile(filePath)
    
    # 设置up和down按钮的使能
    def upDownEnable(self, row:int): # 信号发送的第一个数据，单元格发生变化后，当前的单元格行号
        rowCnt = self.tableWidget.rowCount()
        if row == 0: # 第一行
            if row + 1 == rowCnt: # 只有一行
                self.setUpDownEnable(False, False)
            else:
                self.setUpDownEnable(False, True)
        elif row + 1 == rowCnt: # 最后一行
            self.setUpDownEnable(True, False)
        else:
            self.setUpDownEnable(True, True)
    
    @pyqtSlot()
    def on_upBtn_clicked(self):
        self.upDownSolt(True)
    
    @pyqtSlot()
    def on_downBtn_clicked(self):
        self.upDownSolt(False)
    
    @pyqtSlot()
    def on_closeBtn_clicked(self):
        self.close()
    
    def upDownSolt(self, state: bool):
        row = self.tableWidget.currentRow()
        if state: # up
            curRow = row - 1
        else: # down
            curRow = row + 1
        temp = self.infoList[curRow]
        self.infoList[curRow] = self.infoList[row]
        self.infoList[row] = temp

        currentItemInfo = [self.tableWidget.item(row, column).text() for column in range(1, self.tableWidget.columnCount())]
        downerItemInfo = [self.tableWidget.item(curRow, column).text() for column in range(1, self.tableWidget.columnCount())]
        for column in range(1, self.tableWidget.columnCount()):
            currentItem = self.tableWidget.item(row, column)
            downerItem = self.tableWidget.item(curRow, column)
            currentItem.setText(downerItemInfo[column - 1])
            downerItem.setText(currentItemInfo[column - 1])
        self.tableWidget.setCurrentCell(curRow, 0)
    
    @pyqtSlot()
    def on_deleteBtn_clicked(self):
        row = self.tableWidget.rowCount()
        curRow = self.tableWidget.currentRow()
        self.tableWidget.removeRow(curRow)
        del self.infoList[curRow]
        for i in range(row):
            idItem = QTableWidgetItem(str(i + 1))
            idItem.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(i, 0, idItem)
        if row == 1: # 只有一行
            self.setUpDownEnable(False, False)
            self.setBtnEnable(False)
        else:
            if curRow == 0: # 想删除的行是第一行时，聚焦下一行
                self.tableWidget.setCurrentCell(curRow + 1, 0)
            else:
                self.tableWidget.setCurrentCell(curRow - 1, 0)
    
    @pyqtSlot()
    def on_mergeBtn_clicked(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "save file", "C:\\", "Inter Hex files(*.hex);;Binary files(*.bin);;Motorola files(*.s19)") 
        if filePath != "":
            dataDict = {}
            for i in range(self.length):
                dataDict[i + 0x08000000] = 0xff
            ihAll = IntelHex(dataDict) 
            for info in self.infoList:
                file = str(info["fullPath"])
                addr = str(info["address"])
                ihTmp = self.fileWithSize(file, addr)
                ihAll.merge(ihTmp, overlap='replace')

            mergeDict = ihAll.todict()
            if isinstance(list(mergeDict)[-1], str):
                del mergeDict[list(mergeDict)[-1]]

            self.sigMergeFile.emit(filePath, mergeDict)
            self.sigSaveFile.emit(f"Merge file ---> merge file@{filePath} Success")
        else:
            pass
    
    # 将需要合并的文件先扩展为内存的大小
    def fileWithSize(self, file: str, binStart: str):
        ih = IntelHex()
        if file.endswith(".hex"):
            ih.fromfile(file, "hex") 
        elif file.endswith(".bin"):
            ih.loadbin(file, offset = int(binStart, 16))
        elif file.endswith(".s19"):
            bc = bincopy.BinFile(file)
            ih.loadhex(StringIO(bc.as_ihex()))
        ihDict = ih.todict()
        if isinstance(list(ihDict)[-1], str):
            del ihDict[list(ihDict)[-1]]
        
        return IntelHex(ihDict)


    def setUpDownEnable(self, upBool: bool, downBool: bool):
        self.upBtn.setEnabled(upBool)
        self.downBtn.setEnabled(downBool)

    def addDataFile(self, file: str, binStart = 0x08000000, binEnd = 0x08007FFF, defalut = 0xff):
        fileInfo = {}

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

        if file.endswith(".bin"): 
            maxaddr = binEnd
        difference = maxaddr - minaddr + 1 # 再更新一下

        (filePath, fileName) = os.path.split(file)
        fileInfo["file"] = fileName
        fileInfo["address"] = "0x{:08X}".format(minaddr)
        fileInfo["length"] = str(difference)
        fileInfo["path"] = filePath
        fileInfo["fullPath"] = file

        return fileInfo

    def insertTable(self, fileInfo: dict):
        row = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row)
        self.infoList.append(fileInfo)
        for i in range(5):
            if i == 0:
                tableItem = QTableWidgetItem(str(row + 1))
            elif i == 1:
                tableItem = QTableWidgetItem(fileInfo["file"])
            elif i == 2:
                tableItem = QTableWidgetItem(fileInfo["address"])
            elif i == 3:
                tableItem = QTableWidgetItem(fileInfo["length"])
            elif i == 4:
                tableItem = QTableWidgetItem(fileInfo["path"])
            tableItem.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(row, i, tableItem)
        self.tableWidget.setCurrentCell(row, 0)

 
    def loadFile(self, filePath: str):
        if filePath.endswith(".hex") or filePath.endswith(".s19"):
            info = self.addDataFile(filePath)
            self.insertTable(info)
        elif filePath.endswith(".bin"):
            flashSize = int(self.length / 1024)
            binLoad = OpenBinFile(flashSize, self)
            if binLoad.exec_():
                start = binLoad.start.text()
                end = binLoad.end.text()
                ck = "FF" if binLoad.checkBox.isChecked() else "00"
                info = self.addDataFile(filePath, int(start, 16), int(end, 16), int(ck, 16))
                self.insertTable(info)
    
    def setBtnEnable(self, state: bool):
        self.deleteBtn.setEnabled(state)
        self.mergeBtn.setEnabled(state)
        
    


# 合并文件
# 添加文件信息，添加一行
# 文件可上下移动，当前行数变化就触发信号，修改上下移动按钮的使能，且没有ID的行不能选中
# 删除文件信息，删除一行