# MM32Programmer CMD

## Brief

this is just for MM32-LINK MINI Programmer.

## support 
- MM32F0010
- MM32F0020
- MM32F0040
- MM32F0130 *
- MM32F0140 *
- MM32F0160 *
- MM32G0140 *
- MM32A0140 *
- MM32F003 *
- MM32L07x *
- MM32F03x *
- MM32L0130 *
- MM32L0160 *
- MM32SPIN05 *
- MM32SPIN06 *
- MM32SPIN07 *
- MM32SPIN08 *
- MM32SPIN0280 *
- MM32F103C8 *
- MM32F103CB *
- MM32L3xx *
- MM32F3270 *
- MM32F5270 *
- MM32F5280 *
  
> \*: Test



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
| MM32L0020 | `0x0BC11477` ?? |  |
| MM32L0130 | 0x0BB11477 |  |
| MM32F3270 | 0x2BA01477 | 0x4BA00477 |
| MM32F5270 | 0x1BE12AEB | 0x0BE11AEB |

### 2. MCU DEV_ID

| MCU | Addr | Value|
|---|:---:|:---:|
| MM32F0010 | 0x40013400 | 0xBC4350D1 |
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

## MM32Programmer Command List

### 1. deviceList

json file
```json		
{
	"command": "devicelist"
}
```

json command
```cmd
"{'command': 'devicelist'}"
```

return
```json	
{
    'code': 0, 
    'message': '[info] Get device list success', 
    'data': [
        {
            'uid': '0880ff20f17004c75fd',
            'product': 'MM32_V1 CMSIS-DAP',
            'vendor': 'MindMotion'
        }, 
        {
            'uid': '0880ff20f17004c75fd', 
            'product': 'MM32_V1 CMSIS-DAP', 
            'vendor': 'MindMotion'
        }
    ]
}
```

### 2.connectDevice

json file
```json	
{
	"command": "connectDevice",
	"index": 1
}
```

json command
```cmd
"{'command': 'connectDevice', 'index': 0}"
```

> index为deviceList返回的下标索引值,后期可以扩展编程器配置


Return
```json	
{
    'code': 0, 
    'message': '[info] You select idx=0, device UID:0880ff20f17004c75fd\n[info] Target connnect Pass\n', 
    'data': [
        {
            'MCU_ID': 196154487, 
            'CPU_INFO': 'Cortex-M0 r0p0', 
            'DEV_ID': 2353221841
        }
    ]
}
```

### 3.readMemory

json file
```json	
{
	"command": "readMemory",
	"index": 0,
	"mcu": "MM32F0010",
    "address": 0, 
    "length": 10
}
```
    
>address:欲读取数据地址</br>
length:欲读取数据长度(全部为10进制)

json command
```cmd
"{'command': 'readMemory', 'index': 0, 'mcu': 'MM32F0010', 'address': 0, 'length': 10}"
```

Return
```json	
{
    'code': 0, 
    'message': '[info] Read Success', 
    'data': [255, 255, 255, 255, 255, 255, 255, 255, 255, 255]
}
```

### 4.writeMemory

json file
```json
{
	"command": "writeMemory",
	"index": 0,
	"mcu": "MM32F0010",
	"address": 0,
    "data": [1, 2]
}
```

json command
```cmd
"{'command': 'writeMemory','index': 0,'mcu': 'MM32F0010','address': 0,'data': [1, 2]}"
```

>address:欲写入数据地址</br>
length:欲写入取数据长度(全部为10进制)</br>
data: 欲写入数据


Return
```json
{
    'code': 0, 
    'message': '[info] Read Success', 
    'data': [255, 255, 255, 255, 255, 255, 255, 255, 255, 255]
}
```

### 5.1 全片擦除 earseChip
json file
```json
{
	"command": "earseChip",
	"index": 0,
	"mcu": "MM32F0010"
}
```
json command
```cmd
"{'command': 'earseChip','index': 0,'mcu': 'MM32F0010'}"
```

### 5.2 扇区擦除 earseSector
json file
```json
{
	"command": "earseSector",
	"index": 0,
	"mcu": "MM32F0010",
	"address": 0,
	"length": 32768
}
```
Return
```json
{
    'code': 0, 
    'message': '[info] Earse Success\n', 
    'data': []
}
```

json command
```
"{'command': 'earseSector','index': 0,'mcu': 'MM32F0010','address': 0,'length': 32768}"
```

Return
```json
{
    'code': 0, 
    'message': '[info] Earse Success\n', 
    'data': []
}
```
