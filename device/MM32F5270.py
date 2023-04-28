"""
 Flash OS Routines (Automagically Generated)
 Copyright (c) 2017-2017 ARM Limited
"""
from .flash import Flash

"""
 Flash OS Routines (Automagically Generated)
 Copyright (c) 2017-2017 ARM Limited
"""
class MM32F5270(object):
    CHIP_CORE = 'STAR-MC1'

    PAGE_SIZE = 1024 * 1
    SECT_SIZE = 1024 * 1
    CHIP_SIZE = 1024 * 256

    def __init__(self, xlink):
        super(MM32F5270, self).__init__()

        self.xlink = xlink

        self.flash = Flash(self.xlink, MM32F5270_flash_algo)

    def sect_erase(self, addr, size):
        self.flash.Init(0, 0, 1)
        for i in range(addr // self.SECT_SIZE, (addr + size + (self.SECT_SIZE - 1)) // self.SECT_SIZE):
            self.flash.EraseSector(self.SECT_SIZE * i)
        self.flash.UnInit(1)

    def chip_write(self, addr, data):
        self.sect_erase(addr, len(data))
        self.flash.Init(0, 0, 2)
        for i in range(0, len(data)//self.PAGE_SIZE):
            self.flash.ProgramPage(0x08000000 + addr + self.PAGE_SIZE * i, data[self.PAGE_SIZE*i : self.PAGE_SIZE*(i+1)])
        self.flash.UnInit(2)

    def chip_read(self, addr, size, buff):
        c_char_Array = self.xlink.read_mem(0x08000000 + addr, size)

        buff.extend(list(bytes(c_char_Array)))

    def chip_erase(self):
        self.flash.Init(0, 0, 4)
        self.flash.EraseChip()
        self.flash.UnInit(4)

class MM32F5280(MM32F5270):
    PAGE_SIZE = 1024 * 1
    SECT_SIZE = 1024 * 1
    CHIP_SIZE = 1024 * 256

    def __init__(self, xlink):
        super().__init__(xlink)

        self.flash = Flash(self.xlink, MM32F5270_flash_algo)


MM32F5270_flash_algo = {
    'load_address' : 0x20000000,
    'instructions' : [
        0xE00ABE00, 0x062D780D, 0x24084068, 0xD3000040, 0x1E644058, 0x1C49D1FA, 0x2A001E52, 0x4770D1F2,
        0x0004F242, 0x0002F2C4, 0x1123F240, 0x5167F2C4, 0xF6486001, 0xF6CC11AB, 0x600151EF, 0xBF004770,
        0x9002B083, 0x92009101, 0x0004F242, 0x0002F2C4, 0x1123F240, 0x5167F2C4, 0xF6486001, 0xF6CC12AB,
        0x600252EF, 0x0008F242, 0x0002F2C4, 0x60026001, 0x0000F242, 0x0002F2C4, 0x60012100, 0x000CF242,
        0x0002F2C4, 0xF0416801, 0x60010114, 0x001CF242, 0x0002F2C4, 0x07406800, 0xD4152800, 0xF243E7FF,
        0xF2C40000, 0xF2450000, 0x60015155, 0x0004F243, 0x0000F2C4, 0x60012106, 0x0008F243, 0x0000F2C4,
        0x71FFF640, 0xE7FF6001, 0xB0032000, 0xBF004770, 0x9000B081, 0x0010F242, 0x0002F2C4, 0xF0416801,
        0x60010180, 0xF4216801, 0x60017180, 0xB0012000, 0xBF004770, 0xF242B081, 0xF2C40014, 0xF04F0002,
        0x60016100, 0x000CF242, 0x0002F2C4, 0xF0416801, 0x60010114, 0x0010F242, 0x0002F2C4, 0xF0416801,
        0x60010104, 0xF0416801, 0x60010140, 0xF242E7FF, 0xF2C4000C, 0x68000002, 0x280007C0, 0xE7FFD008,
        0x0000F243, 0x0000F2C4, 0x21AAF64A, 0xE7EE6001, 0x0010F242, 0x0002F2C4, 0xF0216801, 0x60010104,
        0x000CF242, 0x0002F2C4, 0xF0106800, 0xD00B0F14, 0xF242E7FF, 0xF2C4000C, 0x68010002, 0x0114F041,
        0x20016001, 0xE0029000, 0x90002000, 0x9800E7FF, 0x4770B001, 0x9000B082, 0xF2429800, 0xF2C40114,
        0x60080102, 0x000CF242, 0x0002F2C4, 0xF0416801, 0x60010114, 0x0008F242, 0x0002F2C4, 0x1123F240,
        0x5167F2C4, 0xF6486001, 0xF6CC11AB, 0x600151EF, 0x0010F242, 0x0002F2C4, 0xF0416801, 0x60010120,
        0xF0416801, 0x60010140, 0xF242E7FF, 0xF2C4000C, 0x68000002, 0x280007C0, 0xE7FFD008, 0x0000F243,
        0x0000F2C4, 0x21AAF64A, 0xE7EE6001, 0x0010F242, 0x0002F2C4, 0xF0216801, 0x60010120, 0x000CF242,
        0x0002F2C4, 0xF0106800, 0xD00B0F14, 0xF242E7FF, 0xF2C4000C, 0x68010002, 0x0114F041, 0x20016001,
        0xE0029001, 0x90012000, 0x9801E7FF, 0x4770B002, 0xB082B580, 0xFEE4F7FF, 0x0000F64F, 0x70FFF6C1,
        0xF7FF9000, 0xF242FF97, 0xF2C40110, 0x680A0102, 0x73EFF641, 0x600A401A, 0xF042680A, 0x600A0210,
        0x21A5F645, 0x80119A00, 0xF242E7FF, 0xF2C4000C, 0x68000002, 0x280007C0, 0xE7FFD008, 0x0000F243,
        0x0000F2C4, 0x21AAF64A, 0xE7EE6001, 0x0010F242, 0x0002F2C4, 0xF0216801, 0x60010110, 0x000CF242,
        0x0002F2C4, 0xF0106800, 0xD00B0F14, 0xF242E7FF, 0xF2C4000C, 0x68010002, 0x0114F041, 0x20016001,
        0xE0029001, 0x90012000, 0x9801E7FF, 0xBD80B002, 0xB084B580, 0xFFACF7FF, 0xF7FF9003, 0x2100FEFB,
        0x71FEF6C1, 0x46089002, 0xFF44F7FF, 0x90012100, 0xB0044608, 0xBF00BD80, 0x9000B082, 0x000CF242,
        0x0002F2C4, 0xF0416801, 0x60010114, 0x0010F242, 0x0002F2C4, 0xF0416801, 0x60010102, 0xF2429900,
        0xF2C40214, 0x60110202, 0xF0416801, 0x60010140, 0xF242E7FF, 0xF2C4000C, 0x68000002, 0x280007C0,
        0xE7FFD008, 0x0000F243, 0x0000F2C4, 0x21AAF64A, 0xE7EE6001, 0x0010F242, 0x0002F2C4, 0xF0216801,
        0x60010102, 0x000CF242, 0x0002F2C4, 0xF0106800, 0xD00B0F14, 0xF242E7FF, 0xF2C4000C, 0x68010002,
        0x0114F041, 0x20016001, 0xE0029001, 0x90012000, 0x9801E7FF, 0x4770B002, 0x4613B083, 0x91019002,
        0x2003F88D, 0xB0032001, 0xBF004770, 0x9002B084, 0x92009101, 0x30019801, 0x0001F020, 0xF2429001,
        0xF2C4000C, 0x68010002, 0x0104F041, 0xE7FF6001, 0x28009801, 0xE7FFD044, 0x0010F242, 0x0002F2C4,
        0xF0416801, 0x60010101, 0x88009800, 0x80089902, 0xF242E7FF, 0xF2C4000C, 0x68000002, 0x280007C0,
        0xE7FFD008, 0x0000F243, 0x0000F2C4, 0x21AAF64A, 0xE7EE6001, 0x0010F242, 0x0002F2C4, 0xF0216801,
        0x60010101, 0x000CF242, 0x0002F2C4, 0xF0106800, 0xD00B0F14, 0xF242E7FF, 0xF2C4000C, 0x68010002,
        0x0114F041, 0x20016001, 0xE00C9003, 0x30029802, 0x98009002, 0x90003002, 0x38029801, 0xE7B79001,
        0x90032000, 0x9803E7FF, 0x4770B004, 0x00000000
    ],

    'pc_Init'            : 0x20000041,
    'pc_UnInit'          : 0x200000D1,
    'pc_EraseSector'     : 0x20000319,
    'pc_ProgramPage'     : 0x200003CD,
    'pc_Verify'          : 0x12000001F,
    'pc_EraseChip'       : 0x200002F1,
    'pc_BlankCheck'      : 0x200003B9,
    'pc_Read'            : 0x12000001F,
    
    'static_base'        : 0x20000800,
    'begin_data'         : 0x20000C00,
    'begin_stack'        : 0x20001400,

    'analyzer_supported' : False,

    # Relative region addresses and sizes
    'ro_start'           : 0x00000000,
    'ro_size'            : 0x0000046C,
    'rw_start'           : 0x0000046C,
    'rw_size'            : 0x00000004,
    'zi_start'           : 0x00000470,
    'zi_size'            : 0x00000000,

    # Flash information
    'flash_start'        : 0x08000000,
    'flash_size'         : 0x00040000,
    'flash_page_size'    : 0x00000400,
    'sector_sizes': (
        (0x00000, 0x00400),
    )
}
