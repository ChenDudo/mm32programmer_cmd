# MM32Programmer CMD

## Bref

this is just for MM32-LINK MINI Programmer.

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
| MM32F0010 | 0x40013400 | 0xCC4350D1 |
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

### 1.deviceList

#### Paramater: String
```json		
{
	"command": "devicelist"
}
```

#### Return: json_printf
```json	
{
    code: 0,
    message: '',
    data: [
        {
            uid: "0880ff1bf12004c75fd",
            target: "CMSIS-DAP",
            company:"MindMotion Co.,Ltd.",
        },
    ]
}
```

### 2.connectDevice
#### Paramater:
```json	
{
	"command": "connectDevice",
	"index": 1
}
```

- index为deviceList返回的下标索引值,后期可以扩展编程器配置
#### Return:
```json	
{
    code：0,
    message: '',
    data: {},
}
```

### 3.readMemory
#### Paramater:
```json	
{
    command: 'readMemory', 
    address: 134217728, 
    length: 16
}
```
    
- address:欲读取数据地址
- length:欲读取数据长度(全部为10进制)
#### Return:
```json	
{
    code: 0,
    message: '',
    data: ["AA","BB","11","01","23"],
}
```

### 4.writeMemory
#### Paramater:
```json
{
    command: 'writeMemory',
    address: 134217728, 
    length: 16,
    data: ["00","11","22","33","44","55","66","77","88","99","AA","BB","CC","DD","EE","FF"],
}
```

- address:欲写入数据地址
- length:欲写入取数据长度(全部为10进制)
- data: 欲写入数据
#### Return:
```json
    {
        code: 0,
        message: '',
        data: {},
    }
```