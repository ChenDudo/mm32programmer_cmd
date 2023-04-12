import sys
sys.path.append(r"C:\Users\MM\gitworks\10.3.2.202\embeded-group2\mm32program")
from access_pyocdAPI import LinkerObject

_ID_DEV = {"0x8C4350D1": ["MM32F0010"],
           "0x4C50F800": ["MM32F0020"],
           "0x4C50E800": ["MM32F0040", "MM32F0140", "MM32G0140"],
           "0xCC5680C7": ["MM32F0130"],
           "0x4C50E900": ["MM32F0160"],
           "0xCC5680F1": ["MM32F0270"],
           "0x4C512000": ["MM32L0020"],
           "0x4C4D1000": ["MM32L0130"],
           "0xCC9AA0E7": ["MM32F3270"],
           "0x4D4D0800": ["MM32F5270"]}

# 检测是否有link连接，有则返回真，反之假
def checkLink(speed: int):
    api = LinkerObject()
    api.speed = speed
    linkList = list(api.outputGetLinker()["data"])
    if len(linkList) != 0:
        return True
    else:
        return False

# 获取mcu
def recognizeMCU(speed: int):
    api = LinkerObject()
    api.speed = speed
    mcuList = list(api.selectLinker()["data"])

    if len(mcuList) != 0:
        devId = "0x{:08X}".format(mcuList[0]["DEV_ID"])
        if devId in _ID_DEV:
            mcu = _ID_DEV[devId]
            return mcu
        else:
            return 2 # 表示当前设备ID未收录
    else:
        return 1 # 表示未连接到任何设备
    
# 读取flash
def readMemory(series: str, addr: int, length: int, speed: int):
    api = LinkerObject()
    api.speed = speed
    api.setTarget(series)
    api.oprateAddr = addr # 默认起始地址为0x0800_0000
    api.oprateSize = length # 默认读取地址
    message = api.readChip()
    if "[info] Read Success" in message["message"]:
        return message["data"]
    else:
        return []
    
# 全片擦除
def eraseFillChip(series: str, speed: int):
    api = LinkerObject()
    api.speed = speed
    api.setTarget(series)
    message = api.earseChip()
    print(message)
    if "[info] Earse Success" in message["message"]:
        return True
    else:
        return False
    
# 写flash
def writeMemory(series: str, addr: int, data: list, speed: int):
    api = LinkerObject()
    api.speed = speed
    api.setTarget(series)
    api.oprateAddr = addr # 0x08000000
    api.wrbuff = data
    message = api.writeChip()
    if "[info] Write Success" in message["message"]:
        return True
    else:
        return False
    
# 按扇区擦除
def eraseSectors(series: str, addr: int, length: int, speed: int):
    api = LinkerObject()
    api.speed = speed
    api.setTarget(series)
    api.oprateAddr = addr
    api.oprateSize = length
    message = api.earseSector()
    if "[info] Earse Success" in message["message"]:
        return True
    else:
        return False

def optErase(optAddr: int, speed: int):
    api = LinkerObject()
    api.speed = speed
    eraseMessage = api.optionByteEarse(optAddr)
    print(eraseMessage)
    if "[info] OPT Earse Success." in eraseMessage["message"]:
        return True
    else:
        return False


# 写optionbyte
def optWrite(optAddr: int, data: list, speed: int):
    api = LinkerObject()
    api.speed = speed
    writeMessage = api.optionByteProgram(optAddr, data)
    print(writeMessage)
    if "[info] OPT Program Success." in writeMessage["message"]:
        return True
    else:
        return False

# 擦除后直接写
def optOpertion(optAddr: int, data: list):
    api = LinkerObject()
    eraseMessage = api.optionByteEarse(optAddr)
    if "[info] OPT Earse Success." in eraseMessage["message"]:
        writeMessage = api.optionByteProgram(optAddr, data)
        print(writeMessage)
        if "[info] OPT Program Success." in writeMessage["message"]:
            return True
        else:
            return False
    else:
        return False

def readAnyMemory(addr: int, length: int, speed: int):
    api = LinkerObject()
    api.speed = speed
    message = api.readMem32(addr, length)
    print(message)
    if "[info] readMem32 Success" in message["message"]:
        return message["data"]
    else:
        return []

# if __name__ == "__main__":
#     api = LinkerObject()
#     optErase(0x1FFFF800)
#     optWrite(0x1FFFF800, [0xDE21])


