import collections

from . import MM32
from . import MM32A0140
from . import MM32F003
from . import MM32F0010
from . import MM32F0020
from . import MM32F0040
from . import MM32F103
from . import MM32F0130
from . import MM32F0160
from . import MM32F0270
from . import MM32F3270
from . import MM32F5230
from . import MM32F5270
from . import MM32F5280
from . import MM32F5330
from . import MM32G0001
from . import MM32G0140
from . import MM32G0160
from . import MM32G5330
from . import MM32L0020
from . import MM32L0130
from . import MM32SPIN0230

Devices = collections.OrderedDict([
    # Old Chip
    ('MM32F003',     MM32F003.MM32F003),
    ('MM32F031Q',    MM32F0040.MM32F0140),
    ('MM32F103C8',   MM32F103.MM32F103C8),
    ('MM32F103CB',   MM32F103.MM32F103CB),
    ('MM32L073',     MM32F0040.MM32F0140),
    # New Chip
    ('MM32A0140',    MM32A0140.MM32A0140),
    ('MM32F0010',    MM32F0010.MM32F0010),
    ('MM32F0020',    MM32F0020.MM32F0020),
    ('MM32F0040',    MM32F0040.MM32F0040),
    ('MM32F0130',    MM32F0130.MM32F0130),
    ('MM32F0140',    MM32F0040.MM32F0140),
    ('MM32F0160',    MM32F0160.MM32F0160),
    ('MM32F0270',    MM32F0270.MM32F0270),
    ('MM32F3270',    MM32F3270.MM32F3270),
    ('MM32F5230',    MM32F5230.MM32F5230),
    ('MM32F5270',    MM32F5270.MM32F5270),
    ('MM32F5280',    MM32F5280.MM32F5280),
    ('MM32F5330',    MM32F5330.MM32F5330),
    ('MM32G0001',    MM32G0001.MM32G0001),
    ('MM32G0140',    MM32G0140.MM32G0140),
    ('MM32G0160',    MM32G0160.MM32G0160),
    ('MM32G5330',    MM32G5330.MM32G5330),
    ('MM32L0020',    MM32L0020.MM32L0020),
    ('MM32L0130',    MM32L0130.MM32L0130),
    # SPIN Special
    ('MM32SPIN05',   MM32F0040.MM32F0140),
    ('MM32SPIN06',   MM32F0040.MM32F0140),
    ('MM32SPIN07',   MM32F0040.MM32F0140),
    ('MM32SPIN0230', MM32SPIN0230.MM32SPIN0230),
    ('MM32SPIN0280', MM32F0040.MM32F0140),
    ('MM32SPIN2x',   MM32F0040.MM32F0140),
    # Pre-DRV
    ('MM32SPIN040',  MM32F0040.MM32F0140),
    ('MM32SPIN120',  MM32F0040.MM32F0140),
    ('MM32SPIN160',  MM32F0040.MM32F0140),
    ('MM32SPIN360',  MM32F0040.MM32F0140),
    ('MM32SPIN560',  MM32F0040.MM32F0140),
    ('MM32SPIN580',  MM32F0040.MM32F0140),
    ('MM32SPIN320',  MM32F0040.MM32F0140),
    ('MM32SPIN380',  MM32F0040.MM32F0140),
    # DRV
    ('MM32SPIN222',  MM32F0040.MM32F0140),
    ('MM32SPIN223',  MM32F0040.MM32F0140),
    ('MM32SPIN422',  MM32F0040.MM32F0140),
    # test
    ('MM32',         MM32.MM32),
    # ('STM32F103C8',    STM32F103.STM32F103C8),
    # ('STM32F103C8-LS', STM32F103_LS.STM32F103C8),
    # ('STM32F103RC',    STM32F103.STM32F103RC),
   	# ('STM32F103RC-LS', STM32F103_LS.STM32F103RC),
])
