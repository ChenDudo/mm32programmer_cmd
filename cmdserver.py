# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    :   cmdServer.py
@Time    :   2023/03/31 15:48:37
@Author  :   Chen Do
@Version :   1.0
@Desc    :   None
"""

import os
import sys
import argparse
import socket
import json
import time

import mm32program_v2


# def ifProcessRunning(process_name):
#     try:
#         pl = psutil.pids()
#         result = 0  #"PROCESS_IS_NOT_RUNNING"
#         nowPid = os.getpid()
#         for pid in pl:
#             # print(psutil.Process(pid).name())
#             if (psutil.Process(pid).name() == process_name):
#                 print("pid = %d, nowPid = %d, name = %s" %(pid, nowPid, psutil.Process(pid).name()))
#                 if isinstance(pid, int):
#                     if pid == nowPid:
#                         result = 0
#                     else:
#                         result = 1  #"PROCESS_IS_RUNNING"
#         print("result = "+str(result))
#         return result
#     except Exception as e:
#         print("ERROR: ",str(e))
#         return 2        #"Get PROCESS error"
    

# def check_port(ip, port):
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     try:
#         s.connect((ip, port))
#         s.shutdown(2)
#         return True
#     except socket.error as e:
#         return False


def access(port):
    # privileged port # out of range
    if port < 1024 or 65535 < port:
        if port != 80:
            return False
    # if 'win32' == sys.platform:
    #     cmd = 'netstat -aon|findstr ":%s "' % port
    # elif 'linux' == sys.platform:
    #     cmd = 'netstat -aon|grep ":%s "' % port
    # else:
    #     print('Unsupported system type %s' % sys.platform)
    #     return False
    cmd = 'netstat -aon|findstr ":%s "' % port
    with os.popen(cmd, 'r') as f:
        if '' != f.read():
            return True
        else:
            return False

def sformatTime():
    return time.strftime("[%Y-%m-%d %H:%M:%S]", (time.localtime(time.time())))

def slog_print(text):
    print("%s %s" % (sformatTime(), text))


def cmdHandle():
    parser = argparse.ArgumentParser(description = 'MM32-LINK Programmer Server')
    parser.add_argument('-v', '--version', action='store_true', help="show the current version")
    parser.add_argument('-R', '-run', metavar='', dest='port', help="Server port")
    args = parser.parse_args()
    if args.version:
        print("MM32-LINK Programmer Server 1.0(2023/3/31) by BD4SXU.")
    if args.port:
        openServer(int(args.port))
    else:
        parser.print_help()

def is_json(raw_msg):
    try:
      	json.loads(raw_msg)
    except ValueError:
        return False
    return True

def openServer(port):
    ip = '127.0.0.1'
    linker = mm32program_v2.LinkerObject()
    if (access(port)):
        slog_print('ERROR: Port %s is occupied.' % port)
        return

    # socket.setdefaulttimeout(5000)
    # sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        #create an AF_INET, STREAM socket (TCP)
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        slog_print("ERROR: Failed to create socket. Error code: %s, Error message: %s." % (str(msg[0]), msg[1]))
        sys.exit()

    # sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # set socket option value
    try:
        sk.bind((ip, port))
    except Exception as e:
        slog_print("ERROR: Server creat bind %s:%d Error, %s." % (ip, port, str(e)))
        return

    slog_print("INFO: Socket Created. Please Access: %s:%d ...." % (ip, port))

    while True:
        sk.listen()
        conn, addr = sk.accept()
        slog_print("INFO: New Client TCP Connection Success.")
        while True:
            try:
                ret = conn.recv(1024*256)
                if ret == b'bye\r\n' or ret == b'bye':
                    conn.send(b'bye')
                    slog_print("INFO: Client request Closed.")
                    return
                if is_json(ret) == True:
                    try:
                        jsonText = json.loads(ret)
                        info = json.dumps(mm32program_v2.jsonhandle(linker, jsonText))
                    except Exception as e:
                        info = ("ERROR: Input is not json-format.")
                else:
                    info = ("INFO: Please input Json Format String")
                conn.send(bytes(info+'\r\n', encoding='utf-8'))
            except Exception as e:
                slog_print("ERROR: Client TCP Connection Failed. Message:%s" % (str(e)))
                break

    conn.close()
    sk.close()

if __name__ == "__main__":
    cmdHandle()


'''
{"command": "devicelist"}
{"command": "scanTarget", "index": 0, "speed": 5000000}
{"command": "connectDevice", "index": 0, "speed": 5000000, "mcu": "MM32F0010"}
{"command": "readMemory", "index": 0, "speed": 5000000, "mcu": "MM32F0010", "address": 0, "length": 10}
{"command": "writeMemory", "index": 0, "speed": 5000000, "mcu": "MM32F0010", "address":0, "data": [1, 2]}
{"command": "earseChip", "index": 0, "speed": 5000000, "mcu": "MM32F0010"}
{"command": "earseSector", "index": 0, "speed": 5000000, "mcu": "MM32F0010", "address": 0,"length":32768}
{"command": "readMem32", "index": 0, "speed": 5000000, "mcu": "MM32F0010", "address": 536868864, "length": 8}
{"command": "writeMem32", "index": 0, "speed": 5000000, "mcu": "MM32F0010", "address": 1073881092, "data": [1164378403]}
{"command": "optEarse","index": 0, "speed": 5000000, "mcu": "MM32F0010", "address": 536868864}
{"command": "optWrite", "index": 0, "speed": 5000000, "mcu": "MM32F0010", "address": 536868866, "data": [90]}
{"command": "reEarseF0010", "index": 0}
{"command": "resetTarget", "index": 0, "rstType": 0}
{"command": "releaseDevice", "index": 0}
'''