# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    :   cmsclient.py
@Time    :   2023/03/31 15:51:53
@Author  :   Chen Do
@Version :   1.0
@Desc    :   None
"""

import socket
sk = socket.socket()            # 创建客户端套接字


sk.connect(('127.0.0.1',1234))  # 尝试连接服务器

while True:
    info = input('>>>')         # 信息发送
    if info=='':
        sk.close()
        info='---hello----'

    sk.send(bytes(info,encoding='utf-8'))
    ret = sk.recv(1024)         # 信息接收

    if ret == b'bye':           # 结束会话
        sk.send(b'bye')
        break
    print(ret.decode('utf-8'))  # 信息打印
    
sk.close()                      # 关闭客户端套接字
