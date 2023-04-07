"""
 Flash OS Routines (Automagically Generated)
 Copyright (c) 2017-2017 ARM Limited
"""
from .flash import Flash

"""
 Flash OS Routines (Automagically Generated)
 Copyright (c) 2017-2017 ARM Limited
"""
class MM32L0020(object):
    CHIP_CORE = 'Cortex-M0+'

    PAGE_SIZE = 1024 * 1
    SECT_SIZE = 1024 * 1
    CHIP_SIZE = 1024 * 32

    def __init__(self, xlink):
        super(MM32L0020, self).__init__()

        self.xlink = xlink

        self.flash = Flash(self.xlink, MM32L0020_flash_algo)

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

MM32L0020_flash_algo = {
    'load_address' : 0x20000000,
    'instructions' : [
        0xE00ABE00, 0x062D780D, 0x24084068, 0xD3000040, 0x1E644058, 0x1C49D1FA, 0x2A001E52, 0x4770D1F2,
        0x49764877, 0x49776041, 0x47706041, 0x4A734874, 0x49746042, 0x60826041, 0x21006081, 0x68C16001,
        0x43112214, 0x69C060C1, 0xD4060740, 0x496E486F, 0x21066001, 0x496E6041, 0x20006081, 0x48684770,
        0x22806901, 0x61014311, 0x15826901, 0x61014391, 0x47702000, 0x2101B530, 0x06C94861, 0x68C16141,
        0x43212414, 0x690160C1, 0x43292504, 0x69016101, 0x43112240, 0x495F6101, 0xE0004A5C, 0x68C36011,
        0xD1FB07DB, 0x43A96901, 0x68C16101, 0xD0044221, 0x432168C1, 0x200160C1, 0x2000BD30, 0xB530BD30,
        0x6148494F, 0x231468C8, 0x60C84318, 0x6088484B, 0x6088484C, 0x24206908, 0x61084320, 0x22406908,
        0x61084310, 0x4A49484B, 0x6010E000, 0x07ED68CD, 0x6908D1FB, 0x610843A0, 0x401868C8, 0x68C8D003,
        0x60C84318, 0xBD302001, 0xF7FFB530, 0x4D42FF89, 0xF7FF4628, 0x493AFFD4, 0x158A6908, 0x61084310,
        0x24106908, 0x61084320, 0x8028483C, 0x4A374839, 0x6010E000, 0x07DB68CB, 0x6908D1FB, 0x610843A0,
        0x221468C8, 0xD0034010, 0x431068C8, 0x200160C8, 0xB500BD30, 0xFFD8F7FF, 0xFF8CF7FF, 0xBD002000,
        0x4927B530, 0x231468CA, 0x60CA431A, 0x2402690A, 0x610A4322, 0x69086148, 0x43102240, 0x48256108,
        0xE0004A22, 0x68CD6010, 0xD1FB07ED, 0x43A06908, 0x68C86108, 0xD0034018, 0x431868C8, 0x200160C8,
        0x2001BD30, 0xB5F04770, 0x1C494D15, 0x68EB0849, 0x24040049, 0x60EB4323, 0x4C162714, 0x692BE01A,
        0x43332601, 0x8813612B, 0x4B108003, 0x601CE000, 0x07F668EE, 0x692BD1FB, 0x005B085B, 0x68EB612B,
        0xD004423B, 0x433868E8, 0x200160E8, 0x1C80BDF0, 0x1C921E89, 0xD1E22900, 0xBDF02000, 0x45670123,
        0x40022000, 0xCDEF89AB, 0x00005555, 0x40003000, 0x00000FFF, 0x0000AAAA, 0x1FFFF800, 0x00005AA5,
        0x00000000
    ],

    'pc_Init'            : 0x2000002D,
    'pc_UnInit'          : 0x2000005F,
    'pc_EraseSector'     : 0x20000161,
    'pc_ProgramPage'     : 0x200001A7,
    'pc_Verify'          : 0x12000001F,
    'pc_EraseChip'       : 0x20000153,
    'pc_BlankCheck'      : 0x200001A3,
    'pc_Read'            : 0x12000001F,
    
    'static_base'        : 0x20000400,
    'begin_data'         : 0x20000800,
    'begin_stack'        : 0x20001000,

    'analyzer_supported' : False,

    # Relative region addresses and sizes
    'ro_start'           : 0x00000000,
    'ro_size'            : 0x00000200,
    'rw_start'           : 0x00000200,
    'rw_size'            : 0x00000004,
    'zi_start'           : 0x00000204,
    'zi_size'            : 0x00000000,

    # Flash information
    'flash_start'        : 0x08000000,
    'flash_size'         : 0x00008000,
    'flash_page_size'    : 0x00000400,
    'sector_sizes': (
        (0x00000, 0x00400),
    )
}
