"""
 Flash OS Routines (Automagically Generated)
 Copyright (c) 2017-2017 ARM Limited
"""
from .flash import Flash

"""
 Flash OS Routines (Automagically Generated)
 Copyright (c) 2017-2017 ARM Limited
"""
class MM32F0160(object):
    CHIP_CORE = 'Cortex-M0'

    PAGE_SIZE = 1024 * 1
    SECT_SIZE = 1024 * 1
    CHIP_SIZE = 1024 * 128

    def __init__(self, xlink):
        super(MM32F0160, self).__init__()

        self.xlink = xlink

        self.flash = Flash(self.xlink, MM32F0160_flash_algo)

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

MM32F0160_flash_algo = {
    'load_address' : 0x20000000,
    'instructions' : [
        0xE00ABE00, 0x062D780D, 0x24084068, 0xD3000040, 0x1E644058, 0x1C49D1FA, 0x2A001E52, 0x4770D1F2,
        0x49034802, 0x49036001, 0x47706001, 0x40022004, 0x45670123, 0xCDEF89AB, 0x490D480C, 0x4A0D6001,
        0x60416002, 0x1F016042, 0x600A2200, 0x22146881, 0x6082430A, 0x07406980, 0x4807D406, 0x60014907,
        0x60412106, 0x60814906, 0x47702000, 0x40022004, 0x45670123, 0xCDEF89AB, 0x40003000, 0x00005555,
        0x00000FFF, 0x68014805, 0x430A2280, 0x21016002, 0x68020209, 0x6002438A, 0x47702000, 0x40022010,
        0x2001B570, 0x491806C2, 0x680B608A, 0x43132214, 0x684C600B, 0x431C2304, 0x684C604C, 0x43252540,
        0x680C604D, 0xD10907E4, 0x439C684C, 0x680B604C, 0xD0164213, 0x4313680B, 0xBD70600B, 0x4D0C4C0B,
        0x680E602C, 0xD0EF07F6, 0x680E602C, 0xD0EB07F6, 0x680E602C, 0xD0E707F6, 0x680E602C, 0xD1EF07F6,
        0x2000E7E2, 0x46C0BD70, 0x4002200C, 0x0000AAAA, 0x40003000, 0x491BB5B0, 0x680A6088, 0x43022014,
        0x1F0A600A, 0x60134B18, 0x60134B18, 0x2220684B, 0x604B4313, 0x2440684B, 0x604C431C, 0x07DB680B,
        0x684BD10A, 0x604B4393, 0x4202680A, 0x680AD017, 0x600A4302, 0xBDB02001, 0x4C0E4B0D, 0x680D6023,
        0xD0EE07ED, 0x680D6023, 0xD0EA07ED, 0x680D6023, 0xD0E607ED, 0x680D6023, 0xD1EF07ED, 0x2000E7E1,
        0x46C0BDB0, 0x4002200C, 0x45670123, 0xCDEF89AB, 0x0000AAAA, 0x40003000, 0x492FB5F0, 0x38084608,
        0x60034B2E, 0x60044C2E, 0x608D4D2E, 0x22146808, 0x60084310, 0x60031F08, 0x684B6004, 0x43032020,
        0x684B604B, 0x431C2440, 0x680B604C, 0x4B2607DB, 0xD1244C26, 0x4386684E, 0x6808604E, 0xD0024210,
        0x43106808, 0x20016008, 0x684F0206, 0x604F4337, 0x2610684F, 0x604F4337, 0x802F4F1D, 0x07ED680D,
        0x6023D01E, 0x07ED680D, 0x6023D01A, 0x07ED680D, 0x6023D016, 0x07ED680D, 0x6023D012, 0x6023E7EE,
        0x07F6680E, 0x6023D0D6, 0x07F6680E, 0x6023D0D2, 0x07F6680E, 0x6023D0CE, 0x07F6680E, 0xE7C9D1EF,
        0x43B3684B, 0x680B604B, 0xD0034213, 0x4313680B, 0xBDF0600B, 0xBDF02000, 0x4002200C, 0x45670123,
        0xCDEF89AB, 0x1FFFF800, 0x0000AAAA, 0x40003000, 0x00005AA5, 0xF7FFB5B0, 0x2001FF8F, 0x481706C1,
        0x68026081, 0x430A2114, 0x68436002, 0x43132204, 0x68436043, 0x431C2440, 0x68036044, 0xD10A07DB,
        0x43936843, 0x68026043, 0xD002420A, 0x430A6802, 0x20006002, 0x4B0ABDB0, 0x60234C0A, 0x07ED6805,
        0x6023D0EE, 0x07ED6805, 0x6023D0EA, 0x07ED6805, 0x6023D0E6, 0x07ED6805, 0xE7E1D1EF, 0x4002200C,
        0x0000AAAA, 0x40003000, 0x4918B5B0, 0x2214680B, 0x600B4313, 0x2302684C, 0x604C431C, 0x68486088,
        0x43042440, 0x6808604C, 0xD10A07C0, 0x43986848, 0x68086048, 0xD0174210, 0x43106808, 0x20016008,
        0x480BBDB0, 0x60204C0B, 0x07ED680D, 0x6020D0EE, 0x07ED680D, 0x6020D0EA, 0x07ED680D, 0x6020D0E6,
        0x07ED680D, 0xE7E1D1EF, 0xBDB02000, 0x4002200C, 0x0000AAAA, 0x40003000, 0x47702001, 0xB084B5F0,
        0x68234C20, 0x431D2504, 0x1C4D6025, 0x438D2101, 0x2D002300, 0x9300D032, 0x4F1C4E1B, 0x68659501,
        0x6065430D, 0x88159203, 0x80059002, 0x07ED6825, 0x603ED00D, 0x07ED6825, 0x603ED009, 0x07ED6825,
        0x603ED005, 0x07ED6825, 0x603ED001, 0x6865E7EE, 0x438D460B, 0x68216065, 0x42292514, 0x9D01D10B,
        0x9A031EAD, 0x98021C92, 0x2D001C80, 0xD1D54619, 0xB0049800, 0x6820BDF0, 0x60204328, 0xB0044618,
        0x46C0BDF0, 0x4002200C, 0x0000AAAA, 0x40003000, 0x00000000
    ],

    'pc_Init'            : 0x20000039,
    'pc_UnInit'          : 0x20000085,
    'pc_EraseSector'     : 0x200002E9,
    'pc_ProgramPage'     : 0x2000035D,
    'pc_Verify'          : 0x12000001F,
    'pc_EraseChip'       : 0x20000275,
    'pc_BlankCheck'      : 0x20000359,
    'pc_Read'            : 0x12000001F,
    
    'static_base'        : 0x20000400,
    'begin_data'         : 0x20000800,
    'begin_stack'        : 0x20001000,

    'analyzer_supported' : False,

    # Relative region addresses and sizes
    'ro_start'           : 0x00000000,
    'ro_size'            : 0x000003D0,
    'rw_start'           : 0x000003D0,
    'rw_size'            : 0x00000004,
    'zi_start'           : 0x000003D4,
    'zi_size'            : 0x00000000,

    # Flash information
    'flash_start'        : 0x08000000,
    'flash_size'         : 0x00020000,
    'flash_page_size'    : 0x00000400,
    'sector_sizes': (
        (0x00000, 0x00400),
    )
}
