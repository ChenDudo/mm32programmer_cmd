# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    :   mm32program.py
@Time    :   2023/02/20 13:12:52
@Author  :   Chen Do
@Version :   1.0
@Desc    :   None
"""

import time
import device
import xlink

from pyocd.probe import aggregator
from pyocd.coresight import dap, ap, cortex_m

# Debug
Debug = 1
DonePrint = 0
timeShow = 1

# Flash Define
FLASH_KEYR_addr     =  (0x40022000 + 0x04)
FLASH_OPTKEYR_addr  =  (0x40022000 + 0x08)
FLASH_SR_addr       =  (0x40022000 + 0x0C)
FLASH_CR_addr       =  (0x40022000 + 0x10)
FLASH_AR_addr       =  (0x40022000 + 0x14)

FLASH_CR_OPTWRE     =  (1 << 9)
FLASH_CR_LOCK       =  (1 << 7)
FLASH_CR_STRT       =  (1 << 6)
FLASH_CR_OPTER      =  (1 << 5)
FLASH_CR_OPTPG      =  (1 << 4)
FLASH_CR_MER        =  (1 << 2)
FLASH_CR_PER        =  (1 << 1)
FLASH_CR_PG         =  (1 << 0)

FLASH_SR_BSY        =  (1 << 0)
FLASH_SR_PGERR      =  (1 << 2)
FLASH_SR_WRPRTERR   =  (1 << 4)
FLASH_SR_EOP        =  (1 << 5)

def formatTime():
    return time.strftime("[%Y-%m-%d %H:%M:%S]", (time.localtime(time.time())))

def log_print(text):
    if Debug:
        print("%s %s" % (formatTime(), text))

class returnJson():
    def __init__(self):
        self.owndict = {
            'code':0,
            'message':'',
            'data':[]
        }

    def uninit(self):
        self.clearMessage()
        self.clearCode()
        self.clearData()

    def clearMessage(self):
        self.owndict['message'] = ''

    def clearData(self):
        self.owndict['data'] = []

    def clearCode(self):
        self.owndict['code'] = 0

    def setCode(self, num):
        self.owndict['code'] = num
    
    def getCode(self):
        return self.owndict['code']

    def appendMes(self, str):
        self.owndict['message'] = self.owndict['message'] + (str)

    # def output(self):
    #     return json.dumps(self.owndict)


class LinkerObject(returnJson):
    def __init__(self):
        super(LinkerObject, self).__init__()

        self.daplinks = []
        self.daplink = None
        self.selectIdx = 0
        
        self.xlk = None
        self.dev = None
        self.target = 'MM32F0010'
        self.speed = 1000000

        self.wrbuff = []
        self.rdbuff = []
        self.oprateAddr = 0
        self.oprateSize = 0

    def setTarget(self, targetname):
        self.target = targetname

    def setSelectIdx(self, idx):
        self.selectIdx = idx

    def setOprateAddr(self, addr):
        self.oprateAddr = addr

    def setOprateSize(self, size):
        self.oprateAddr = size

    def getRxbuff(self):
        return self.rxbuff

    def setWrbuff(self, data):
        self.wrbuff = data

    # ### local function
    # def _getLinker(self):
    #     self.daplinks = aggregator.DebugProbeAggregator.get_all_connected_probes()
    #     return self.daplinks

    ############################################################################
    # step 1: scan Linker
    # return 0: scan ok
    # return 6: Scan found none LINK
    ############################################################################
    def scanLinker(self):
        self.daplinks = aggregator.DebugProbeAggregator.get_all_connected_probes()
        if not len(self.daplinks):
            self.setCode(6)
            self.appendMes("ERROR: MM32LINK Not Found. Please Check LINK Power.")
            return
        # return json string
        for i, daplink in enumerate(self.daplinks):
            linker_dict = {
            'uid':'',
            'product':'',
            'vendor':''
            }
            linker_dict['uid']      = daplink.unique_id
            linker_dict['product']  = daplink.product_name
            linker_dict['vendor']   = daplink.vendor_name
            self.owndict['data'].append(linker_dict)

    # connect device
    ## return 0: OK
    ## return 1: connect failed
    def _connectDAP__(self):
        try:
            # Start Connect
            self.daplink = self.daplinks[self.selectIdx]
            self.daplink.set_clock(self.speed)
            try:
                self.daplink.open()
            except AssertionError:
                self.daplink.close()
                self.daplink.open()
            # Get DP
            self.target_iDP = dap.DebugPort(self.daplink, None)
            self.target_iDP.init()
            self.target_iDP.power_up_debug()
            # Get AP
            self.target_iAP = ap.AHB_AP(self.target_iDP, 0)
            self.target_iAP.init()
            # Get xLINK
            self.xlk = xlink.XLink(cortex_m.CortexM(None, self.target_iAP))
            # self.xlk.reset()
            # self.xlk.close()
        except Exception as e:
            log_print("Warning: connect dap failed.%s" % (str(e)))
            try:
                self.daplink.close()
            except Exception as e:
                log_print("WARNING: LINK -> Closed.")
            return 1
        return 0

    ############################################################################
    # step 2: scan Target MCU
    # return 1: idx out of range
    # return 2: Access Target MCU DAP Failed
    ############################################################################
    def scanTargetMCU(self):
        if self.selectIdx >= len(self.daplinks):
            try:
                self.setCode(1)
                self.appendMes("ERROR: select Linker_idx Out Of Range:%d." % (len(self.deviceUIDs)))
            except Exception as e:
                self.appendMes("ERROR: Please use 'devicelist' scan again.")
        else:
            try:
                pUID = self.daplinks[self.selectIdx].unique_id
                pName = self.daplinks[self.selectIdx].product_name
                self.appendMes("INFO: Selected linker_idx=%d, linker_UID=%s, linker_name=%s." % (self.selectIdx, pUID, pName))

                if not self._connectDAP__():
                    # init DEVInfo
                    cpuinfo = ''
                    devid = ''
                    mcuInfo_dict = {
                        'MCU_ID':0,
                        'CPU_INFO':'',
                        'DEV_ID':0
                    }
                    # Get DEVInfo
                    self.MCUID = self.target_iDP.read_id_code()
                    self.M0_DEV_ID = self.xlk.read_mem_U32(0x40013400, 1)[0]
                    self.Mx_DEV_ID = self.xlk.read_mem_U32(0x40007080, 1)[0]
                    self.CPUINFO = cortex_m.CortexM(None, self.target_iAP)._read_core_type()
                    if (self.CPUINFO):
                        cpuinfo = self.CPUINFO[0] + ' r'+str(self.CPUINFO[1])+'p'+str(self.CPUINFO[2])
                    if (self.MCUID == 0x0BB11477) or (self.MCUID == 0x0BC11477):
                        devid = self.M0_DEV_ID
                    else:
                        devid = self.Mx_DEV_ID
                    # Set DEVInfo
                    mcuInfo_dict['MCU_ID'] = self.MCUID
                    mcuInfo_dict['CPU_INFO'] = cpuinfo
                    mcuInfo_dict['DEV_ID'] = devid
                    self.owndict['data'].append(mcuInfo_dict)
                    # Return True
                    self.xlk.close()
                    # self.daplink.close()
                    # self.setCode(0)
                    # self.appendMes("INFO: Scan Target MCU.")
                else:
                    self.setCode(2)
                    self.appendMes("ERROR: Access Target MCU DAP Failed.")
            except Exception as e:
                log_print("Warning: %s" % (str(e)))
                self.setCode(3)
                self.appendMes("ERROR: oprate Failed.")
            finally:
                self.xlk = None
                self.target_iDP = None
                self.target_iAP = None
                # self.daplink.close()
            # except Exception as e:
            #     log_print("WARNING: LINK close.%s" % (str(e)))
            #     self.setCode(0)
            #     self.appendMes("WARNING: Link Close.")

    ############################################################################
    # step 3: connect Target MCU
    # return 0: OK
    # return 2: connect Target DAP failed
    ############################################################################
    def connectTargetMCU(self):
        if self._connectDAP__():
            self.setCode(2)
            self.appendMes("ERROR: Access Target MCU DAP Failed.")
        else:
            try:
                self.dev = device.Devices[self.target](self.xlk)
            except Exception as e:
                log_print("Warning: open device failed.%s" % (str(e)))
                self.setCode(1)
                self.appendMes("ERROR: Access Target Device Failed.")

    ############################################################################
    # step 4.1 : earse Chip
    # return 3: operate failed
    ############################################################################
    def earseChip(self):
        if not self.dev:
            self.setCode(5)
            self.appendMes("Error: Target Device is None.Please use ConnectDevice to get.")
            log_print("Warning: Please use ConnectDevice to get Dev.")
            return
        try:
            self.dev.chip_erase()
        except AssertionError:
            log_print("Warning: AssertionError")
        # except Exception as e:
        #     log_print("Warning: earse chip failed.%s" % (str(e)))
            self.setCode(3)
            self.appendMes("INFO: Earse Chip Failed.")

    ############################################################################
    # step 4.2 : earse Sector
    # return 3: operate failed
    ############################################################################
    def earseSector(self):
        if not self.dev:
            self.setCode(5)
            self.appendMes("Error: Target Device is None.Please use ConnectDevice to get.")
            log_print("Warning: Please use ConnectDevice to get Dev.")
            return
        try:
            self.dev.sect_erase(self.oprateAddr, self.oprateSize)
            # self.setCode(0)
            # self.appendMes("INFO: Earse Sector Success.")
        except Exception as e:
            log_print("Warning: earse sector failed.%s" % (str(e)))
            self.setCode(3)
            self.appendMes("INFO: Earse Sector Failed.")

    ############################################################################
    # step 4.3 : read Chip
    # return 3: operate failed
    ############################################################################
    def readChip(self):
        if not self.dev:
            self.setCode(5)
            self.appendMes("Error: Target Device is None.Please use ConnectDevice to get.")
            log_print("Warning: Please use ConnectDevice to get Dev.")
            return
        try:
            self.owndict['data'] = []
            self.rdbuff = []
            self.dev.chip_read(self.oprateAddr, self.oprateSize, self.rdbuff)
            for i in self.rdbuff:
                self.owndict['data'].append(i)
        except Exception as e:
            log_print("Message: read chip failed.%s" % (str(e)))
            self.setCode(3)
            self.appendMes("ERROR: Read Failed.")

    ############################################################################
    # step 4.4 : write Chip
    # return 3: operate failed
    ############################################################################
    def writeChip(self):
        if not self.dev:
            self.setCode(5)
            self.appendMes("Error: Target Device is None.Please use ConnectDevice to get.")
            log_print("Message: Please use ConnectDevice to get Dev.")
            return
        try:
            self.dev.chip_write(self.oprateAddr, self.wrbuff)
        except Exception as e:
            log_print("Message: chip write failed.%s" % (str(e)))
            self.setCode(3)
            self.appendMes("ERROR: Write Failed")

    ############################################################################
    # step 4.5 : read Mem U32
    # return 3: operate failed
    ############################################################################
    def readMem32(self, addr, count = 1):
        try:
            self.owndict['data'] = self.xlk.read_mem_U32(addr, count)
        except Exception as e:
            log_print("Message: read memU32 failed.%s" % (str(e)))
            self.setCode(3)
            self.appendMes("ERROR: readMem32 Failed")

    ############################################################################
    # step 4.6 : write Mem U32
    # return 3: operate failed
    ############################################################################
    def writeMem32(self, addr, dat):
        try:
            waddr = addr & 0xFFFFFFFC
            for wdat in dat:
                self.xlk.write_U32(waddr, wdat & 0xFFFFFFFF)
                waddr = waddr + 4
        except Exception as e:
            log_print("Message: write mem U32 failed.%s" % (str(e)))
            self.setCode(3)
            self.appendMes("ERROR: writeMem32 Failed")

    ## local function
    def _readU32Dat(self, addr, count = 1):
        readadr = addr & 0xFFFFFFFC
        readdat = []
        while count >= 1:
            dat = self.xlk.read_U32(readadr)
            count = count - 1
            readadr = readadr + 4
            readdat.append(hex(dat))
        self.appendMes("INFO: Read 0x%08X: " % addr)
        for readitem in readdat:
            self.appendMes(readitem+',')

    def _waitFlashSR(self):
        retrytimes = 5
        read_Flash_SR = self.xlk.read_U32(FLASH_SR_addr)
        while retrytimes and (read_Flash_SR & 0x01):
            read_Flash_SR = self.xlk.read_U32(FLASH_SR_addr)
            time.sleep(0.1)
            retrytimes = retrytimes - 1
        if retrytimes == 0:
            self.setCode(4)
            self.appendMes("WARNING: Wait Timeout, now FLash.SR = 0x%08x." % read_Flash_SR)
        read_Flash_CR = self.xlk.read_U32(FLASH_CR_addr)
        self.xlk.write_U32(FLASH_CR_addr, read_Flash_CR & (~(FLASH_CR_STRT | FLASH_CR_OPTER | FLASH_CR_OPTPG | FLASH_CR_MER | FLASH_CR_PER | FLASH_CR_PG)))
        self.xlk.write_U32(FLASH_SR_addr, FLASH_SR_EOP | FLASH_SR_WRPRTERR | FLASH_SR_PGERR)

    def _optEarse(self, addr):
        self.xlk.write_U32(FLASH_AR_addr, addr)
        self._en_OPTER()
        self._waitFlashSR()
        self.xlk.write_U16(FLASH_SR_addr, 1 << 5)

    def _unlockFlash(self):
        self.xlk.write_U32(FLASH_KEYR_addr, 0x45670123)
        self.xlk.write_U32(FLASH_KEYR_addr, 0xCDEF89AB)

    def _unlockOPT(self):
        self.xlk.write_U32(FLASH_OPTKEYR_addr, 0x45670123)
        self.xlk.write_U32(FLASH_OPTKEYR_addr, 0xCDEF89AB)
    
    def _lockFLash(self):
        self.xlk.write_U32(FLASH_CR_addr, FLASH_CR_LOCK)
        read_Flash_CR = self.xlk.read_U32(FLASH_CR_addr)
        self.appendMes("INFO: Flash Lock, Flash.CR = " +hex(read_Flash_CR)+'.')

    def _en_OPTPG(self):
        read_Flash_CR = self.xlk.read_U32(FLASH_CR_addr)
        self.xlk.write_U32(FLASH_CR_addr, FLASH_CR_OPTPG | read_Flash_CR)
        read_Flash_CR = self.xlk.read_U32(FLASH_CR_addr)
        self.appendMes("INFO: OPT.PG Enable, Flash.CR = " +hex(read_Flash_CR)+'.')

    def _dis_OPTPG(self):
        read_Flash_CR = self.xlk.read_U32(FLASH_CR_addr)
        self.xlk.write_U32(FLASH_CR_addr, 0xFFFFFFEF & read_Flash_CR)
        read_Flash_CR = self.xlk.read_U32(FLASH_CR_addr)
        self.appendMes("INFO: OPT.PG Disable, Flash.CR = " +hex(read_Flash_CR)+'.')

    def _en_OPTER(self):
        read_Flash_CR = self.xlk.read_U32(FLASH_CR_addr)
        self.xlk.write_U16(FLASH_CR_addr, FLASH_CR_OPTER | FLASH_CR_STRT | read_Flash_CR)
        read_Flash_CR = self.xlk.read_U32(FLASH_CR_addr)
        self.appendMes("INFO: OPT.ER Enable, Flash.CR = " +hex(read_Flash_CR)+'.')


    ############################################################################
    # step 4.7 : option Byte Earse
    # return 3: operate failed
    ############################################################################
    def optionByteEarse(self, addr):
        try:
            self._unlockFlash()
            self._optEarse(addr)
            self._waitFlashSR()
            self.owndict['data'] = self.xlk.read_mem_U32(0x1ffff800, 10)
        except Exception as e:
            log_print("Message: opt earse or read mem32 failed.%s" % (str(e)))
            self.setCode(3)
            self.appendMes("ERROR: OPT Earse Failed.")
        if Debug:
            print(self.owndict)

    ############################################################################
    # step 4.8 : option Byte Program
    # return 3: operate failed
    # return 4: Flash wait time out
    ############################################################################
    def optionByteProgram(self, addr, dat):
        try:
            readAddr = addr & 0xFFFFFFFC
            self._readU32Dat(readAddr, 10)
            self._unlockFlash()
            waddr = addr
            for wdat in dat:
                wdat = wdat & 0xFFFF
                self._unlockOPT()
                self._en_OPTPG()
                self.appendMes('INFO: write '+hex(waddr)+"="+hex(wdat)+'.')
                self.xlk.write_U16(waddr, wdat)
                self._waitFlashSR()
                waddr = waddr + 2
            self._dis_OPTPG()
            self._lockFLash()
            self.owndict['data'] = self.xlk.read_mem_U32(readAddr, 10)
            if self.getCode() == 4:
                self.appendMes("WARNING: Operate timeout.")
        except Exception as e:
            log_print("Message: Flash operate failed.%s" % (str(e)))
            self.setCode(3)
            self.appendMes("ERROR: OPT Program Failed.")

    ############################################################################
    # Special handle : hold and Earse F0010
    # return 0: ok
    # return 3: operate failed
    ############################################################################
    def reEarseF0010(self):
        # self._getLinker()
        # self.daplink = self.daplinks[self.selectIdx]
        # self.daplink.set_clock(self.speed)
        # self.daplink.open()
        self.daplink._link._protocol.set_swj_pins(0, 0, 19945)
        time.sleep(1)
        try:
            dev = device.Devices['MM32F0010'](self.xlk)
            dev.chip_erase()
        except Exception as e:
            log_print("Message: open Device or earse failed. %s" % (str(e)))
            self.setCode(3)
            self.appendMes("ERROR: Operate Failed.")

    ############################################################################
    # reset Target
    # return 0: ok
    # return 3: operate failed
    ############################################################################
    def resetTarget(self, type = 0):
        if not self.dev:
            self.setCode(5)
            self.appendMes("Error: Target Device is None.Please use ConnectDevice to get.")
            log_print("Message: Please use ConnectDevice to get Dev.")
            return
        try:
            if (type == 0): # software reset
                self.xlk.reset()
            elif (type == 1):   # hardware reset
                self.target_iDP.set_reset_pin_low()
                time.sleep(1)
                self.target_iDP.set_reset_pin_high()
            else:
                self.daplink._link._protocol.set_swj_pins(0, 0, 19945)
        except Exception as e:
            log_print("Message: target or link reset failed.%s" % (str(e)))
            self.setCode(3)
            self.appendMes("ERROR: Operate Failed.")

    ############################################################################
    # release Link
    # return 0: ok
    # return 3: operate failed
    ############################################################################
    def releaseLink(self):
        if (self.xlk):
            try:
                self.xlk.close()
            except Exception as e:
                log_print("Message: XLk close() failed.%s" % (str(e)))
        else:
            log_print("release self.xlk is None.")
        self.xlk = None
        self.dev = None
        self.target_iDP = None
        self.target_iAP = None
        self.daplink = None
        

def jsonhandle(linker, jsonText):
    # cmd handle
    cmd = jsonText['command']
    linker.uninit()
    if (cmd == 'devicelist'):
        linker.scanLinker()
    elif (cmd == 'scanTarget'):
        # select Linker-idx
        if ("index" in jsonText):
            idx = jsonText['index']
        else:
            idx = 0
        linker.setSelectIdx(idx)
        linker.scanTargetMCU()
    elif (cmd == 'connectDevice'):
        # select Linker-idx
        if ("index" in jsonText):
            idx = jsonText['index']
        else:
            idx = 0
        linker.setSelectIdx(idx)
        # swd speed
        if ("speed" in jsonText):
            if (jsonText['speed'] > 1000):
                linker.speed = jsonText['speed']
        else:
            linker.speed = 1000000
        # select MCU
        if ("mcu" in jsonText):
            mcu = jsonText['mcu']
        else:
            mcu = 'MM32F0010'
        linker.setTarget(mcu)
        linker.connectTargetMCU()
    elif (cmd == 'releaseDevice'):
        linker.releaseLink()
    elif (cmd == 'readMemory'):
        linker.oprateAddr = jsonText['address']
        linker.oprateSize = jsonText['length']
        linker.readChip()
    elif (cmd == 'writeMemory'):
        linker.oprateAddr = jsonText['address']
        linker.wrbuff     = jsonText['data']
        linker.writeChip()
    elif (cmd == 'earseChip'):
        linker.earseChip()
    elif (cmd == 'earseSector'):
        linker.oprateAddr = jsonText['address']
        linker.oprateSize = jsonText['length']
        linker.earseSector()
    elif (cmd == 'readMem32'):
        addr = jsonText['address']
        cnt = jsonText['length']
        linker.readMem32(addr, cnt)
    elif (cmd == 'writeMem32'):
        addr = jsonText['address']
        dat = jsonText['data']
        linker.writeMem32(addr, dat)
    elif (cmd == 'optWrite'):
        addr = jsonText['address']
        dat = jsonText['data']
        linker.optionByteProgram(addr, dat)
    elif (cmd == 'optEarse'):
        addr = jsonText['address']
        linker.optionByteEarse(addr)
    elif (cmd == 'reEarseF0010'):
        linker.reEarseF0010()
    elif (cmd == 'resetTarget'):
        if ("rstType" in jsonText):
            type = jsonText['rstType']
        else:
            type = 0
        linker.resetTarget(type)
    if DonePrint:
        log_print(str(linker.owndict))
    
    return linker.owndict


# test
if __name__ == "__main__":
    commandHanle()



# errcode 
# 0: success
# 1: select Linker is Out of Range
# 2: Target connect Failed
# 3: Operate Failed
# 4: MCU Flash Wait Timeout
# 5: None Target Device
# 6: Scan found none LINK