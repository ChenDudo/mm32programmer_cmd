"""
 Flash OS Routines (Automagically Generated)
 Copyright (c) 2017-2017 ARM Limited
"""
from .flash import Flash

"""
 Flash OS Routines (Automagically Generated)
 Copyright (c) 2017-2017 ARM Limited
"""
class MM32F0270(object):
    CHIP_CORE = 'Cortex-M0'

    PAGE_SIZE = 1024 * 1
    SECT_SIZE = 1024 * 1
    CHIP_SIZE = 1024 * 128

    def __init__(self, xlink):
        super(MM32F0270, self).__init__()

        self.xlink = xlink

        self.flash = Flash(self.xlink, MM32F0270_flash_algo)

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

MM32F0270_flash_algo = {
    'load_address' : 0x20000000,
    'instructions' : [
        0xE00ABE00, 0x062D780D, 0x24084068, 0xD3000040, 0x1E644058, 0x1C49D1FA, 0x2A001E52, 0x4770D1F2,
        0x49A848A7, 0x48A86048, 0x47706048, 0x4603B510, 0x4CA448A3, 0x48A46060, 0x48A16060, 0x48A260A0,
        0x200060A0, 0x46206020, 0x241468C0, 0x4C9D4320, 0x462060E0, 0x240469C0, 0x28004020, 0x489BD106,
        0x60204C9B, 0x60602006, 0x60A0489A, 0xBD102000, 0x48944601, 0x22806900, 0x4A924310, 0x46106110,
        0x15926900, 0x4A8F4390, 0x20006110, 0x20014770, 0x498C06C0, 0x46086148, 0x211468C0, 0x49894308,
        0x460860C8, 0x21046900, 0x49864308, 0x46086108, 0x21406900, 0x49834308, 0xE0026108, 0x49844886,
        0x48806008, 0x07C068C0, 0x28000FC0, 0x487DD1F6, 0x21046900, 0x497B4388, 0x46086108, 0x211468C0,
        0x28004008, 0x4877D006, 0x430868C0, 0x60C84975, 0x47702001, 0xE7FC2000, 0x48724601, 0x68C06141,
        0x43102214, 0x60D04A6F, 0x6090486D, 0x6090486E, 0x69004610, 0x43102220, 0x61104A6A, 0x69004610,
        0x43102240, 0x61104A67, 0x486BE002, 0x60104A68, 0x68C04864, 0x0FC007C0, 0xD1F62800, 0x69004861,
        0x43902220, 0x61104A5F, 0x68C04610, 0x40102214, 0xD0062800, 0x68C0485B, 0x4A5A4310, 0x200160D0,
        0x20004770, 0xB500E7FC, 0xFF5AF7FF, 0xF7FF485B, 0x4854FFC3, 0x495A6900, 0x49524008, 0x46086108,
        0x21106900, 0x494F4308, 0x48566108, 0x80084953, 0x4851E002, 0x6008494E, 0x68C0484A, 0x0FC007C0,
        0xD1F62800, 0x69004847, 0x43882110, 0x61084945, 0x68C04608, 0x40082114, 0xD0062800, 0x68C04841,
        0x49404308, 0x200160C8, 0x2000BD00, 0xB500E7FC, 0xFFC9F7FF, 0xFF5BF7FF, 0xF7FF4843, 0x2000FF8D,
        0x4601BD00, 0x68C04837, 0x43102214, 0x60D04A35, 0x69004610, 0x43102202, 0x61104A32, 0x61414610,
        0x22406900, 0x4A2F4310, 0xE0026110, 0x4A304832, 0x482C6010, 0x07C068C0, 0x28000FC0, 0x4829D1F6,
        0x22026900, 0x4A274390, 0x46106110, 0x221468C0, 0x28004010, 0x4823D006, 0x431068C0, 0x60D04A21,
        0x47702001, 0xE7FC2000, 0x20014603, 0xB5104770, 0x1C484603, 0x00490841, 0x68C0481A, 0x43202404,
        0x60E04C18, 0x4817E027, 0x24016900, 0x4C154320, 0x88106120, 0xE0028018, 0x4C154817, 0x48116020,
        0x07C068C0, 0x28000FC0, 0x480ED1F6, 0x08406900, 0x4C0C0040, 0x46206120, 0x241468C0, 0x28004020,
        0x4808D006, 0x432068C0, 0x60E04C06, 0xBD102001, 0x1C921C9B, 0x29001E89, 0x2000D1D5, 0x0000E7F7,
        0x45670123, 0x40022000, 0xCDEF89AB, 0x00005555, 0x40003000, 0x00000FFF, 0x0000AAAA, 0x1FFFF800,
        0x00001FEF, 0x00005AA5, 0x1FFE0000, 0x00000000
    ],

    'pc_Init'            : 0x2000002D,
    'pc_UnInit'          : 0x20000071,
    'pc_EraseSector'     : 0x200001E3,
    'pc_ProgramPage'     : 0x2000024F,
    'pc_Verify'          : 0x12000001F,
    'pc_EraseChip'       : 0x200001CF,
    'pc_BlankCheck'      : 0x20000249,
    'pc_Read'            : 0x12000001F,
    
    'static_base'        : 0x20000400,
    'begin_data'         : 0x20000800,
    'begin_stack'        : 0x20001000,

    'analyzer_supported' : False,

    # Relative region addresses and sizes
    'ro_start'           : 0x00000000,
    'ro_size'            : 0x000002CC,
    'rw_start'           : 0x000002CC,
    'rw_size'            : 0x00000004,
    'zi_start'           : 0x000002D0,
    'zi_size'            : 0x00000000,

    # Flash information
    'flash_start'        : 0x08000000,
    'flash_size'         : 0x00020000,
    'flash_page_size'    : 0x00000400,
    'sector_sizes': (
        (0x00000, 0x00400),
    )
}
