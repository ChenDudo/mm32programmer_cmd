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

    def readStoreLinkers(self):
        if os.path.exists(get_path()+"\\scanlist.json"):
            with open(get_path()+"\\scanlist.json") as f:
                data = json.load(f)
                for i in range(len(data)):
                    uid = data[str(i)].split(',')[0]
                    self.deviceUIDs.append(uid)
                print("[info]: Last-Saved-Device_info read out: ", self.deviceUIDs)
                pass
        else:
            print("[error]: Nothing to found. Please use '-g' or ''--get' to get Scan list...")
    
    def _getLinker(self):
        self.daplinks = aggregator.DebugProbeAggregator.get_all_connected_probes()
        return self.daplinks

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
        self.readStoreLinkers()
        self.selectIdx = idx
        if idx >= len(self.deviceUIDs):
            print("[error]: You selected is out of device range.")
            pass
        else:
            self.selectUID = self.deviceUIDs[idx]
            print("[info]: You select idx=",idx,", device UID:", self.selectUID)
            self.getChipUUID()
        
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
            # Get Device
            print("[info]: Connect to target: "+ self.target)
            self.dev = device.Devices[self.target](self.xlk)
        except Exception as e:
            print("[error]: Connect Failed")
            self.daplink.close()
            return False
        return True

    def getChipUUID(self):
        if self._connectDAP():
            print("[info]: MCU_ID = 0x%08X" % self.MCUID)
            if (self.CPUINFO):
                print("[info]: CPU core is %s r%dp%d" % self.CPUINFO)
            if (self.MCUID == 0x0BB11477) or (self.MCUID == 0x0BC11477):
                print("[info]: DEV_ID = 0x%X" % self.M0_DEV_ID)
            else:
                print("[info]: DEV_ID = 0x%X" % self.Mx_DEV_ID)
            return True
        else:
            return False

    def writeChip(self):
        if (self._connectDAP()):
            self.dev.chip_write()

def parse_args():
    linker = LinkerObject()
    parser = argparse.ArgumentParser(description = 'MM32-LINK basic programming operations.')
    parser.add_argument('-v', '--version', action='store_true', help="Show the current version.")
    parser.add_argument('-g', '--get', action='store_true', dest='reqGet', help="Get DAP devices.")
    parser.add_argument('-s', '--select', type = int, metavar='', default = 0, help="Select device to connect.")  # choices=range(len(linker.linkers)),
    parser.add_argument('-c', '--connect', action='store_true', help="Operate: Connect.")
    parser.add_argument('-w', '--write', metavar='', dest='reqWrite', help="Operate: write chip.")
    parser.add_argument('-r', '--read', metavar='', dest='reqRead', help="Operate: read chip.")
    parser.add_argument('-e', '--earse', metavar='', dest='reqEarse', help="Operate: earse chip.")
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


if __name__ == "__main__":
    parse_args()
