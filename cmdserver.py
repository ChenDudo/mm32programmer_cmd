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
import mm32program
import json

def cmdHandle():
    parser = argparse.ArgumentParser(description = 'MM32-LINK Programmer Server')
    parser.add_argument('-v', '--version', action='store_true', help="show the current version")
    parser.add_argument('-R', '-run', metavar='', dest='port', help="Server port") #required=True
    args = parser.parse_args()
    if args.version:
        print("MM32-LINK Programmer Server 1.0(2023/3/31) by BD4SXU.")
    if args.port:
        # print(int(args.port))
        print("MM32-LINK Programmer Server is run...")
        openServer(int(args.port))
    # parser.print_help()

def openServer(port):
    sk = socket.socket()    # 创建服务器端套接字
    # sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 设置给定套接字选项的值。
    sk.bind(('127.0.0.1', port))    # 把地址绑定到套接字
    print("[INFO] Please connect: "+'127.0.0.1:'+str(port))
    sk.listen()                     # 监听链接
    conn, addr = sk.accept()        # 接受客户端链接

    while True:
        try:
            ret = conn.recv(1024)       # 接收客户端信息
            # print(type(ret)) = class 'bytes'
            # print(ret.decode('utf-8'))
            if ret == b'bye':           # stop handle
                conn.send(b'bye')
                break
            # rText = str(ret).replace("\'", "\"")
            # print(rText)
            try:
                jsonText = json.loads(ret)
                info = json.dumps(mm32program.jsonhandle(jsonText))
            except Exception as e:
                info = ("[error] json handle failed.")
            conn.send(bytes(info, encoding='utf-8'))
        except Exception as e:
            info = ("[error] recv failed.")
            conn.send(bytes(info, encoding='utf-8'))
    conn.close()    # close client connect
    sk.close()      # cloase server socket

if __name__ == "__main__":
    cmdHandle()