# link固件升级
# 首先读取文件的前256个字节，依次读取（字节）
# id         0   ：16
# fileVer    16  ：4
# mode       20  ：16
# version    36  ：16
# partName   52  ：16
# md5        68  ：32
# date       100 ：32
# 确认前两个字段对不对，id应为"MindMotion",
# 通过3des和密钥'MindMotion Upgrade'将剩下的数据解码成hex信息，用于升级
# 在计算升级信息的md5和开头获取的信息进行比较，如果正确则升级
from Crypto.Cipher import DES3
from Crypto.Hash import SHA256, MD5
import binascii

class LinkUpgrade:

    def __init__(self, file: str) -> None:
        self.upgradeFile = file

    # 以二进制方式打开文件，按顺序读取前256个字节, 判断文件内容是否是用于固件升级
    @staticmethod
    def readDatFile(datFile: str):
        info = bytes('', encoding="UTF-8")
        with open(datFile, "rb") as f:
            info = f.read()
        id = info[0:16].decode("UTF-8").strip("\x00")
        mode = info[20:36].decode("UTF-8").strip("\x00")
        if id == "ID:MindMotion" and mode == "App":
            md5 = info[68:100].decode("UTF-8")
            data = info[256:]
            # print(info[0:16].decode("UTF-8").strip("\x00") == "ID:MindMotion")
            # print("ID:" + info[0:16].decode("UTF-8"))
            # print("fileVersion: " + info[16:20].decode("UTF-8"))
            # print("Mode: " + info[20:36].decode("UTF-8"))
            # print("version: " + info[36:52].decode("UTF-8"))
            # print("partName: " + info[52:68].decode("UTF-8"))
            # print("md5: " + info[68:100].decode("UTF-8"))
            # print("date:" + info[100:132].decode("UTF-8"))
            return md5, data
        else:
            return False
    
    @staticmethod
    def parse3des(md5: str, data: bytes):
        # 生成密钥
        # key = "MindMotion Upgrade".encode('utf-8') # bytes.fromhex("507EB4BB9E2430761A7F763EEB95B047") get_random_bytes(16)
        key = DES3.adjust_key_parity("MindMotion Upgrade".encode('utf-8')[:16])
        # 3des解密
        des3Obj = DES3.new(bytes.fromhex("507EB4BB9E2430761A7F763EEB95B047"), DES3.MODE_ECB)
        decData = des3Obj.decrypt(data)
        # md5验证
        md5Obj = MD5.new()
        md5Obj.update(decData)
        digest = md5Obj.hexdigest()
        print(key.hex())
        print(md5)
        print(digest)

# if __name__ == "__main__":
#     md5, dat = LinkUpgrade.readDatFile(r"C:\MindMotion\MM32Programmer\upgrade\MM32LinkUpgrade.dat")
#     LinkUpgrade.parse3des(md5, dat)
