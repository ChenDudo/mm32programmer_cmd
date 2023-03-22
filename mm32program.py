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

    def clearMessage(self):
        self.owndict['message'] = ''

    def setCode(self, num):
        self.owndict['code'] = num
    
    def getCode(self):
        return self.owndict['code']

    def appendMes(self, str):
        self.owndict['message'] = self.owndict['message'] + (str)

    def output(self):
        return json.dumps(self.owndict)

class LinkerObject(returnJson):
    # reCode = returnJson()

    def __init__(self):
        super(LinkerObject, self).__init__()
        self.selectUID = ''
        self.selectIdx = 0
        self.deviceUIDs = []
        self.daplinks = []
        self.daplink = None
        self.xlk = None
        self.dev = None
        self.target = 'MM32F0010'
        self.wrbuff = []
        self.rdbuff = []
        self.oprateAddr = 0
        self.oprateSize = 0
        self.speed = 1000000

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
    
    def _readStoreLinkers(self):
        if os.path.exists(get_path()+"\\scanlist.json"):
            with open(get_path()+"\\scanlist.json") as f:
                data = json.load(f)
                for i in range(len(data)):
                    uid = data[str(i)].split(',')[0]
                    self.deviceUIDs.append(uid)
                # print("[info]: Last-Saved-Device_info read out: ", self.deviceUIDs)
        else:
            # print("[error]: Nothing to found. Please use '-g' or ''--get' to get Scan list...")
            return 1
        return 0
    
    def _getLinker(self):
        self.daplinks = aggregator.DebugProbeAggregator.get_all_connected_probes()
        return self.daplinks

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
    ## deviceList
    ## return :
    #     {
    #     "code": 0,
    #     "message": "",
    #     "data": [
    #         {
    #             "uid": "0880ff03f13004c75fd",
    #             "target": "MM32_V1 CMSIS-DAP",
    #             "company":"MindMotion",
    #         },
    #     ]
    # }
    ############################################################################
    def outputGetLinker(self):
        self._getLinker()
        linker_dict = {
            'uid' : '',
            'product' : '',
            'vendor' : ''
        }
        linkerIdx = []
        linkerUniqueID = []
        for i, daplink in enumerate(self.daplinks):
            linkerIdx.append(i)
            linkerUniqueID.append(daplink.unique_id+','+daplink.product_name+','+daplink.vendor_name)
        dicUUID  = dict(zip(linkerIdx, linkerUniqueID))
        for i, daplink in enumerate(self.daplinks):
            linker_dict['uid'] = daplink.unique_id
            linker_dict['product'] = daplink.product_name
            linker_dict['vendor'] = daplink.vendor_name
            self.owndict['data'].append(linker_dict)
        # print("Scan info: ", dicUUID)
        with open(get_path()+"\\scanlist.json","w+",encoding='utf-8') as f:
            json.dump(dicUUID, f)
            # print("Save scanlist finished...\nSavePath: "+get_path()+"\\scanlist.json")
        self.setCode(0)
        self.appendMes("[info] Get device list success.")
        print(self.owndict)

    ############################################################################
    def selectLinker(self, idx = 0):
        if (self._readStoreLinkers()):
            # self.outputGetLinker()
            self.setCode(1)
            self.appendMes('[warnning] not found lastsaved scanlist.json. Please try again or ignore.')
        else:
            self.selectIdx = idx
            if idx >= len(self.deviceUIDs):
                self.setCode(1)
                self.appendMes("[error] Selected out of Range(devicelist).")
            else:
                self.selectUID = self.deviceUIDs[idx]
                self.appendMes("[info] You select idx="+str(idx)+", device UID:"+str(self.selectUID)+'.')
                # self._getChipUUID()
                if not self._connectDAP():
                    cpuinfostr = ''
                    devidstr = ''
                    if (self.CPUINFO):
                        # print("[info]: CPU core is %s r%dp%d" % self.CPUINFO)
                        cpuinfostr = self.CPUINFO[0] + ' r'+str(self.CPUINFO[1])+'p'+str(self.CPUINFO[2])
                    if (self.MCUID == 0x0BB11477) or (self.MCUID == 0x0BC11477):
                        # print("[info]: DEV_ID = 0x%X" % self.M0_DEV_ID)
                        devid = self.M0_DEV_ID
                    else:
                        # print("[info]: DEV_ID = 0x%X" % self.Mx_DEV_ID)
                        devid = self.Mx_DEV_ID
                    
                    mcuInfo_dict = {
                        'MCU_ID' : 0,
                        'CPU_INFO' : '',
                        'DEV_ID' : 0
                        # 'UID1': 0,
                        # 'UID2': 0,
                        # 'UID3': 0
                    }
                    mcuInfo_dict['MCU_ID'] = self.MCUID
                    mcuInfo_dict['CPU_INFO'] = cpuinfostr
                    mcuInfo_dict['DEV_ID'] = devid
                    # mcuInfo_dict['UID1'] = self.UID1
                    # mcuInfo_dict['UID2'] = self.UID2
                    # mcuInfo_dict['UID3'] = self.UID3
                    
                    self.owndict['data'].append(mcuInfo_dict)
                    self.setCode(0)
                    self.appendMes("[info] Target connnect Pass.")
                else:
                    self.setCode(1)
                    self.appendMes("[error] Target connect Failed.")
        print(self.owndict)

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
                # self.xlk.reset()
                # self.xlk.close()
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
            # self.xlk.reset()
            # self.xlk.close()
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
                # print(self.rdbuff)
                for i in self.rdbuff:
                    self.owndict['data'].append(i)
                self.appendMes("[info] Read Success.")
            except Exception as e:
                self.appendMes("[error] Read Failed.")
                self.setCode(1)
            # self.xlk.reset()
            # self.xlk.close()
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
        self.xlk.reset()
            # self.xlk.close()
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
        # self.xlk.reset()
        # self.xlk.close()
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
            # self.xlk.reset()
            # self.xlk.close()
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
        # readdat = self.xlk.read_mem_U32(readadr, count)
        # print("0x%08X read total: " % addr, readdat)
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
        # read_Flash_CR = self.xlk.read_U32(FLASH_CR_addr)
        # read_Flash_SR = self.xlk.read_U32(FLASH_SR_addr)
        # print("FLASH_CR = "+hex(read_Flash_CR))
        # print("FLASH_SR = "+hex(read_Flash_SR))

    def _optEarse(self, addr):
        self.xlk.write_U32(FLASH_AR_addr, addr)
        self._en_OPTER()
        self._waitFlashSR()
        self.xlk.write_U16(FLASH_SR_addr, 1 << 5)

    def _unlockFlash(self):
        # read_Flash_CR = self.xlk.read_U32(FLASH_CR_addr)
        # if read_Flash_CR & FLASH_CR_LOCK:
        #     print("Flash is Locked! Flash_CR = 0x%08x" % read_Flash_CR)
        #     self.xlk.write_U32(FLASH_KEYR_addr, 0x45670123)
        #     self.xlk.write_U32(FLASH_KEYR_addr, 0xCDEF89AB)
        #     read_Flash_CR = self.xlk.read_U32(FLASH_CR_addr)
        #     print("...Flash Unlock, Flash_CR = 0x%08x" % read_Flash_CR)
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
        # self.xlk.write_U32(FLASH_CR_addr, ~FLASH_CR_OPTPG | read_Flash_CR)
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
        # self.xlk.reset()
        # self.xlk.close()
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
                # self._readU32Dat(readAddr, 10)
                if self.getCode() == 0:
                    self.appendMes("[info] OPT Program Success.")
                else:
                    self.appendMes("[error] OPT Program Something error.")
            except Exception as e:
                self.appendMes("[error] OPT Program Failed.")
                self.setCode(1)
        self.xlk.reset()
        self.xlk.close()
        print(self.owndict)
        
'''
# def parse_args():
#     linker = LinkerObject()
#     parser = argparse.ArgumentParser(description = 'MM32-LINK Basic Programming Operations')
#     parser.add_argument('-v', '--version', action='store_true', help="Show the current version.")
#     parser.add_argument('-g', '--get', action='store_true', dest='reqGet', help="Get DAP devices.")
#     parser.add_argument('-s', '--select', type = int, metavar='', default = 0, help="Select device to connect.")  # choices=range(len(linker.linkers)),
#     parser.add_argument('-c', '--connect', action='store_true', help="Operate: Connect.")
#     parser.add_argument('-w', '--write', action='store_true', help="Operate: write chip.")
#     parser.add_argument('-r', '--read', action='store_true', help="Operate: read chip.")
#     parser.add_argument('-e', '--earse', action='store_true', help="Operate: earse chip.")
#     parser.add_argument('-f', '--file', metavar='', dest='reqFile', type=argparse.FileType('r'), help="Indicate File path")
#     # return parser.parse_args()
#     # print(parser.print_help())
#     args = parser.parse_args()
#     if args.version:
#         print("MM32Program_pyCMD 0.9(2023/2/24) by BD4XSU.")
#         sys.exit(0)
#     if args.reqGet:
#         linker.outputGetLinker()
#         sys.exit(1)
#     if args.connect:
#         linker.selectLinker(int(args.select))
#     if args.earse:
#         linker.earseChip()
#     if args.read:
#         linker.readChip()
#     if args.write:
#         linker.writeChip()
'''

def commandHanle():
    parser = argparse.ArgumentParser(description = 'MM32-LINK Basic Programming Operations')
    parser.add_argument('-v', '--version', action='store_true', help="show the current version")
    parser.add_argument('-p', '-path', metavar='', dest='path', help="json path")
    parser.add_argument('-j', '-json', metavar='', dest='json', help="json (string)")
    parser.add_argument('-E', '--earse', action='store_true', help="!Test earse MCU [Unstable]")
    parser.add_argument('-CH', '--connectHalt', action='store_true', help="!Test connect & halt MCU [Unstable]")
    args = parser.parse_args()
    if args.version:
        print("MM32Program_pyCMD 1.0(2023/2/24) by BD4SXU.")
        sys.exit(0)
    if args.earse:
        linker = LinkerObject()
        linker.earseChip()
    if args.connectHalt:
        linker = LinkerObject()
        linker._connectDAP()
    if args.path:
        try:
            with open(args.path, 'r+') as f:
                jsonText = json.load(f)
                jsonhandle(jsonText)
        except Exception as e:
            print("[error] Operate failed.")
        # sys.exit(1)
    if args.json:
        try:
            rText = args.json.replace("\'", "\"")
            jsonText = json.loads(rText)
            jsonhandle(jsonText)
        except Exception as e:
            print("[error] Operate failed.")
    # print(parser.print_help())

def jsonhandle(jsonText):
    linker = LinkerObject()
    
    cmd = jsonText['command']
    # get speed
    if ("speed" in jsonText):
        if (jsonText['speed'] > 1000):
            linker.speed = jsonText['speed']
    else:
        linker.speed = 1000000
    if (cmd == 'devicelist'):
        linker.outputGetLinker()
    elif (cmd == 'connectDevice'):
        idx = (jsonText["index"])
        linker.selectLinker(idx)
    elif (cmd == 'readMemory'):
        linker.setSelectIdx(jsonText['index'])
        linker.setTarget(jsonText['mcu'])
        linker.oprateAddr = jsonText['address']
        linker.oprateSize = jsonText['length']
        linker.readChip()
    elif (cmd == 'writeMemory'):
        linker.setSelectIdx(jsonText['index'])
        linker.setTarget(jsonText['mcu'])
        linker.oprateAddr = jsonText['address']
        linker.wrbuff = jsonText['data']
        linker.writeChip()
    elif (cmd == 'earseChip'):
        linker.setSelectIdx(jsonText['index'])
        linker.setTarget(jsonText['mcu'])
        linker.earseChip()
    elif (cmd == 'earseSector'):
        linker.setSelectIdx(jsonText['index'])
        linker.setTarget(jsonText['mcu'])
        linker.oprateAddr = jsonText['address']
        linker.oprateSize = jsonText['length']
        linker.earseSector()
    elif (cmd == 'readMem32'):
        linker.setSelectIdx(jsonText['index'])
        addr = jsonText['address']
        cnt = jsonText['length']
        linker.readMem32(addr, cnt)
    elif (cmd == 'writeMem32'):
        linker.setSelectIdx(jsonText['index'])
        addr = jsonText['address']
        dat = jsonText['data']
        linker.writeMem32(addr, dat)
    elif (cmd == 'optWrite'):
        linker.setSelectIdx(jsonText['index'])
        addr = jsonText['address']
        dat = jsonText['data']
        linker.optionByteProgram(addr, dat)
    elif (cmd == 'optEarse'):
        linker.setSelectIdx(jsonText['index'])
        addr = jsonText['address']
        linker.optionByteEarse(addr)
    # self.xlk.reset()
    # self.xlk.close()


if __name__ == "__main__":
    # parse_args()
    commandHanle()
