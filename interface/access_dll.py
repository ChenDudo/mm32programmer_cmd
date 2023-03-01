import json
from ctypes import *

BUFF_SIZE = 256
class AccessDll():

    class TRSystemConfig(Structure):
        _fields_ = [("serverAddress", c_ubyte * BUFF_SIZE),
                    ("database", c_ubyte * BUFF_SIZE)]

    def __init__(self, path):
        self.systemConfig = self.TRSystemConfig((c_ubyte * BUFF_SIZE)(*b"Temp"), (c_ubyte * BUFF_SIZE)(*b"mmData.db"))
        self.path = path
        self.dll = cdll.LoadLibrary(self.path)
        self.initStatus = self.dll.initSystemConfig(self.systemConfig)

    def print_json_to_str(self, buffer) -> dict:
        data_json = json.loads(buffer.value.decode('GBK'))
        # data_string = json.dumps(data_json, indent=4, ensure_ascii=False)
        return data_json

    def get_series_list(self):
        buf = create_string_buffer(81920)
        status = self.dll.getSeriesList(buf)
        buf_list = list(buf)
        if status != 0 or buf_list[30] == b'\x00':
            print('access fail, please check parameter')
        else:
            return buf

    def get_chip_list_for_all(self):
        buf = create_string_buffer(81920)
        status = self.dll.getChipList4All(buf)
        buf_list = list(buf)
        if status != 0 or buf_list[30] == b'\x00':
            print('access fail, please check parameter')
        else:
            return buf

    # def getSeriesAndPart(self) -> dict: # 系列确定开发板型号和内核，开发板型号确定flash大小(算法不好，系列不能重复出现，否则会覆盖之前的数据)
    #     seriesInfo = {}
    #     dataCenter = AccessDll("Temp/dataCenter.dll")
    #     allSeries = dataCenter.print_json_to_str(dataCenter.get_series_list())
    #     seriesList = allSeries["data"]
    #     for i in range(len(seriesList)): # 获取全系列名
    #         seriesInfo[seriesList[i]["seriesName"]] = {} # core,part

    #     allChips = dataCenter.print_json_to_str(dataCenter.get_chip_list_for_all())
    #     chipsList = allChips["data"]
    #     length = len(chipsList)
    #     chips = {} #partname:flashsize
    #     tempSeries = chipsList[0]["seriesName"]
    #     for i in range(length):
    #         series = chipsList[i]["seriesName"]
    #         if tempSeries != series:
    #             seriesInfo[tempSeries]["core"] = chipsList[i-1]["core"]
    #             seriesInfo[tempSeries]["part"] = chips
    #             chips = {} 
    #         tempSeries = series
    #         partName = chipsList[i]["partName"]
    #         flashSize = chipsList[i]["flashSize"]
    #         chips[partName] = flashSize
    #     #将最后的芯片信息填入
    #     seriesInfo[tempSeries]["core"] = chipsList[length - 1]["core"]
    #     seriesInfo[tempSeries]["part"] = chips

    #     #处理没有part的series
    #     info = {}
    #     for key, value in seriesInfo.items():
    #         if len(value) != 0:
    #             info[key] = value
    #         else:
    #             pass
        
    #     return info


# if __name__ == "__main__":
#     dataCenter = AccessDll("Temp/dataCenter.dll")
#     allSeries = dataCenter.getSeriesAndPart()
#     print((json.dumps(allSeries, indent=4, ensure_ascii=False)))
#     # allChips = dataCenter.print_json_to_str(dataCenter.get_chip_list_for_all())

