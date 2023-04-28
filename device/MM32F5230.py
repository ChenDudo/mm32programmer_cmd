"""
 Flash OS Routines (Automagically Generated)
 Copyright (c) 2017-2017 ARM Limited
"""
from .flash import Flash

"""
 Flash OS Routines (Automagically Generated)
 Copyright (c) 2017-2017 ARM Limited
"""
class MM32F5230(object):
    CHIP_CORE = 'STAR-MC1'

    PAGE_SIZE = 1024 * 1
    SECT_SIZE = 1024 * 1
    CHIP_SIZE = 1024 * 256

    def __init__(self, xlink):
        super(MM32F5230, self).__init__()

        self.xlink = xlink

        self.flash = Flash(self.xlink, MM32F5230_flash_algo)

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

class MM32F5280(MM32F5230):
    PAGE_SIZE = 1024 * 1
    SECT_SIZE = 1024 * 1
    CHIP_SIZE = 1024 * 256

    def __init__(self, xlink):
        super().__init__(xlink)

        self.flash = Flash(self.xlink, MM32F5230_flash_algo)


MM32F5230_flash_algo = {
    'load_address' : 0x20000000,
    'instructions' : [
        0xE00ABE00, 0x062D780D, 0x24084068, 0xD3000040, 0x1E644058, 0x1C49D1FA, 0x2A001E52, 0x4770D1F2,
        0x47702001, 0x000CF242, 0x1123F240, 0x13ABF648, 0x0C00F64F, 0x0002F2C4, 0x5167F2C4, 0x53EFF6CC,
        0x7CFFF6C1, 0x1C08F840, 0x3C08F840, 0xC008F8C0, 0xF0426802, 0x60020214, 0x1C04F840, 0x3C04F840,
        0xF0416841, 0x60410120, 0xF0416841, 0x60410140, 0x07C96801, 0x0100F243, 0x0100F2C4, 0x6842D12A,
        0x0220F022, 0x68026042, 0x0F14F012, 0x6802BF1E, 0x0214F042, 0x68426002, 0x7280F442, 0x68426042,
        0x0210F042, 0xF6456042, 0xF8AC22A5, 0x68022000, 0xD12307D2, 0xF0216841, 0x60410110, 0xF0116801,
        0xBF0F0F14, 0x68012000, 0x0114F041, 0xBF186001, 0x47702001, 0x23AAF64A, 0x6802600B, 0xD0CE07D2,
        0x6802600B, 0xBF1E07D2, 0x6802600B, 0x72C2EA5F, 0x600BD0C5, 0x07D26802, 0xE7C0D1EE, 0x22AAF64A,
        0x6803600A, 0xD0D507DB, 0x6803600A, 0xBF1E07DB, 0x6803600A, 0x73C3EA5F, 0x600AD0CC, 0x07DB6803,
        0xE7C7D1EE, 0xF7FFB580, 0xF242FF7D, 0xF04F000C, 0xF2C46100, 0x60810002, 0xF0416801, 0x60010114,
        0xF0416841, 0x60410104, 0xF0416841, 0x60410140, 0x07C96801, 0x6841D10D, 0x0104F021, 0x68016041,
        0x0F14F011, 0x6801BF1E, 0x0114F041, 0x20006001, 0xF243BD80, 0xF64A0100, 0xF2C422AA, 0x600A0100,
        0x07DB6803, 0x600AD0E7, 0x07DB6803, 0x600ABF1E, 0xEA5F6803, 0xD0DE73C3, 0x6803600A, 0xD1EE07DB,
        0x0000E7D9, 0x010CF242, 0x0102F2C4, 0xF042680A, 0x600A0214, 0xF042684A, 0x604A0202, 0x68486088,
        0x0040F040, 0x68086048, 0xD10F07C0, 0xF0206848, 0x60480002, 0xF0106808, 0xBF0F0F14, 0x68082000,
        0x0014F040, 0xBF186008, 0x47702001, 0x0000F243, 0x22AAF64A, 0x0000F2C4, 0x680B6002, 0xD0E507DB,
        0x680B6002, 0xBF1E07DB, 0x680B6002, 0x73C3EA5F, 0x6002D0DC, 0x07DB680B, 0xE7D7D1EE, 0x000CF242,
        0x6100F04F, 0x0002F2C4, 0x68016081, 0x0114F041, 0x68416001, 0x0104F041, 0x68416041, 0x0140F041,
        0x68016041, 0xD10F07C9, 0xF0216841, 0x60410104, 0xF0116801, 0xBF0F0F14, 0x68012000, 0x0114F041,
        0xBF186001, 0x47702001, 0x0100F243, 0x22AAF64A, 0x0100F2C4, 0x6803600A, 0xD0E507DB, 0x6803600A,
        0xBF1E07DB, 0x6803600A, 0x73C3EA5F, 0x600AD0DC, 0x07DB6803, 0xE7D7D1EE, 0x010CF242, 0x0102F2C4,
        0x68086088, 0x0014F040, 0xF2406008, 0xF2C41023, 0xF8415067, 0xF6480C04, 0xF6CC10AB, 0xF84150EF,
        0x68480C04, 0x0020F040, 0x68486048, 0x0040F040, 0x68086048, 0xD10F07C0, 0xF0206848, 0x60480020,
        0xF0106808, 0xBF0F0F14, 0x68082000, 0x0014F040, 0xBF186008, 0x47702001, 0x0000F243, 0x22AAF64A,
        0x0000F2C4, 0x680B6002, 0xD0E507DB, 0x680B6002, 0xBF1E07DB, 0x680B6002, 0x73C3EA5F, 0x6002D0DC,
        0x07DB680B, 0xE7D7D1EE, 0x0004F242, 0x1123F240, 0x0002F2C4, 0x5167F2C4, 0xF6486001, 0xF6CC11AB,
        0x600151EF, 0x00004770, 0x0004F242, 0x1123F240, 0x12ABF648, 0x0002F2C4, 0x5167F2C4, 0x52EFF6CC,
        0x60026001, 0x21006041, 0xF8406042, 0x68811C04, 0x0114F041, 0x69806081, 0xD40B0740, 0x0000F243,
        0x5155F245, 0x0000F2C4, 0x21066001, 0xF6406041, 0x608171FF, 0x47702000, 0xF242B5B0, 0x3101040C,
        0x0402F2C4, 0x0C01F021, 0xF1BC6823, 0xF0430F00, 0x60230304, 0xF243D033, 0xF64A0E00, 0xF2C421AA,
        0xBF000E00, 0x88156863, 0x0301F043, 0x80056063, 0x07DB6823, 0xF8CEBF1E, 0x68231000, 0x73C3EA5F,
        0xF8CED00E, 0x68231000, 0xBF1E07DB, 0x1000F8CE, 0xEA5F6823, 0xD00373C3, 0x1000F8CE, 0xBF00E7E8,
        0xF0236863, 0x60630301, 0xF0136823, 0xD1080F14, 0x0C02F1BC, 0x0202F102, 0x0002F100, 0x2000D1D2,
        0x6820BDB0, 0x0014F040, 0x20016020, 0x0000BDB0, 0x0010F242, 0x0002F2C4, 0xF0416801, 0x60010180,
        0xF4216801, 0x60017180, 0x47702000, 0x00000000
    ],

    'pc_Init'            : 0x20000349,
    'pc_UnInit'          : 0x20000431,
    'pc_EraseSector'     : 0x200001A5,
    'pc_ProgramPage'     : 0x20000399,
    'pc_Verify'          : 0x12000001F,
    'pc_EraseChip'       : 0x20000125,
    'pc_BlankCheck'      : 0x20000021,
    'pc_Read'            : 0x12000001F,
    
    'static_base'        : 0x20000800,
    'begin_data'         : 0x20000C00,
    'begin_stack'        : 0x20001400,

    'analyzer_supported' : False,

    # Relative region addresses and sizes
    'ro_start'           : 0x00000000,
    'ro_size'            : 0x0000042C,
    'rw_start'           : 0x0000042C,
    'rw_size'            : 0x00000004,
    'zi_start'           : 0x00000430,
    'zi_size'            : 0x00000000,

    # Flash information
    'flash_start'        : 0x08000000,
    'flash_size'         : 0x00020000,
    'flash_page_size'    : 0x00000400,
    'sector_sizes': (
        (0x00000, 0x00400),
    )
}
