# MM32Programmer CMD

## Bref

this is just for MM32-LINK MINI Programmer.


## MM32Programmer Command List

### 1.deviceList

#### Paramater: String
```json		
{
	command: 'deviceList',
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
    command: 'connectDevice', 
    index: 1
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