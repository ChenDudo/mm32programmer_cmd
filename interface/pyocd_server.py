import sys
sys.path.append(r"C:\Users\MM\gitworks\10.3.2.202\embeded-group2\mm32program")
import json
import socket
import threading
import access_pyocdServer
import time

class PyocdServer:

    def __init__(self, port: int) -> None:
        # 开启服务器端口，套接字监听
        self.startServer(port)
        # 创建客户端套接字，连接服务器端口
        self.sk = socket.socket()
        self.sk.connect(('127.0.0.1', port))

    def startServer(self, port: int):
        # target指向函数如果有参数必须放在args中，如果放在一起会直接运行
        evt = threading.Event()
        server = threading.Thread(target = access_pyocdServer.openServer, args=(port, evt), daemon=True)
        server.start()
        evt.wait()

    def clientSocket(self, command: dict, bye="continue"):
        if bye == "bye":
            content = "bye"
        else:
            content = json.dumps(command)
        self.sk.send(bytes(content, encoding="utf-8"))
        ret = self.sk.recv(1024*65)
        print(ret.decode('utf-8'))


if __name__ == "__main__":
    test = PyocdServer(1210)
    test.clientSocket({"command": "devicelist"})
    time.sleep(1)
    # test.clientSocket({"command": "scanTarget", "index": 0, "speed": 1000000})
    # time.sleep(1)
    test.clientSocket({"command": "connectDevice", "index": 0, "speed": 1000000, "mcu": "MM32F0130"})
    time.sleep(1)
    # test.clientSocket({"command": "earseChip", "index": 0, "speed": 1000000, "mcu": "MM32F0130"})
    # time.sleep(1)
    # data = [0x11 for _ in range(65536)]
    # print(len(data))
    # start = time.time()
    # test.clientSocket({"command": "writeMemory", "index": 0, "speed": 1000000, "mcu": "MM32F0130", "address":0, "data": data[:32768]})
    # test.clientSocket({"command": "writeMemory", "index": 0, "speed": 1000000, "mcu": "MM32F0130", "address":32768, "data": data[32768:]})
    # end = time.time()
    # print(end-start)
    test.clientSocket({}, "bye") # 关闭程序时，客户端套接字向服务器发送退出