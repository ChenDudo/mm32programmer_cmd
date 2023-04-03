# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    :   mm32program.py
@Time    :   2023/02/20 13:12:52
@Author  :   Chen Do
@Version :   1.0
@Desc    :   None
"""

import os
import sys
import argparse
import json
# import demjson
# import pyocd

import device
import xlink

from time import sleep
from pyocd.probe import aggregator
from pyocd.coresight import dap, ap, cortex_m


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


def get_path():
    return os.getcwd()      #.replace('\\','/')
#     if getattr(sys, 'frozen', False):
#         application_path = sys._MEIPASS
#     else:
#         application_path = os.path.dirname(os.path.abspath(__file__))  # os.path.dirname(__file__)
#     return application_path


class returnJson():
    def __init__(self):
        self.owndict = {
            'code':     0,
            'message':  '',
            'data':     []
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

    def output(self):
        return json.dumps(self.owndict)


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

    ############################################################################
    # step 1: linker handle  (devicelist)
    ############################################################################
    def outputGetLinker(self):
        self._getLinker()

        # part A: save scanlist.json
        # linkerIdx = []
        # linkerUniqueID = []
        # for i, daplink in enumerate(self.daplinks):
        #     linkerIdx.append(i)
        #     linkerUniqueID.append(daplink.unique_id+','+daplink.product_name+','+daplink.vendor_name)
        #     # linkerUniqueID.append(self.daplinks[i].unique_id+','+self.daplinks[i].product_name+','+self.daplinks[i].vendor_name)
        # dicUUID  = dict(zip(linkerIdx, linkerUniqueID))
        # with open(get_path()+"\\scanlist.json","w+",encoding='utf-8') as f:
        #     json.dump(dicUUID, f)
        
        # part B: return json string
        for i, daplink in enumerate(self.daplinks):
            linker_dict = {
            'uid' : '',
            'product' : '',
            'vendor' : ''
            }
            linker_dict['uid'] = daplink.unique_id
            linker_dict['product'] = daplink.product_name
            linker_dict['vendor'] = daplink.vendor_name
            self.owndict['data'].append(linker_dict)
        
        self.setCode(0)
        self.appendMes("[info] Get device list success.")
        print(self.owndict)

    def _getLinker(self):
        self.daplinks = aggregator.DebugProbeAggregator.get_all_connected_probes()
        return self.daplinks
    

    ############################################################################
    # step 2: connect Device (connectDevice)
    ############################################################################
    def selectLinker(self, idx = 0):
        if self.selectIdx >= len(self.daplinks):
            self.setCode(1)
            self.appendMes("[error] select Linker idx is Out-Of-Range: "+len(self.deviceUIDs)+'.')
        else:
            selectUID = self.daplinks[self.selectIdx].unique_id
            self.appendMes("[info] You select idx="+str(idx)+", device UID:"+str(selectUID)+'.')
            # connect Target Decive
            if not self._connectDAP():
                cpuinfostr = ''
                devidstr = ''
                if (self.CPUINFO):
                    cpuinfostr = self.CPUINFO[0] + ' r'+str(self.CPUINFO[1])+'p'+str(self.CPUINFO[2])
                if (self.MCUID == 0x0BB11477) or (self.MCUID == 0x0BC11477):
                    devid = self.M0_DEV_ID
                else:
                    devid = self.Mx_DEV_ID
                mcuInfo_dict = {
                    'MCU_ID' : 0,
                    'CPU_INFO' : '',
                    'DEV_ID' : 0
                }
                mcuInfo_dict['MCU_ID'] = self.MCUID
                mcuInfo_dict['CPU_INFO'] = cpuinfostr
                mcuInfo_dict['DEV_ID'] = devid
                self.owndict['data'].append(mcuInfo_dict)
                self.setCode(0)
                self.appendMes("[info] Target connnect Pass.")
            else:
                self.setCode(2)
                self.appendMes("[error] Target connect Failed.")
        print(self.owndict)

    # connect device
    def _connectDAP(self):
        try:
            # Start Connect
            self._getLinker()
            self.daplink = self.daplinks[self.selectIdx]
            self.daplink.set_clock(self.speed)
            self.daplink.open()
            # Get DP
            iDP = dap.DebugPort(self.daplink, None)
            iDP.init()
            iDP.power_up_debug()
            self.MCUID = iDP.read_id_code()
            # Get AP
            iAP = ap.AHB_AP(iDP, 0)
            iAP.init()
            self.CPUINFO = cortex_m.CortexM(None, iAP)._read_core_type()
            # Get xLINK
            self.xlk = xlink.XLink(cortex_m.CortexM(None, iAP))
            # Get DEVinfo
            self.M0_DEV_ID = self.xlk.read_mem_U32(0x40013400, 1)[0]
            self.Mx_DEV_ID = self.xlk.read_mem_U32(0x40007080, 1)[0]
            #  # Get UID
            # self.UID1 = self.xlk.read_mem_U32(0x1FFFF7E8, 1)[0]
            # self.UID2 = self.xlk.read_mem_U32(0x1FFFF7EC, 1)[0]
            # self.UID3 = self.xlk.read_mem_U32(0x1FFFF7F0, 1)[0]
        except Exception as e:
            self.daplink.close()
            return 1
        return 0

    def _quit_Reset(self, reset):
        try:
            # Start Connect
            self._getLinker()
            self.daplink = self.daplinks[self.selectIdx]
            self.daplink.open()
            # Get DP
            iDP = dap.DebugPort(self.daplink, None)
            iDP.init()
            # Get AP
            iAP = ap.AHB_AP(iDP, 0)
            iAP.init()
            self.xlk = xlink.XLink(cortex_m.CortexM(None, iAP))
            if reset:
                self.xlk.reset()
            self.xlk.close()
        except Exception as e:
            self.daplink.close()
            return 1
        return 0

    def _getChipUUID(self):
        if not self._connectDAP():
            print("[info] MCU_ID = 0x%08X" % self.MCUID)
            if (self.CPUINFO):
                print("[info] CPU core is %s r%dp%d" % self.CPUINFO)
            if (self.MCUID == 0x0BB11477) or (self.MCUID == 0x0BC11477):
                print("[info] DEV_ID = 0x%X" % self.M0_DEV_ID)
            else:
                print("[info] DEV_ID = 0x%X" % self.Mx_DEV_ID)
            return 0
        else:
            return 1


    ############################################################################
    def earseSector(self):
        if not self._connectDAP():
            try:
                try:
                    self.dev = device.Devices[self.target](self.xlk)
                except Exception as e:
                    self.appendMes("[error] Device connect Failed.")
                    self.setCode(1)
                self.dev.sect_erase(self.oprateAddr, self.oprateSize)
                self.appendMes("[info] Earse Success.")
                self.setCode(0)
            except Exception as e:
                self.appendMes("[info] Earse Failed.")
                self.setCode(1)
        else:
            self.appendMes("[error] Linker connect Failed.")
            self.setCode(1)
        print(self.owndict)

    ############################################################################
    def earseChip(self):
        errcode = 0
        if not self._connectDAP():
            try:
                try:
                    self.dev = device.Devices[self.target](self.xlk)
                except Exception as e:
                    self.appendMes("[error] Device connect Failed.")
                    self.setCode(1)
                self.dev.chip_erase()
                self.appendMes("[info] Earse Success.")
                self.setCode(0)
            except Exception as e:
                self.appendMes("[info] Earse Failed.")
                self.setCode(0)
        else:
            self.appendMes("[error] Linker connect Failed.")
            self.setCode(1)
        print(self.owndict)

    ############################################################################
    def readChip(self):
        self.setCode(0)
        if not self._connectDAP():
            try:
                try:
                    self.dev = device.Devices[self.target](self.xlk)
                except Exception as e:
                    self.appendMes("[error] Device connect Failed.")
                    self.setCode(1)
                self.dev.chip_read(self.oprateAddr, self.oprateSize, self.rdbuff)
                for i in self.rdbuff:
                    self.owndict['data'].append(i)
                self.appendMes("[info] Read Success.")
            except Exception as e:
                self.appendMes("[error] Read Failed.")
                self.setCode(1)
        print(self.owndict)

    ############################################################################
    def writeChip(self):
        self.setCode(0)
        if not self._connectDAP():
            try:
                try:
                    self.dev = device.Devices[self.target](self.xlk)
                except Exception as e:
                    self.appendMes("[error] Device connect Failed")
                    self.setCode(1)
                self.dev.chip_write(self.oprateAddr, self.wrbuff)
                self.appendMes("[info] Write Success")
            except Exception as e:
                self.appendMes("[error] Write Failed")
                self.setCode(1)
        print(self.owndict)

    ############################################################################
    def readMem32(self, addr, count = 1):
        self.setCode(0)
        if not self._connectDAP():
            try:
                readadr = addr
                self.owndict['data'] = self.xlk.read_mem_U32(readadr, count)
                self.appendMes("[info] readMem32 Success")
            except Exception as e:
                self.appendMes("[error] readMem32 Failed")
                self.setCode(1)
        print(self.owndict)

    ############################################################################
    def writeMem32(self, addr, dat):
        self.setCode(0)
        if not self._connectDAP():
            try:
                try:
                    self.dev = device.Devices[self.target](self.xlk)
                except Exception as e:
                    self.appendMes("[error] Device connect Failed")
                    self.setCode(1)
                waddr = addr & 0xFFFFFFFC
                for wdat in dat:
                    self.xlk.write_U32(waddr, wdat & 0xFFFFFFFF)
                    waddr = waddr + 4
                self.appendMes("[info] writeMem32 Success")
            except Exception as e:
                self.appendMes("[error] writeMem32 Failed")
                self.setCode(1)
        print(self.owndict)


    ############################################################################
    def _readU32Dat(self, addr, count = 1):
        readadr = addr & 0xFFFFFFFC
        readdat = []
        while count >= 1:
            dat = self.xlk.read_U32(readadr)
            count = count - 1
            readadr = readadr + 4
            readdat.append(hex(dat))
        self.appendMes("[info] Read 0x%08X: " % addr)
        for readitem in readdat:
            self.appendMes(readitem+',')
        self.appendMes('END.')

    def _waitFlashSR(self):
        retrytimes = 5
        read_Flash_SR = self.xlk.read_U32(FLASH_SR_addr)
        while retrytimes and (read_Flash_SR & 0x01):
            read_Flash_SR = self.xlk.read_U32(FLASH_SR_addr)
            sleep(0.1)
            retrytimes = retrytimes - 1
        if retrytimes == 0:
            self.setCode(1)
            self.appendMes("[warning] Wait Timeout, now FLash.SR = 0x%08x." % read_Flash_SR)
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
        self.appendMes("[info] Flash Lock, Flash.CR = " +hex(read_Flash_CR)+'.')

    def _en_OPTPG(self):
        read_Flash_CR = self.xlk.read_U32(FLASH_CR_addr)
        self.xlk.write_U32(FLASH_CR_addr, FLASH_CR_OPTPG | read_Flash_CR)
        read_Flash_CR = self.xlk.read_U32(FLASH_CR_addr)
        self.appendMes("[info] OPT.PG Enable, Flash.CR = " +hex(read_Flash_CR)+'.')

    def _dis_OPTPG(self):
        read_Flash_CR = self.xlk.read_U32(FLASH_CR_addr)
        self.xlk.write_U32(FLASH_CR_addr, 0xFFFFFFEF & read_Flash_CR)
        read_Flash_CR = self.xlk.read_U32(FLASH_CR_addr)
        self.appendMes("[info] OPT.PG Disable, Flash.CR = " +hex(read_Flash_CR)+'.')

    def _en_OPTER(self):
        read_Flash_CR = self.xlk.read_U32(FLASH_CR_addr)
        self.xlk.write_U16(FLASH_CR_addr, FLASH_CR_OPTER | FLASH_CR_STRT | read_Flash_CR)
        read_Flash_CR = self.xlk.read_U32(FLASH_CR_addr)
        self.appendMes("[info] OPT.ER Enable, Flash.CR = " +hex(read_Flash_CR)+'.')


    ############################################################################
    def optionByteEarse(self, addr):
        self.setCode(0)
        if not self._connectDAP():
            try:
                self._unlockFlash()
                self._optEarse(addr)
                self.appendMes("[info] OPT Earse Success.")
                self._waitFlashSR()
                self.owndict['data'] = self.xlk.read_mem_U32(0x1ffff800, 10)
                # self._readU32Dat(addr, cnt)
                self._readU32Dat(0x1ffff800, 10)
            except Exception as e:
                self.appendMes("[error] OPT Earse Failed.")
                self.setCode(1)
        print(self.owndict)


    ############################################################################
    def optionByteProgram(self, addr, dat):
        self.setCode(0)
        if not self._connectDAP():
            try:
                readAddr = addr & 0xFFFFFFFC
                self._readU32Dat(readAddr, 10)
                self._unlockFlash()

                waddr = addr
                for wdat in dat:
                    wdat = wdat & 0xFFFF
                    self._unlockOPT()
                    self._en_OPTPG()
                    self.appendMes('[info]: write '+hex(waddr)+"="+hex(wdat)+'.')
                    self.xlk.write_U16(waddr, wdat)
                    self._waitFlashSR()
                    waddr = waddr + 2

                self._dis_OPTPG()
                self._lockFLash()

                self.owndict['data'] = self.xlk.read_mem_U32(readAddr, 10)
                if self.getCode() == 0:
                    self.appendMes("[info] OPT Program Success.")
                else:
                    self.appendMes("[error] OPT Program Something error.")
            except Exception as e:
                self.appendMes("[error] OPT Program Failed.")
                self.setCode(1)
        self.xlk.reset()
        print(self.owndict)

    def reEarseF0010(self):
        self._getLinker()
        self.daplink = self.daplinks[self.selectIdx]
        self.daplink.set_clock(self.speed)
        self.daplink.open()
        self.daplink._link._protocol.set_swj_pins(0, 0, 19945)
        sleep(1)
        self.earseChip()


def jsonhandle(linker, jsonText):

    # swd speed
    if ("speed" in jsonText):
        if (jsonText['speed'] > 1000):
            linker.speed = jsonText['speed']
    else:
        linker.speed = 1000000
        
    # select Linker-idx
    if ("index" in jsonText):
        idx = jsonText['index']
    else:
        idx = 0
    linker.setSelectIdx(idx)

    # select MCU
    if ("mcu" in jsonText):
        mcu = jsonText['mcu']
    else:
        mcu = 'mm32f0010'
    linker.setTarget(mcu)

    # cmd handle
    cmd = jsonText['command']
    linker.uninit()
    if (cmd == 'devicelist'):
        linker.outputGetLinker()
    elif (cmd == 'connectDevice'):
        linker.selectLinker()
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
    elif (cmd == 'quit_reset'):
        if ("reset" in jsonText):
            if (jsonText['reset'] == 0):
                reset = 0
            else:
                reset = 1
        else:
            reset = 1
        linker._quit_Reset(reset)
    return linker.owndict


# test
if __name__ == "__main__":
    commandHanle()



# errcode 
# 0: success
# 1: select Linker is Out of Range
# 2: Target connect Failed