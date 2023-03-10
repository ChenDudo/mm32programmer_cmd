import collections

from . import MM32
from . import MM32F0010
from . import MM32F0020
from . import MM32F0x40
from . import MM32F3270
from . import MM32F5270
from . import MM32F003
from . import MM32F103

Devices = collections.OrderedDict([
    ('MM32F0010',    MM32F0010.MM32F0010),
    ('MM32F0020',    MM32F0020.MM32F0020),
    ('MM32F0040',    MM32F0x40.MM32F0040),
    ('MM32F0130',    MM32F0x40.MM32F0140),
    ('MM32F0140',    MM32F0x40.MM32F0140),
    ('MM32F0160',    MM32F0x40.MM32F0140),
    ('MM32G0140',    MM32F0x40.MM32F0140),
    ('MM32A0140',    MM32F0x40.MM32F0140),
    ('MM32F003',     MM32F003.MM32F003),
    ('MM32L07x',     MM32F0x40.MM32F0140),
    ('MM32F03x',     MM32F0x40.MM32F0140),
    ('MM32L0130',    MM32F0x40.MM32F0140),
    ('MM32L0160',    MM32F0x40.MM32F0140),
    ('MM32SPIN05',   MM32F0x40.MM32F0140),
    ('MM32SPIN06',   MM32F0x40.MM32F0140),
    ('MM32SPIN07',   MM32F0x40.MM32F0140),
    ('MM32SPIN08',   MM32F0x40.MM32F0140),
    ('MM32SPIN0280', MM32F0x40.MM32F0140),
    ('MM32F103C8',   MM32F103.MM32F103C8),
    ('MM32F103CB',   MM32F103.MM32F103CB),
    ('MM32L3xx',     MM32F103.MM32F103CB),
    ('MM32F3270',    MM32F3270.MM32F3270),
    ('MM32F5270',    MM32F5270.MM32F5270),
    ('MM32F5280',    MM32F5270.MM32F5270),
    ('MM32',         MM32.MM32),
    # ('STM32F103C8',    STM32F103.STM32F103C8),
    # ('STM32F103C8-LS', STM32F103_LS.STM32F103C8),
    # ('STM32F103RC',    STM32F103.STM32F103RC),
   	# ('STM32F103RC-LS', STM32F103_LS.STM32F103RC),
])
