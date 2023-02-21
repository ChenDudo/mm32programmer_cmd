"""
 Flash OS Routines (Automagically Generated)
 Copyright (c) 2017-2017 ARM Limited
"""
from .flash import Flash

"""
 Flash OS Routines (Automagically Generated)
 Copyright (c) 2017-2017 ARM Limited
"""
class MM32F0020(object):
    CHIP_CORE = 'Cortex-M0'

    PAGE_SIZE = 1024 * 1 // 2
    SECT_SIZE = 1024 * 1
    CHIP_SIZE = 1024 * 32

    def __init__(self, xlink):
        super(MM32F0020, self).__init__()

        self.xlink = xlink

        self.flash = Flash(self.xlink, MM32F0020_flash_algo)

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

MM32F0020_flash_algo = {
    'load_address' : 0x20000000,
    'instructions' : [
        0xE00ABE00, 0x062D780D, 0x24084068, 0xD3000040, 0x1E644058, 0x1C49D1FA, 0x2A001E52, 0x4770D1F2,
        0x4A3C483B, 0x483C6050, 0x48396050, 0x483A6090, 0x20FF6090, 0x483960D0, 0x46106150, 0x22206900,
        0x4A344310, 0x46106110, 0x22406900, 0x4A314310, 0xBF006110, 0x68C0482F, 0x40102230, 0xD0F92800,
        0x68C0482C, 0x40102210, 0xD0072800, 0x68C04829, 0x43102214, 0x60D04A27, 0x47702001, 0x69004825,
        0x43902220, 0x61104A23, 0x69004610, 0x43102210, 0x61104A20, 0x4A214822, 0x217D8010, 0xBF0000C9,
        0x1E494608, 0xD1FB2800, 0x6900481A, 0x43902210, 0x61104A18, 0x60D020FF, 0x06C02001, 0x46106150,
        0x22046900, 0x4A134310, 0x46106110, 0x22406900, 0x4A104310, 0xBF006110, 0x68C0480E, 0x40102230,
        0xD0F92800, 0x68C0480B, 0x40102210, 0xD0072800, 0x68C04808, 0x43102214, 0x60D04A06, 0xE7BC2001,
        0x69004804, 0x43902204, 0x61104A02, 0xE7B42000, 0x45670123, 0x40022000, 0xCDEF89AB, 0x1FFFF800,
        0x00005AA5, 0x48194601, 0x221468C0, 0x4A174310, 0x461060D0, 0x22026900, 0x4A144310, 0x46106110,
        0x69006141, 0x43102240, 0x61104A10, 0x4810E002, 0x60104A10, 0x68C0480D, 0x0FC007C0, 0xD1F62800,
        0x6900480A, 0x43902202, 0x61104A08, 0x68C04610, 0x40102214, 0xD0062800, 0x68C04804, 0x4A034310,
        0x200160D0, 0x20004770, 0x0000E7FC, 0x40022000, 0x0000AAAA, 0x40003000, 0x4603B510, 0x4C114810,
        0x48116060, 0x20006060, 0x46206020, 0x241468C0, 0x4C0C4320, 0x462060E0, 0x4C0C6800, 0x4C094320,
        0x46206020, 0x240469C0, 0x28004020, 0x4808D106, 0x60204C08, 0x60602006, 0x60A04807, 0xBD102000,
        0x45670123, 0x40022000, 0xCDEF89AB, 0xCC103FFF, 0x00005555, 0x40003000, 0x00000FFF, 0x4603B510,
        0x08411C48, 0x481F0049, 0x240468C0, 0x4C1D4320, 0xE03360E0, 0x68C0481B, 0x43202414, 0x60E04C19,
        0x06000E18, 0x06E42401, 0xD11742A0, 0x69004815, 0x43202401, 0x61204C13, 0x80188810, 0x4812E002,
        0x60204C12, 0x68C0480F, 0x0FC007C0, 0xD1F62800, 0x6900480C, 0x00400840, 0x61204C0A, 0x68C04809,
        0x40202414, 0xD0062800, 0x68C04806, 0x4C054320, 0x200160E0, 0x1C9BBD10, 0x1E891C92, 0xD1C92900,
        0xE7F72000, 0x40022000, 0x0000AAAA, 0x40003000, 0x48044601, 0x22806900, 0x4A024310, 0x20006110,
        0x00004770, 0x40022000, 0x00000000
    ],

    'pc_Init'            : 0x20000199,
    'pc_UnInit'          : 0x20000291,
    'pc_EraseSector'     : 0x20000125,
    'pc_ProgramPage'     : 0x200001FD,
    'pc_Verify'          : 0x12000001F,
    'pc_EraseChip'       : 0x20000021,
    'pc_BlankCheck'      : 0x12000001F,
    'pc_Read'            : 0x12000001F,
    
    'static_base'        : 0x20000300,
    'begin_data'         : 0x20000400,
    'begin_stack'        : 0x20000800,

    'analyzer_supported' : False,

    # Relative region addresses and sizes
    'ro_start'           : 0x00000000,
    'ro_size'            : 0x00000288,
    'rw_start'           : 0x00000288,
    'rw_size'            : 0x00000004,
    'zi_start'           : 0x0000028C,
    'zi_size'            : 0x00000000,

    # Flash information
    'flash_start'        : 0x08000000,
    'flash_size'         : 0x00008000,
    'flash_page_size'    : 0x00000400//2,
    'sector_sizes': (
        (0x00000, 0x00400),
    )
}
