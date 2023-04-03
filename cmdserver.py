# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    :   cmdServer.py
@Time    :   2023/03/31 15:48:37
@Author  :   Chen Do
@Version :   1.0
@Desc    :   None
"""

import socket
import argparse
import configparser
import mm32program_v2
import json
import sys


def cmdHandle():
    parser = argparse.ArgumentParser(description = 'MM32-LINK Programmer Server')
    parser.add_argument('-v', '--version', action='store_true', help="show the current version")
    parser.add_argument('-R', '-run', metavar='', dest='port', help="Server port")
    args = parser.parse_args()
    if args.version:
        print("MM32-LINK Programmer Server 1.0(2023/3/31) by BD4SXU.")
    if args.port:
        print("MM32-LINK Programmer Server is run...")
        openServer(int(args.port))
    else:
        parser.print_help()



def openServer(port):
    linker = mm32program_v2.LinkerObject()

    # socket.setdefaulttimeout(5000)
    sk = socket.socket()
    # sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # set socket option value
    try:
        sk.bind(('127.0.0.1', port))
    except:
        print("Creat Server 127.0.0.1:"+str(port)+" Error.")
        sys.exit(0)

    print("Please connect: "+'127.0.0.1:'+str(port))
    sk.listen()
    conn, addr = sk.accept()

    while True:
        try:
            ret = conn.recv(1024*64)

            if ret == b'bye':
                conn.send(b'bye')
                break

            try:
                jsonText = json.loads(ret)
                info = json.dumps(mm32program_v2.jsonhandle(linker, jsonText))
            except Exception as e:
                info = ("[error] json handle failed.")
            
            conn.send(bytes(info+'\r\n', encoding='utf-8'))

        except Exception as e:
            print("[error] Server connect failed",str(e))
            conn.close()
            sys.exit()
        #     conn.send(bytes(info, encoding='utf-8'))
        # except socket.timeout as e:
        #     print("-----socket timout"),str(e)

    conn.close()
    sk.close()

if __name__ == "__main__":
    cmdHandle()


'''
{"command": "devicelist"}
{"command": "connectDevice", "index": 0, "speed": 5000000}
{"command": "readMemory","index": 0,"mcu": "MM32F0010","address": 0,"length": 10}
{"command": "writeMemory","index": 0,"speed": 5000000,"mcu": "MM32F0010","address":0,"data": [1, 2]}
{"command": "earseChip","index": 0,"mcu": "MM32F0010"}
{"command": "earseSector","index": 0,"mcu": "MM32F0010","address": 0,"length":32768}
{"command": "readMem32", "index": 0, "address": 536868864, "length": 8}
{"command": "writeMem32", "index": 0, "address": 1073881092, "data": [1164378403]}
{"command": "optEarse", "index": 0, "address": 536868864}
{"command": "optWrite", "index": 0, "address": 536868866, "data": [90]}
{"command": "reEarseF0010", "index": 0}
{"command": "quit_reset", "index": 0, "reset": 1}
'''
