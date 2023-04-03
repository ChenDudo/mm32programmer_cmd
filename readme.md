# MM32Programmer Driver
[TOC]
## Brief

For MM32-LINK Programmer Server.

## 服务器运行
```powershell
cmdserver.exe -R 1234

cmdserver.exe -run 1234
```

## 客户端测试
```powershell
python cmsclient.py
```

## API 接口说明

### 1. 扫描 LINK 设备

client cmd:
```json		
{"command": "devicelist"}
```
old cmd:
```cmd
-j "{'command': 'devicelist'}"
```

return:
```json	
{
    "code": 0, 
    "message": "[info] Get device list success", 
    "data": [
        {
            "uid": "0880ff20f17004c75fd",
            "product": "MM32_V1 CMSIS-DAP",
            "vendor": "MindMotion"
        }, 
        {
            "uid": "0880ff20f17004c75fd", 
            "product": "MM32_V1 CMSIS-DAP", 
            "vendor": "MindMotion"
        }
    ]
}
```

### 2. 连接目标板

client cmd:
```json	
{"command": "connectDevice", "index": 0, "speed": 5000000}
```

old cmd:
```cmd
-j "{'command': 'connectDevice', 'index': 0, 'speed': 5000000}"
```

- index 为 deviceList 索引值,后期可以扩展编程器配置
- speed: 小于 1,000 或没配置时，默认Speed 为 1,000,000


Return
```json	
{
    "code": 0, 
    "message": "[info] You select idx=0, device UID:0880ff20f17004c75fd.[info] Target connnect Pass.", 
    "data": [
        {
            "MCU_ID": 196154487, 
            "CPU_INFO": "Cortex-M0 r0p0", 
            "DEV_ID": 2353221841,
            "UID1": 1296904704, 
            "UID2": 4294967112, 
            "UID3": 4294966911
        }
    ]
}
```

### 3. 读取 Memory

client cmd:
```json	
{"command": "readMemory","index": 0,"mcu": "MM32F0010","address": 0,"length": 10}
```

- address:欲读取数据地址<br />
- length:欲读取数据长度(全部为10进制)

old cmd:
```cmd
-j "{'command': 'readMemory', 'index': 0, 'mcu': 'MM32F0010', 'address': 0, 'length': 10}"
```

Return
```json	
{
    "code": 0, 
    "message": "[info] Read Success", 
    "data": [255, 255, 255, 255, 255, 255, 255, 255, 255, 255]
}
```


### 4. 写入 Memory

client cmd:
```json
{"command": "writeMemory","index": 0,"speed": 5000000,"mcu": "MM32F0010","address": 0,"data": [1, 2]}
```

old cmd:
```cmd
"{'command': 'writeMemory','index': 0,'speed': 5000000',mcu': 'MM32F0010','address': 0,'data': [1, 2]}"
```
- address:欲写入数据地址<br />
- length:欲写入取数据长度(全部为10进制)<br />
- data: 欲写入数据

Return
```json
{
    "code": 0, 
    "message": "[info] Read Success", 
    "data": [255, 255, 255, 255, 255, 255, 255, 255, 255, 255]
}
```

### 5.1 全片擦除
client cmd:
```json
{"command": "earseChip","index": 0,"mcu": "MM32F0010"}
```
old cmd:
```cmd
"{'command': 'earseChip','index': 0,'mcu': 'MM32F0010'}"
```
Return
```json
{
    "code": 0, 
    "message": "[info] Earse Success\n", 
    "data": []
}
```

### 5.2 扇区擦除
client cmd:
```json
{"command": "earseSector","index": 0,"mcu": "MM32F0010","address": 0,"length": 32768}
```
old cmd:
```json
-j "{'command': 'earseSector','index': 0,'mcu': 'MM32F0010','address': 0,'length': 32768}"
```
Return:
```json
{
    "code": 0, 
    "message": "[info] Earse Success\n", 
    "data": []
}
```


### 6 读32位内存
client cmd:
```json
{"command": "readMem32", "index": 0, "address": 536868864, "length": 8}
```
old cmd:
```json
-j "{'command': 'readMem32', 'index': 0, 'address': 536868864, 'length': 8}"
```
- address: 要写入的地址<br />
- length: 读取长度 /（32bit）个数

### 7 写32位内存
client cmd:
```json
{"command": "writeMem32", "index": 0, "address": 1073881092, "data": [1164378403]}
```
old cmd:
```json
-j "{'command': 'writeMem32', 'index': 0, 'address': 1073881092, 'data': [1164378403]}"
```

### 8 选项字节擦除
client cmd:
```json
{"command": "optEarse", "index": 0, "address": 536868864}
```
old cmd:
```cmd
-j "{'command': 'optEarse', 'index': 0, 'address': 536868864}"
```

### 9 选项字节编程
client cmd:
```json
{"command": "optWrite", "index": 0, "address": 536868864, "data": [23205,65280,2805,255]}
```
old cmd:
```json
-j "{'command': 'optWrite', 'index': 0, 'address': 536868864, 'data': [23205,65280,2805,255]}"
```

### 10 特殊 F0010 擦除
client cmd:
```json
{"command": "reEarseF0010", "index": 0}
```
old cmd:
```json
-j "{'command': 'reEarseF0010', 'index': 0}
```

### 11 释放LINK
client cmd:
```json
{"command": "quit_reset", "index": 0, "reset": 1}
```
old cmd:
```json
-j "{'command': 'quit_reset', 'index': 0, 'reset': 1}"
```

- reset = 1: reset&run and release LINK (default)
- reset = 0: no reset and release LINK








## How to Get Target Info

> From MindMotion User-Manual
### 1. CortexM.CPUID

| 0xE000ED00 |  SW_ID | JTAG_ID
|---|:---:|:---:|
| MM32F0010 | 0x0BB11477 |  |
| MM32F0020 | 0x0BB11477 |  |
| MM32F0040 | 0x0BB11477 |  |
| MM32F0140 | 0x0BB11477 |  |
| MM32F0160 | 0x0BB11477 |  |
| MM32F0270 | 0x0BB11477 |  |
| MM32G0140 | 0x0BB11477 |  |
| MM32L0020 | 0x0BC11477 |  |
| MM32L0130 | 0x0BB11477 |  |
| MM32F3270 | 0x2BA01477 | 0x4BA00477 |
| MM32F5270 | 0x1BE12AEB | 0x0BE11AEB |

### 2. MCU DEV_ID

| MCU | Addr | Value|
|---|:---:|:---:|
| MM32F0010 | 0x40013400 | 0x8C4350D1 |
| MM32F0020 | 0x40013400 | 0x4C50F800 |
| MM32F0040 | 0x40013400 | 0X4C50E800 |
| MM32F0140 | 0x40013400 | 0X4C50E800 |
| MM32F0160 | 0x40013400 | 0X4C50E900 |
| MM32F0270 | 0x40013400 | 0xCC5680F1 |
| MM32G0140 | 0x40013400 | 0X4C50E800 |
| MM32L0020 | 0x40013400 | 0x4C512000 |
| MM32L0130 | 0x40013400 | 0x4C4D1000 |
| MM32F3270 | 0x40007080 | 0xCC9AA0E7 |
| MM32F5270 | 0x40007080 | 0x4D4D0800 |



## 其他
###  OptionByte 操作笔记

### OptionByte 编程
对应地址写入值
1. 读 FLASH_CR.LOCK 位 <br />
2. 判断 FLASH_CR.LOCK = 1 ？<br />
3. yes:<br />
   执行解锁序列：<br />
   FLASH->KEYR = 0x45670123;<br />
   FLASH->KEYR = 0xCDEF89AB;<br />
4. 判断 FLASH_CR.OPTWRE = 0 ?
5. yes:<br />
   执行解锁序列：<br />
   FLASH->OPTKEYR = 0x45670123;<br />
   FLASH->OPTKEYR = 0xCDEF89AB;<br />
6. 写 FLASH_CR.OPTPG = 1
7. 写 所需地址 半字操作
   1. FLASH_AR = 写入的地址
8. 等待 FLASH_SR.BSY != 1
9.  FLASH_CR.OPTPG = 0
10. 读 目标地址 检查编程值是否匹配
    
### OptionByte 擦除
对应地址擦除
1. 读 FLASH_CR.LOCK 位 ，判断 = 1 ？<br />
3. yes:<br />
   执行解锁序列：<br />
   写 FLASH->KEYR = 0x45670123;<br />
   写 FLASH->KEYR = 0xCDEF89AB;<br />
4. 读 FLASH_CR.OPTWRE，判断 = 0 ?
5. yes:<br />
   执行解锁序列：<br />
   写 FLASH->OPTKEYR = 0x45670123;<br />
   写 FLASH->OPTKEYR = 0xCDEF89AB;<br />
6. 写 FLASH_AR = 写入的地址
7. 写 FLASH_CR.OPTER = 1
8. 写 FLASH_CR.STRT  = 1
9. 读 FLASH_SR.BSY ， while != 1
10. 写 FLASH_CR.OPTER = 0
11. 读 OptionByte 所有地址数据检查


### 主闪存读保护
> 系统重新上电复位，加载 RDPs 才能生效

使能读保护：
- 设置 FLASH_AR 地址值为 0x1FFF_F800，执行该选项区块擦除
- 按选项字节区块半字编程的操作方式，按顺序写 0x807F（RDP）半字到对应地址。
- 进行上电复位以重新加载选项字节，此时读保护被使能

解除读保护：
从内置 SRAM 或 ICP 方式解除读保护的过程是：
- 设置 FLASH_AR 地址值为 0x1FFFF800，执行该选项区块擦除。按选项字节区块半字编程的操作方式，按流程写 0x5AA5 半字到对应地址。
- 设置 FLASH_AR 地址值为 0x08000000，执行主 Flash 全片擦除。
- 进行上电复位以重新加载选项字节，此时读保护被解除。


### 主闪存写保护

使能写保护
- 通过设置选项字节区块中的 WRP0 中的 WRP 位为 0，设置写保护
- 系统复位后将加载新选项字节，使能写保护<br />
如果试图写入或擦除一个受写保护的页，会引起 FLASH_SR 中的 WRPRTERR 标志位置位。

| address | [15:8] | [7:0] | default |
|:-------:|:------:|:-----:|:-------:|
| 0x1FFF_F808 | nWRP0 | WRP0 | 0xFFFF |

解除写保护<br />
情形 1：解除写保护，同时解除读保护
- 使用闪存控制寄存器（FLASH_CR）的 OPTER 位擦除整个选项字节区块: 写 0x5AA5 半字到对应地址 0x1FFFF800；
- 对 0x08000000 的主 Flash 全片擦除；
- 系统复位，重装载选项字节（包含新的 WRP 字节），写保护被解除<br />
使用这种方法，将解除全片主闪存模块的写保护同时擦除全片主闪存块。

情形 2：解除写保护，同时保持读保护有效，这种情况常见于用户自己实现在程序中编程的启动
程序中：
- 使用闪存控制寄存器（FLASH_CR）的 OPTER 位擦除整个选项字节区块
- 系统复位，重装载选项字节（包含新的 WRP 字节），写保护被解除<br />
使用这种方法，将解除整个主闪存模块的写保护，同时保持读保护有效。
