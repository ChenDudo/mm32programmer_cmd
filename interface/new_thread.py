from PyQt5.QtCore import pyqtSignal, QThread
import interface.pyocd_api as api
import time


class WriteThread(QThread):

    signalOutPut = pyqtSignal(str) # 输出日志
    signalProgress = pyqtSignal(int) # 传递读取的字节数
    sigalFail = pyqtSignal(str) # 输出错误

    def __init__(self, series: str, sectors: dict, flashData: list, speed: int) -> None:
        super().__init__()
        self.series = series
        self.sectors = sectors
        self.data = flashData
        self.speed = speed

    def run(self):
        for key, value in self.sectors.items(): 
            start = time.time()
            state = api.writeMemory(self.series, key, self.data[key: key + value], self.speed)
            if state:
                self.signalProgress.emit(value) # 读取的字节数
            else: # 由于按连续扇区写的，如果出错，判断不出来是哪个扇区的问题
                sectorl = "0x{:08X}".format(0x08000000 + key)
                sectorr = "0x{:08X}".format(0x08000000 + key + value - 1)
                self.sigalFail.emit(f"    Write Chip Sector ---> {sectorl} - {sectorr} Failure")
                return
        end = time.time()
        self.signalOutPut.emit(f"Write Chip ---> End Success, Time:{round(end - start, 2)}sec")

class EraseThread(QThread):

    signalOutPut = pyqtSignal(str)
    signalProgress = pyqtSignal(int)
    signalFail = pyqtSignal(str)

    def __init__(self, series: str, sectors: dict, flashSize: int, speed: int) -> None:
        super().__init__()
        self.series = series
        self.sectors = sectors
        self.flashSize = flashSize
        self.speed = speed

    def run(self):
        start = time.time()
        if len(self.sectors) == 0: 
            state = api.eraseFillChip(self.series, self.speed)
            if state:
                self.signalProgress.emit(self.flashSize * 1024)
                end = time.time()
                self.signalOutPut.emit(f"Erase Chip ---> Size@{self.flashSize}KBytes Success, Time:{round(end - start, 2)}sec")
                return
            else:
                self.signalFail.emit("Erase Chip ---> Failure")
                return
        else:
            for key, value in self.sectors.items(): 
                state = api.eraseSectors(self.series, key, value, self.speed)
                if state:
                    self.signalProgress.emit(value)
                else: 
                    sectorl = "0x{:08X}".format(0x08000000 + key)
                    sectorr = "0x{:08X}".format(0x08000000 + key + value - 1)
                    self.signalFail.emit(f"    Erase Chip Sector ---> {sectorl} - {sectorr} Failure")
                    return
            end = time.time()
            self.signalOutPut.emit(f"Erase Chip Sector ---> End Success, Time:{round(end - start, 2)}sec")

class ReadThread(QThread):

    signalOutPut = pyqtSignal(str)
    signalProgress = pyqtSignal(int)
    signalFail = pyqtSignal(str)
    signalData = pyqtSignal(list, list, int)

    def __init__(self, series: str, sectors: dict, flashSize: int, speed) -> None:
        super().__init__()
        self.series = series
        self.sectors = sectors
        self.fsize = flashSize
        self.speed = speed

    def run(self):
        start = time.time()
        flashData = []
        optData = []
        tempSize = 0
        while(tempSize < self.fsize * 1024):
            if tempSize in self.sectors.keys():
                key = tempSize
                value = self.sectors[tempSize]
                data = api.readMemory(self.series, key, value, self.speed)
                if len(data):
                    self.signalProgress.emit(value)
                    flashData += data
                    tempSize += self.sectors[tempSize]
                else: # 读取失败
                    sectorl = "0x{:08X}".format(0x08000000 + key)
                    sectorr = "0x{:08X}".format(0x08000000 + key + value - 1)
                    self.signalFail.emit(f"    Read Chip Sector ---> {sectorl} - {sectorr} Failure")
                    return
            else:
                flashData += [0xff for _ in range(4096)]
                tempSize += 4096
        
        # 获取optData addr:0x1FFFF800, length:16
        optData = api.readAnyMemory(0x1FFFF800, 16, self.speed)

        self.signalData.emit(flashData, optData, self.fsize)
        end = time.time()
        self.signalOutPut.emit(f"Read Chip ---> End Success, Time:{round(end - start, 2)}sec")

class BlankThread(QThread):

    signalProgress = pyqtSignal(int)
    signalClose = pyqtSignal(str) # 检测到扇区非空则关闭
    signalFail = pyqtSignal(str) # 读取失败

    def __init__(self, series: str, length: int, speed: int) -> None:
        super().__init__()
        self.series = series
        self.length = length
        self.speed = speed
    
    def run(self):
        start = time.time()
        key = 0
        comp = [0xff for i in range(4096)]
        while(key < self.length):
            data = api.readMemory(self.series, key, 4096, self.speed) # 每次检测一个扇区
            if len(data) == 4096: # 读取成功
                if data == comp: # 空扇区
                    self.signalProgress.emit(4096)
                else:
                    sectorl = "0x{:08X}".format(0x08000000 + key)
                    self.signalClose.emit(f"Chip blank ---> Chip data is not empty, address@{sectorl}")
                    return
                key += 4096
            else: # 读取失败
                sectorl = "0x{:08X}".format(0x08000000 + key)
                self.signalFail.emit(f"Chip blank ---> check address@{sectorl} Failure")
                return
        end = time.time()
        self.signalClose.emit(f"Chip Blank ---> Chip is empty, Time: {round(end - start, 2)}sec")

class VerityThread(QThread):

    signalProgress = pyqtSignal(int)
    signalClose = pyqtSignal(str)
    signalFail = pyqtSignal(str)

    def __init__(self, series: str, length: int, data: list, speed: int) -> None:
        super().__init__()
        self.series = series
        self.length = length
        self.currentData = data
        self.speed = speed
    
    def run(self): # 按扇区读取数据，再对比当前数据
        start = time.time()
        key = 0
        while(key < self.length):
            flashData = api.readMemory(self.series, key, 4096, self.speed) # 每次检测一个扇区
            curData = self.currentData[key: key + 4096]
            if len(flashData) == 4096: # 读取成功
                if flashData == curData: # 当前数据与flash一致
                    self.signalProgress.emit(4096)
                else:
                    sectorl = "0x{:08X}".format(0x08000000 + key)
                    self.signalClose.emit(f"Chip Verify ---> chip data is inconsistent with the current data, address@{sectorl}")
                    return
                key += 4096
            else: # 读取失败
                sectorl = "0x{:08X}".format(0x08000000 + key)
                self.signalFail.emit(f"Chip Verify ---> check address@{sectorl} Failure")
                return
        
        end = time.time()
        self.signalClose.emit(f"Chip Verify ---> chip data is consistent with the current data, Time: {round(end - start, 2)}sec")

class OptByteThread(QThread): # f0130系列需要特殊对待读保护 api.optWrite(0x1FFE0000, [0x7F80, 0xFF00]) 0x1FFFF800 user...

    signalFail = pyqtSignal(str)
    signalProgress = pyqtSignal(int)
    signalClose = pyqtSignal(str)

    def __init__(self, addr: int, data: list, speed) -> None:
        super().__init__()
        self.addr = addr
        self.data = data
        self.speed = speed
    
    def run(self):
        # if self.state: # 加读保护
        eraseState = api.optErase(self.addr, self.speed)
        if eraseState:
            self.signalProgress.emit(50)
            writeState = api.optWrite(self.addr, self.data, self.speed)
            if writeState:
                self.signalProgress.emit(100)
                self.signalClose.emit("Enable Readout Protection ---> Success")
            else:
                self.signalFail.emit("Enable Readout Protection ---> Failure")
        else:
            self.signalFail.emit("Enable Readout Protection ---> Failure")
        # else: # 写opt byte
        #     writeState = api.optWrite(self.addr, self.data, self.speed)
        #     self.signalProgress.emit(50)
        #     if writeState:
        #         self.signalProgress.emit(100)
        #         self.signalClose.emit("Enable Readout Protection ---> Success")
        #     else:
        #         self.signalFail.emit("Enable Readout Protection ---> Failure")
