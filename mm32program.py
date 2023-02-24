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
        self.owndict = {
            'code':     0,
            'message':  '',
            'data':     []
        }

    def clearMessage(self):
        self.owndict['message'] = ''

    def setCode(self, num):
        self.owndict['code'] = num

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
        self.appendMes("[info] Get device list success")
        print(self.owndict)

    ############################################################################
    def selectLinker(self, idx = 0):
        if (self._readStoreLinkers()):
            # self.outputGetLinker()
            self.setCode(1)
            self.appendMes('[warnning] not found lastsaved scanlist.json. Please try again or ignore')
        else:
            self.selectIdx = idx
            if idx >= len(self.deviceUIDs):
                self.setCode(1)
                self.appendMes("[error] Selected out of Range(devicelist).")
            else:
                self.selectUID = self.deviceUIDs[idx]
                self.appendMes("[info] You select idx="+str(idx)+", device UID:"+str(self.selectUID)+'\n')
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
                    }
                    mcuInfo_dict['MCU_ID'] = self.MCUID
                    mcuInfo_dict['CPU_INFO'] = cpuinfostr
                    mcuInfo_dict['DEV_ID'] = devid
                    self.owndict['data'].append(mcuInfo_dict)
                    self.setCode(0)
                    self.appendMes("[info] Target connnect Pass\n")
                else:
                    self.setCode(1)
                    self.appendMes("[error] Target connect Failed\n")
        print(self.owndict)

    ############################################################################
    def earseSector(self):
        if not self._connectDAP():
            try:
                try:
                    self.dev = device.Devices[self.target](self.xlk)
                except Exception as e:
                    self.appendMes("[error] Device connect Failed\n")
                    self.setCode(1)
                self.dev.sect_erase(self.oprateAddr, self.oprateSize)
                self.appendMes("[info] Earse Success\n")
                self.setCode(0)
            except Exception as e:
                self.appendMes("[info] Earse Failed\n")
                self.setCode(1)
            self.xlk.reset()
            self.xlk.close()
        else:
            self.appendMes("[error] Linker connect Failed\n")
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
                    self.appendMes("[error] Device connect Failed\n")
                    self.setCode(1)
                self.dev.chip_erase()
                self.appendMes("[info] Earse Success\n")
                self.setCode(0)
            except Exception as e:
                self.appendMes("[info] Earse Failed\n")
                self.setCode(0)
            self.xlk.reset()
            self.xlk.close()
        else:
            self.appendMes("[error] Linker connect Failed\n")
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
                    self.appendMes("[error] Device connect Failed")
                    self.setCode(1)
                self.dev.chip_read(self.oprateAddr, self.oprateSize, self.rdbuff)
                # print(self.rdbuff)
                for i in self.rdbuff:
                    self.owndict['data'].append(i)
                self.appendMes("[info] Read Success")
            except Exception as e:
                self.appendMes("[error] Read Failed")
                self.setCode(1)
        self.xlk.reset()
        self.xlk.close()
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
        self.xlk.close()
        print(self.owndict)

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

def commandHanle():
    parser = argparse.ArgumentParser(description = 'MM32-LINK Basic Programming Operations')
    parser.add_argument('-v', '--version', action='store_true', help="show the current version")
    parser.add_argument('-p', '-path', metavar='', dest='path', help="json path")
    parser.add_argument('-j', '-json', metavar='', dest='json', help="json (string)")
    parser.add_argument('-E', '--earse', action='store_true', help="!Test earse MCU [Unstable]")
    parser.add_argument('-CH', '--connectHalt', action='store_true', help="!Test connect & halt MCU [Unstable]")
    args = parser.parse_args()
    if args.version:
        print("MM32Program_pyCMD 1.0(2023/2/24) by BD4XSU.")
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
    if (cmd == 'earseSector'):
        linker.setSelectIdx(jsonText['index'])
        linker.setTarget(jsonText['mcu'])
        linker.oprateAddr = jsonText['address']
        linker.oprateSize = jsonText['length']
        linker.earseSector()


if __name__ == "__main__":
    # parse_args()
    commandHanle()
