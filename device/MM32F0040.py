"""
 Flash OS Routines (Automagically Generated)
 Copyright (c) 2017-2017 ARM Limited
"""
from .flash import Flash

"""
 Flash OS Routines (Automagically Generated)
 Copyright (c) 2017-2017 ARM Limited
"""
class MM32F0040(object):
    CHIP_CORE = 'Cortex-M0'

    PAGE_SIZE = 1024 * 1
    SECT_SIZE = 1024 * 1
    CHIP_SIZE = 1024 * 32

    def __init__(self, xlink):
        super(MM32F0040, self).__init__()

        self.xlink = xlink

        self.flash = Flash(self.xlink, MM32F0x40_flash_algo)

    def sect_erase(self, addr, size):
        self.flash.Init(0, 0, 1)
        for i in range(addr // self.SECT_SIZE, (addr + size + (self.SECT_SIZE - 1)) // self.SECT_SIZE):
            self.flash.EraseSector(self.SECT_SIZE * i)
        self.flash.UnInit(1)

    def chip_write(self, addr, data):
        # self.sect_erase(addr, len(data))

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

class MM32F0140(MM32F0040):
    PAGE_SIZE = 1024 * 1
    SECT_SIZE = 1024 * 1
    CHIP_SIZE = 1024 * 64

    def __init__(self, xlink):
        # super(MM32F0140, self).__init__(xlink)
        super().__init__(xlink)

        self.flash = Flash(self.xlink, MM32F0x40_flash_algo)


MM32F0x40_flash_algo = {
    'load_address' : 0x20000000,
    'instructions' : [
        0xE00ABE00, 0x062D780D, 0x24084068, 0xD3000040, 0x1E644058, 0x1C49D1FA, 0x2A001E52, 0x4770D1F2,
        0x49A648A5, 0x48A66048, 0x47706048, 0x4603B510, 0x4CA248A1, 0x48A26060, 0x489F6060, 0x48A060A0,
        0x200060A0, 0x46206020, 0x241468C0, 0x4C9B4320, 0x462060E0, 0x240469C0, 0x28004020, 0x4899D106,
        0x60204C99, 0x60602006, 0x60A04898, 0xBD102000, 0x48924601, 0x22806900, 0x4A904310, 0x46106110,
        0x15926900, 0x4A8D4390, 0x20006110, 0x20014770, 0x498A06C0, 0x46086148, 0x211468C0, 0x49874308,
        0x460860C8, 0x21046900, 0x49844308, 0x46086108, 0x21406900, 0x49814308, 0xE0026108, 0x49824884,
        0x487E6008, 0x07C068C0, 0x28000FC0, 0x487BD1F6, 0x21046900, 0x49794388, 0x46086108, 0x211468C0,
        0x28004008, 0x4875D006, 0x430868C0, 0x60C84973, 0x47702001, 0xE7FC2000, 0x48704601, 0x68C06141,
        0x43102214, 0x60D04A6D, 0x6090486B, 0x6090486C, 0x69004610, 0x43102220, 0x61104A68, 0x69004610,
        0x43102240, 0x61104A65, 0x4869E002, 0x60104A66, 0x68C04862, 0x0FC007C0, 0xD1F62800, 0x6900485F,
        0x43902220, 0x61104A5D, 0x68C04610, 0x40102214, 0xD0062800, 0x68C04859, 0x4A584310, 0x200160D0,
        0x20004770, 0xB500E7FC, 0xFF5AF7FF, 0xF7FF4859, 0x4852FFC3, 0x49586900, 0x49504008, 0x46086108,
        0x21106900, 0x494D4308, 0x48546108, 0x80084951, 0x484FE002, 0x6008494C, 0x68C04848, 0x0FC007C0,
        0xD1F62800, 0x69004845, 0x43882110, 0x61084943, 0x68C04608, 0x40082114, 0xD0062800, 0x68C0483F,
        0x493E4308, 0x200160C8, 0x2000BD00, 0xB500E7FC, 0xFFC9F7FF, 0xFF5BF7FF, 0xBD002000, 0x48374601,
        0x221468C0, 0x4A354310, 0x461060D0, 0x22026900, 0x4A324310, 0x46106110, 0x69006141, 0x43102240,
        0x61104A2E, 0x4832E002, 0x60104A2F, 0x68C0482B, 0x0FC007C0, 0xD1F62800, 0x69004828, 0x43902202,
        0x61104A26, 0x68C04610, 0x40102214, 0xD0062800, 0x68C04822, 0x4A214310, 0x200160D0, 0x20004770,
        0x4603E7FC, 0x47702001, 0x4603B510, 0x08411C48, 0x481A0049, 0x240468C0, 0x4C184320, 0xE02760E0,
        0x69004816, 0x43202401, 0x61204C14, 0x80188810, 0x4817E002, 0x60204C14, 0x68C04810, 0x0FC007C0,
        0xD1F62800, 0x6900480D, 0x00400840, 0x61204C0B, 0x68C04620, 0x40202414, 0xD0062800, 0x68C04807,
        0x4C064320, 0x200160E0, 0x1C9BBD10, 0x1E891C92, 0xD1D52900, 0xE7F72000, 0x45670123, 0x40022000,
        0xCDEF89AB, 0x00005555, 0x40003000, 0x00000FFF, 0x0000AAAA, 0x1FFFF800, 0x00001FEF, 0x00005AA5,
        0x00000000
    ],

    'pc_Init'            : 0x2000002D,
    'pc_UnInit'          : 0x20000071,
    'pc_EraseSector'     : 0x200001DD,
    'pc_ProgramPage'     : 0x20000249,
    'pc_Verify'          : 0x12000001F,
    'pc_EraseChip'       : 0x200001CF,
    'pc_BlankCheck'      : 0x20000243,
    'pc_Read'            : 0x12000001F,
    
    'static_base'        : 0x20000400,
    'begin_data'         : 0x20000800,
    'begin_stack'        : 0x20001000,

    'analyzer_supported' : False,

    # Relative region addresses and sizes
    'ro_start'           : 0x00000000,
    'ro_size'            : 0x000002C0,
    'rw_start'           : 0x000002C0,
    'rw_size'            : 0x00000004,
    'zi_start'           : 0x000002C4,
    'zi_size'            : 0x00000000,

    # Flash information
    'flash_start'        : 0x08000000,
    'flash_size'         : 0x00008000,
    'flash_page_size'    : 0x00000400,
    'sector_sizes': (
        (0x00000, 0x00400),
    )
}
