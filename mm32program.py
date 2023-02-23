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
import demjson
# import pyocd

import device
import xlink


from pyocd.probe import aggregator
from pyocd.coresight import dap, ap, cortex_m

def get_path():
    return os.getcwd()      #.replace('\\','/')
#     if getattr(sys, 'frozen', False):
#         application_path = sys._MEIPASS
#     else:
#         application_path = os.path.dirname(os.path.abspath(__file__))  # os.path.dirname(__file__)
#     return application_path
class returnJson():
    def __init__(self):
        self.code = 0
        self.message = '--'
        self.clearMessage()

    def clearMessage(self):
        self.message = ''

    def appendMessage(self, str):
        self.message = self.message + (str)

    def setCode(self, num):
        self.code = num

    def output(self):
        demjson.encode(self, obj, nest_level = 0)

class LinkerObject:
    def __init__(self):
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
        self.errCode = 0
        self.message = ''

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
                # self.message = self.message + ("[info]: Last-Saved-Device_info read out: ", self.deviceUIDs)
        else:
            # self.message = self.message + ("[error]: Nothing to found. Please use '-g' or ''--get' to get Scan list...")
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
        except Exception as e:
            self.message = "[error]: Connect Failed\n"
            self.daplink.close()
            return 1
        return 0

    def _getChipUUID(self):
        if not self._connectDAP():
            print("[info]: MCU_ID = 0x%08X" % self.MCUID)
            if (self.CPUINFO):
                print("[info]: CPU core is %s r%dp%d" % self.CPUINFO)
            if (self.MCUID == 0x0BB11477) or (self.MCUID == 0x0BC11477):
                print("[info]: DEV_ID = 0x%X" % self.M0_DEV_ID)
            else:
                print("[info]: DEV_ID = 0x%X" % self.Mx_DEV_ID)
            return 0
        else:
            return 1

    def outputGetLinker(self):
        self._getLinker()
        linkerIdx = []
        linkerUniqueID = []
        linkerProductName = []
        linkerVendorName = []
        for i, daplink in enumerate(self.daplinks):
            linkerIdx.append(i)
            linkerUniqueID.append(daplink.unique_id+','+daplink.product_name+','+daplink.vendor_name)
        dicUUID  = dict(zip(linkerIdx, linkerUniqueID))
        print("Scan info: ", dicUUID)
        with open(get_path()+"\\scanlist.json","w+",encoding='utf-8') as f:
            json.dump(dicUUID, f)
            print("Save scanlist finished...\nSavePath: "+get_path()+"\\scanlist.json")
        return (dicUUID)
        
    def selectLinker(self, idx = 0):
        errcode = 0
        if (self._readStoreLinkers()):
            # self.outputGetLinker()
            errcode = 2
        else:
            self.selectIdx = idx
            if idx >= len(self.deviceUIDs):
                print("[error]: You selected is out of device range.")
                errcode = 1
            else:
                self.selectUID = self.deviceUIDs[idx]
                print("[info]: You select idx=",idx,", device UID:", self.selectUID)
                self._getChipUUID()
        return errcode

    def earseSector(self):
        errcode = 0
        if not self._connectDAP():
            try:
                try:
                    self.dev = device.Devices[self.target](self.xlk)
                except Exception as e:
                    self.message = self.message + ("[error]Device connect Failed")
                    errcode = 1
                self.dev.sect_erase(self.oprateAddr, self.oprateSize)
                self.message = self.message + ("Earse Success")
            except Exception as e:
                self.message = self.message + ("Earse Failed")
                errcode = 1
        self.xlk.reset()
        self.xlk.close()
        self.errCode = errcode
        return errcode

    def earseChip(self):
        errcode = 0
        if not self._connectDAP():
            try:
                try:
                    self.dev = device.Devices[self.target](self.xlk)
                except Exception as e:
                    print("[error]Device connect Failed")
                    errcode = 1
                self.dev.chip_erase()
                print("Earse Success")
            except Exception as e:
                print("Earse Failed")
                errcode = 1
        self.xlk.reset()
        self.xlk.close()
        self.errCode = errcode
        return errcode

    def readChip(self):
        errcode = 0
        if not self._connectDAP():
            try:
                try:
                    self.dev = device.Devices[self.target](self.xlk)
                except Exception as e:
                    self.message = self.message + ("[error]Device connect Failed")
                    errcode = 1
                self.dev.chip_read(self.oprateAddr, self.oprateSize, self.rdbuff)
                print(self.rdbuff)
                self.message = self.message + ("Read Success")
            except Exception as e:
                self.message = self.message + ("Read Failed")
                errcode = 1
        self.xlk.reset()
        self.xlk.close()
        self.errCode = errcode
        return errcode

    def writeChip(self):
        errcode = 0
        if not self._connectDAP():
            try:
                try:
                    self.dev = device.Devices[self.target](self.xlk)
                except Exception as e:
                    self.message = self.message + ("[error]Device connect Failed")
                    errcode = 1
                self.dev.chip_write(self.oprateAddr, self.wrbuff)
                self.message = self.message + ("Write Success")
            except Exception as e:
                self.message = self.message + ("Write Failed")
                errcode = 1
        self.xlk.reset()
        self.xlk.close()
        self.errCode = errcode
        return errcode


def parse_args():
    linker = LinkerObject()
    parser = argparse.ArgumentParser(description = 'MM32-LINK basic programming operations.')
    parser.add_argument('-v', '--version', action='store_true', help="Show the current version.")
    parser.add_argument('-g', '--get', action='store_true', dest='reqGet', help="Get DAP devices.")
    parser.add_argument('-s', '--select', type = int, metavar='', default = 0, help="Select device to connect.")  # choices=range(len(linker.linkers)),
    parser.add_argument('-c', '--connect', action='store_true', help="Operate: Connect.")
    parser.add_argument('-w', '--write', action='store_true', help="Operate: write chip.")
    parser.add_argument('-r', '--read', action='store_true', help="Operate: read chip.")
    parser.add_argument('-e', '--earse', action='store_true', help="Operate: earse chip.")
    parser.add_argument('-f', '--file', metavar='', dest='reqFile', type=argparse.FileType('r'), help="Indicate File path")
    # return parser.parse_args()
    # print(parser.print_help())
    args = parser.parse_args()
    if args.version:
        print("mm32program_pycmd 0.1 by NJ.")
        sys.exit(0)
    if args.reqGet:
        linker.outputGetLinker()
        sys.exit(1)
    if args.connect:
        linker.selectLinker(int(args.select))
    if args.earse:
        linker.earseChip()
    if args.read:
        linker.readChip()
    if args.write:
        linker.writeChip()

def commandHanle():
    parser = argparse.ArgumentParser(description = 'MM32-LINK basic programming operations.')
    parser.add_argument('-v', '--version', action='store_true', help="show the current version.")
    parser.add_argument('-p', '-path', metavar='', dest='path', help="json path")
    parser.add_argument('-j', '-json', metavar='', dest='json', help="json (string)")
    parser.add_argument('-E', '--earse', action='store_true', help="! Test earse MCU [Unstable]")
    parser.add_argument('-CH', '--connectHalt', action='store_true', help="! Test connect & halt MCU [Unstable]")
    args = parser.parse_args()
    if args.version:
        print("mm32program_pycmd 0.2 by NJ.")
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
            print("[error] Operate failed")
        # sys.exit(1)
    if args.json:
        try:
            rText = args.json.replace("\'", "\"")
            jsonText = json.loads(rText)
            jsonhandle(jsonText)
        except Exception as e:
            print("[error] Operate failed")
    # print(parser.print_help())

def jsonhandle(jsonText):
    linker = LinkerObject()
    reCode  = returnJson()
    cmd = jsonText['command']
    if (cmd == 'devicelist'):
        linker.outputGetLinker()
    if (cmd == 'connectDevice'):
        idx = (jsonText["index"])
        linker.selectLinker(idx)
    if (cmd == 'readMemory'):
        linker.setSelectIdx(jsonText['index'])
        linker.setTarget(jsonText['mcu'])
        linker.oprateAddr = jsonText['address']
        linker.oprateSize = jsonText['length']
        linker.readChip()
    if (cmd == 'writeMemory'):
        linker.setSelectIdx(jsonText['index'])
        linker.setTarget(jsonText['mcu'])
        linker.oprateAddr = jsonText['address']
        linker.wrbuff = jsonText['data']
        linker.writeChip()
    if (cmd == 'earseChip'):
        linker.setSelectIdx(jsonText['index'])
        linker.setTarget(jsonText['mcu'])
        linker.earseChip()
    
    reCode.setCode(linker.errCode)
    reCode.appendMessage(linker.message)
    print(reCode.message)
    # print(reCode.rxbuff)
    # return reCode.output()
    


if __name__ == "__main__":
    # parse_args()
    commandHanle()
