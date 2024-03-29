"""
 Flash OS Routines (Automagically Generated)
 Copyright (c) 2017-2017 ARM Limited
"""
from .flash import Flash

"""
 Flash OS Routines (Automagically Generated)
 Copyright (c) 2017-2017 ARM Limited
"""
class MM32F003(object):
    CHIP_CORE = 'Cortex-M0'

    PAGE_SIZE = 1024 * 1 // 2
    SECT_SIZE = 1024 * 1
    CHIP_SIZE = 1024 * 16

    def __init__(self, xlink):
        super(MM32F003, self).__init__()

        self.xlink = xlink

        self.flash = Flash(self.xlink, MM32F003_flash_algo)

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

MM32F003_flash_algo = {
    'load_address' : 0x20000000,
    'instructions' : [
        0xE00ABE00, 0x062D780D, 0x24084068, 0xD3000040, 0x1E644058, 0x1C49D1FA, 0x2A001E52, 0x4770D1F2,
        0x49784879, 0x49796041, 0x47706041, 0x4A754876, 0x49766042, 0x60826041, 0x21006081, 0x68C16001,
        0x43112214, 0x69C060C1, 0xD4060740, 0x49704871, 0x21066001, 0x49706041, 0x20006081, 0x486A4770,
        0x22806901, 0x61014311, 0x15826901, 0x61014391, 0x47702000, 0x2101B530, 0x06C94863, 0x68C16141,
        0x43212414, 0x690160C1, 0x43292504, 0x69016101, 0x43112240, 0x49616101, 0xE0004A5E, 0x68C36011,
        0xD1FB07DB, 0x43A96901, 0x68C16101, 0xD0044221, 0x432168C1, 0x200160C1, 0x2000BD30, 0xB530BD30,
        0x61484951, 0x231468C8, 0x60C84318, 0x6088484D, 0x6088484E, 0x24206908, 0x61084320, 0x22406908,
        0x61084310, 0x4A4B484D, 0x6010E000, 0x07ED68CD, 0x6908D1FB, 0x610843A0, 0x401868C8, 0x68C8D003,
        0x60C84318, 0xBD302001, 0xF7FFB530, 0x4D44FF89, 0xF7FF4628, 0x493CFFD4, 0x4A426908, 0x61084010,
        0x24106908, 0x61084320, 0x8028483F, 0x4A39483B, 0x6010E000, 0x07DB68CB, 0x6908D1FB, 0x610843A0,
        0x221468C8, 0xD0034010, 0x431068C8, 0x200160C8, 0xB500BD30, 0xFFD8F7FF, 0xFF8CF7FF, 0xF7FF4833,
        0x2000FFAE, 0xB530BD00, 0x68CA4927, 0x431A2314, 0x690A60CA, 0x43222402, 0x6148610A, 0x22406908,
        0x61084310, 0x4A234825, 0x6010E000, 0x07ED68CD, 0x6908D1FB, 0x610843A0, 0x401868C8, 0x68C8D003,
        0x60C84318, 0xBD302001, 0x47702001, 0x4D16B5F0, 0x08491C49, 0x004968EB, 0x43232404, 0x271460EB,
        0xE01A4C16, 0x2601692B, 0x612B4333, 0x80038813, 0xE0004B10, 0x68EE601C, 0xD1FB07F6, 0x085B692B,
        0x612B005B, 0x423B68EB, 0x68E8D004, 0x60E84338, 0xBDF02001, 0x1E891C80, 0x29001C92, 0x2000D1E2,
        0x0000BDF0, 0x45670123, 0x40022000, 0xCDEF89AB, 0x00005555, 0x40003000, 0x00000FFF, 0x0000AAAA,
        0x1FFFF800, 0x00001FEF, 0x00005AA5, 0x1FFE0000, 0x00000000
    ],

    'pc_Init'            : 0x2000002D,
    'pc_UnInit'          : 0x2000005F,
    'pc_EraseSector'     : 0x20000167,
    'pc_ProgramPage'     : 0x200001AD,
    'pc_Verify'          : 0x12000001F,
    'pc_EraseChip'       : 0x20000153,
    'pc_BlankCheck'      : 0x200001A9,
    'pc_Read'            : 0x12000001F,
    
    'static_base'        : 0x20000400,
    'begin_data'         : 0x20000800,
    'begin_stack'        : 0x20001000,

    'analyzer_supported' : False,

    # Relative region addresses and sizes
    'ro_start'           : 0x00000000,
    'ro_size'            : 0x00000210,
    'rw_start'           : 0x00000210,
    'rw_size'            : 0x00000004,
    'zi_start'           : 0x00000214,
    'zi_size'            : 0x00000000,

    # Flash information
    'flash_start'        : 0x08000000,
    'flash_size'         : 0x00004000,
    'flash_page_size'    : 0x00000400,
    'sector_sizes': (
        (0x00000, 0x00400),
    )
}
