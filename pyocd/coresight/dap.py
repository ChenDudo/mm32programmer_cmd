# pyOCD debugger
# Copyright (c) 2015-2018 Arm Limited
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ..core import exceptions
from ..probe.debug_probe import DebugProbe
from .ap import (MEM_AP_CSW, LOG_DAP, APSEL, APBANKSEL, APREG_MASK, AccessPort)
from ..utility.sequencer import CallSequence
import logging
import logging.handlers
import os
import os.path
import six

import time

# DP register addresses.
DP_IDCODE = 0x0 # read-only
DP_ABORT = 0x0 # write-only
DP_CTRL_STAT = 0x4 # read-write
DP_SELECT = 0x8 # write-only
DP_RDBUFF = 0xC # read-only

ABORT_DAPABORT = 0x00000001
ABORT_STKCMPCLR = 0x00000002
ABORT_STKERRCLR = 0x00000004
ABORT_WDERRCLR = 0x00000008
ABORT_ORUNERRCLR = 0x00000010

# DP Control / Status Register bit definitions
CTRLSTAT_ORUNDETECT = 0x00000001
CTRLSTAT_STICKYORUN = 0x00000002
CTRLSTAT_STICKYCMP = 0x00000010
CTRLSTAT_STICKYERR = 0x00000020
CTRLSTAT_READOK = 0x00000040
CTRLSTAT_WDATAERR = 0x00000080

DPIDR_MIN_MASK = 0x10000
DPIDR_VERSION_MASK = 0xf000
DPIDR_VERSION_SHIFT = 12

CSYSPWRUPACK = 0x80000000
CDBGPWRUPACK = 0x20000000
CSYSPWRUPREQ = 0x40000000
CDBGPWRUPREQ = 0x10000000

TRNNORMAL = 0x00000000
MASKLANE = 0x00000f00

class Pin:
    NONE = 0x00 # Used to read current pin values without changing.
    SWCLK_TCK = (1 << 0)
    SWDIO_TMS = (1 << 1)
    TDI = (1 << 2)
    TDO = (1 << 3)
    nTRST = (1 << 5)
    nRESET = (1 << 7)

class DebugPort(object):
    # DAP log file name.
    DAP_LOG_FILE = "pyocd_dap.log"

    # Reset_Pin_Set = 1

    def __init__(self, link, target):
        self.link = link
        self.target = target
        self.valid_aps = None
        self.aps = {}
        self._access_number = 0
        if LOG_DAP:
            self._setup_logging()

        self.Reset_Pin_Set = 1

    @property
    def next_access_number(self):
        self._access_number += 1
        return self._access_number

    ## @brief Set up DAP logging.
    #
    # A memory handler is created that buffers log records before flushing them to a file
    # handler that writes to DAP_LOG_FILE. This improves logging performance by writing to the
    # log file less often.
    def _setup_logging(self):
        cwd = os.getcwd()
        logfile = os.path.join(cwd, self.DAP_LOG_FILE)
        logging.info("dap logfile: %s", logfile)
        self.logger = logging.getLogger('dap')
        self.logger.propagate = False
        formatter = logging.Formatter('%(relativeCreated)010dms:%(levelname)s:%(name)s:%(message)s')
        fileHandler = logging.FileHandler(logfile, mode='w+', delay=True)
        fileHandler.setFormatter(formatter)
        memHandler = logging.handlers.MemoryHandler(capacity=128, target=fileHandler)
        self.logger.addHandler(memHandler)
        self.logger.setLevel(logging.DEBUG)

    def swd_write(self, output, value, nbits):
        """Writes bytes over SWD (Serial Wire Debug).

        Args:
          self (JLink): the ``JLink`` instance
          output (int): the output buffer offset to write to
          value (int): the value to write to the output buffer
          nbits (int): the number of bits needed to represent the ``output`` and
            ``value``

        Returns:
          The bit position of the response in the input buffer.
        """
        ret = 0

        for idx in range(0, nbits):
            out_drive = (output>>idx) & 0x01
            out_value = (value>>idx) & 0x01

            # self.Reset_Pin_Set ^=  1
            
            # pin_value = (Pin.nRESET * self.Reset_Pin_Set) | (Pin.SWDIO_TMS * out_value)
            # pin_drive = (Pin.nRESET | Pin.SWCLK_TCK | (Pin.SWDIO_TMS * out_drive))
            # 
            # self.link._link._protocol.set_swj_pins(pin_value, pin_drive, 0)
            # ret |= self.link._link._protocol.set_swj_pins(pin_value | Pin.SWCLK_TCK, pin_drive, 0)
            # ret <<= 1


            pin_value = (Pin.nRESET * self.Reset_Pin_Set) | (Pin.SWDIO_TMS * out_value)
            pin_drive = (Pin.nRESET | Pin.SWCLK_TCK | (Pin.SWDIO_TMS * out_drive))

            self.link._link._protocol.set_swj_pins((Pin.SWDIO_TMS * out_value) | Pin.nRESET, pin_drive, 0)
            ret |= self.link._link._protocol.set_swj_pins((Pin.SWDIO_TMS * out_value) | Pin.SWCLK_TCK, pin_drive, 0)
            ret <<= 1
        return ret

    def swd_write32(self, out, value):
        return self.swd_write(out, value, 32)

    def set_reset_pin_high(self):
        self.Reset_Pin_Set = 1
        self.link._link._protocol.set_swj_pins(Pin.nRESET | Pin.SWCLK_TCK | Pin.SWDIO_TMS, Pin.nRESET | Pin.SWCLK_TCK | Pin.SWDIO_TMS, 0)

    def set_reset_pin_low(self):
        self.Reset_Pin_Set = 0
        self.link._link._protocol.set_swj_pins(Pin.SWCLK_TCK | Pin.SWDIO_TMS, Pin.nRESET | Pin.SWCLK_TCK | Pin.SWDIO_TMS, 0)

    def sim_halt(self):
        # self.link.connect()
        # try:
        #     self.read_id_code()
        # except Exception as e:
        #     pass
        # self.set_reset_pin_low()
        # self.link.swj_sequence()

        # self.swd_write(0xFFFF, 0x0000, 16)

        self.set_reset_pin_low()
        time.sleep(0.005)
        self.set_reset_pin_high()

        # # # line reset
        # self.swd_write32(0xFFFFFFFF, 0xFFFFFFFF)
        # self.swd_write32(0xFFFFFFFF, 0xFFFFFFFF)
        # self.swd_write(0xFFFF, 0xCE79E, 16)
        # self.swd_write32(0xFFFFFFFF, 0xFFFFFFFF)
        # self.swd_write32(0xFFFFFFFF, 0xFFFFFFFF)
        # self.swd_write(0xFFFF, 0x0000, 2)
        #
        # time.sleep(0.005)

        # read ID
        self.swd_write(0xFF, 0xA5, 8)  # header
        self.swd_write(0x1, 0x0, 1)  # trn
        self.swd_write(0x1, 0x3, 3)  # read ack
        ID = self.swd_write32(0xFFFFFFFF, 0x00000000)  # read data
        self.swd_write(0x1, 0x0, 1)  # read parity
        self.swd_write(0x1, 0x0, 1)  # trn
        self.swd_write(0xFFFF, 0x0000, 2)

        # self.set_reset_pin_low()
        # time.sleep(0.005)
        # self.set_reset_pin_high()

        # write ctrl/stat
        self.swd_write(0xFF, 0xA9, 8)  # header
        self.swd_write(0x1, 0x0, 1)  # trn
        self.swd_write(0x7, 0x7, 3)  # read ack
        self.swd_write(0x1, 0x0, 1)  # trn
        self.swd_write32(0xFFFFFFFF, 0x50000000)  # write data
        self.swd_write(0x1, 0x0, 1)  # parity
        self.swd_write(0x1, 0x0, 1)  # trn
        self.swd_write(0xFFFF, 0x0000, 2)

        # self.set_reset_pin_low()
        # time.sleep(0.005)
        # self.set_reset_pin_high()

        # # write ap4
        # self.swd_write(0xFF, 0x8B, 8)  # header
        # self.swd_write(0x0, 0x0, 1)    # trn
        # self.swd_write(0x0, 0x0, 3)    # read ack
        # self.swd_write(0x0, 0x1, 1)    # trn
        # self.swd_write32(0xFFFFFFFF, 0xE000EDF0) # write data
        # self.swd_write(0x1, 0x1, 1)    # parity
        # self.swd_write(0x1, 0x0, 1)  # trn
        # self.swd_write(0xFFFF, 0x0000, 2)

        # # self.set_reset_pin_low()
        # # # time.sleep(0.005)
        # # self.set_reset_pin_high()


        # # write apc
        # self.swd_write(0xFF, 0xBB, 8)  # header
        # self.swd_write(0x0, 0x0, 1)    # trn
        # self.swd_write(0x0, 0x0, 3)    # read ack
        # self.swd_write(0x0, 0x1, 1)    # trn
        # self.swd_write32(0xFFFFFFFF, 0xA05F0003) # write data
        # self.swd_write(0x1, 0x0, 1)    # parity
        # self.swd_write(0x1, 0x0, 1)  # trn
        # self.swd_write(0xFFFF, 0x0000, 2)

        # self.set_reset_pin_low()
        # # time.sleep(0.005)
        # self.set_reset_pin_high()


        # write select
        self.swd_write(0xFF, 0xB1, 8)  # header
        self.swd_write(0x1, 0x0, 1)  # trn
        self.swd_write(0x7, 0x1, 3)  # read ack
        self.swd_write(0x1, 0x0, 1)  # trn
        self.swd_write32(0xFFFFFFFF, 0x00000000)  # write data
        self.swd_write(0x1, 0x0, 1)  # parity
        self.swd_write(0x1, 0x0, 1)  # trn
        self.swd_write(0xFFFF, 0x0000, 2)

        self.set_reset_pin_low()
        time.sleep(0.005)
        self.set_reset_pin_high()


        # write ap0
        self.swd_write(0xFF, 0xA3, 8)  # header
        self.swd_write(0x1, 0x0, 1)  # trn
        self.swd_write(0x7, 0x1, 3)  # read ack
        self.swd_write(0x1, 0x0, 1)  # trn
        self.swd_write32(0xFFFFFFFF, 0x23000042)  # write data
        # self.swd_write32(0xFFFFFFFF, 0x00000002) # write data
        self.swd_write(0x1, 0x1, 1)  # parity
        self.swd_write(0x1, 0x0, 1)  # trn
        self.swd_write(0xFFFF, 0x0000, 2)

        self.set_reset_pin_low()
        time.sleep(0.005)
        self.set_reset_pin_high()


        # write ap4
        self.swd_write(0xFF, 0x8B, 8)  # header
        self.swd_write(0x1, 0x0, 1)  # trn
        self.swd_write(0x7, 0x1, 3)  # read ack
        self.swd_write(0x1, 0x0, 1)  # trn
        self.swd_write32(0xFFFFFFFF, 0xE000EDF0)  # write data
        self.swd_write(0x1, 0x1, 1)  # parity
        self.swd_write(0x1, 0x0, 1)  # trn
        self.swd_write(0xFFFF, 0x0000, 2)

        self.set_reset_pin_low()
        time.sleep(0.005)
        self.set_reset_pin_high()


        # write apc
        self.swd_write(0xFF, 0xBB, 8)  # header
        self.swd_write(0x1, 0x0, 1)  # trn
        self.swd_write(0x7, 0x1, 3)  # read ack
        self.swd_write(0x1, 0x0, 1)  # trn
        self.swd_write32(0xFFFFFFFF, 0xA05F0007)  # write data
        self.swd_write(0x1, 0x1, 1)  # parity
        self.swd_write(0x1, 0x0, 1)  # trn
        self.swd_write(0xFFFF, 0x0000, 2)

        self.set_reset_pin_low()
        time.sleep(0.005)
        self.set_reset_pin_high()


        # # write apc
        # self.swd_write(0xFF, 0xBB, 8)  # header
        # self.swd_write(0x1, 0x0, 1)  # trn
        # self.swd_write(0x7, 0x1, 3)  # read ack
        # self.swd_write(0x1, 0x0, 1)  # trn
        # self.swd_write32(0xFFFFFFFF, 0xA05F0007)  # write data
        # self.swd_write(0x1, 0x1, 1)  # parity
        # self.swd_write(0x1, 0x0, 1)  # trn
        # self.swd_write(0xFFFF, 0x0000, 2)
        #
        #
        # # write ap4
        # self.swd_write(0xFF, 0x8B, 8)  # header
        # self.swd_write(0x0, 0x0, 1)    # trn
        # self.swd_write(0x0, 0x0, 3)    # read ack
        # self.swd_write(0x0, 0x1, 1)    # trn
        # self.swd_write32(0xFFFFFFFF, 0xE000EDFC) # write data
        # self.swd_write(0x1, 0x1, 1)    # parity
        # self.swd_write(0x1, 0x0, 1)    # trn
        # self.swd_write(0xFFFF, 0x0000, 2)
        #
        # self.set_reset_pin_low()
        # time.sleep(0.005)
        # self.set_reset_pin_high()
        #
        #
        # # write apc
        # self.swd_write(0xFF, 0xBB, 8)  # header
        # self.swd_write(0x0, 0x0, 1)    # trn
        # self.swd_write(0x0, 0x0, 3)    # read ack
        # self.swd_write(0x0, 0x1, 1)    # trn
        # self.swd_write32(0xFFFFFFFF, 0x00000001) # write data
        # self.swd_write(0x1, 0x1, 1)    # parity
        # self.swd_write(0x1, 0x0, 1)    # trn
        # self.swd_write(0xFFFF, 0x0000, 2)
        #
        # self.set_reset_pin_low()
        # time.sleep(0.005)
        # self.set_reset_pin_high()
        #
        #
        # # write ap4
        # self.swd_write(0xFF, 0x8B, 8)  # header
        # self.swd_write(0x0, 0x0, 1)    # trn
        # self.swd_write(0x0, 0x0, 3)    # read ack
        # self.swd_write(0x0, 0x1, 1)    # trn
        # self.swd_write32(0xFFFFFFFF, 0xE000EDF0) # write data
        # self.swd_write(0x1, 0x1, 1)    # parity
        # self.swd_write(0x1, 0x0, 1)    # trn
        # self.swd_write(0xFFFF, 0x0000, 2)
        
        # self.set_reset_pin_low()
        # time.sleep(0.005)
        # self.set_reset_pin_high()



        '''
        MEM_AP_CSW = 0x00

        # AP Control and Status Word definitions
        CSW_SIZE = 0x00000007
        CSW_SIZE8 = 0x00000000
        CSW_SIZE16 = 0x00000001
        CSW_SIZE32 = 0x00000002
        CSW_ADDRINC = 0x00000030
        CSW_NADDRINC = 0x00000000
        CSW_SADDRINC = 0x00000010
        CSW_PADDRINC = 0x00000020
        CSW_DBGSTAT = 0x00000040
        CSW_TINPROG = 0x00000080
        CSW_HPROT = 0x02000000
        CSW_MSTRTYPE = 0x20000000
        CSW_MSTRCORE = 0x00000000
        CSW_MSTRDBG = 0x20000000
        CSW_RESERVED = 0x01000000
        CSW_VALUE = (CSW_RESERVED | CSW_MSTRDBG | CSW_HPROT | CSW_DBGSTAT | CSW_SADDRINC)

        CSW_SIZE = 0x00000007
        CSW_SIZE8 = 0x00000000
        CSW_SIZE16 = 0x00000001
        CSW_SIZE32 = 0x00000002

        # Debug Halting Control and Status Register
        DHCSR = 0xE000EDF0

        DBGKEY = (0xA05F << 16)

        C_DEBUGEN = (1 << 0)
        C_HALT = (1 << 1)
        C_STEP = (1 << 2)
        C_MASKINTS = (1 << 3)
        C_SNAPSTALL = (1 << 5)
        S_REGRDY = (1 << 16)
        S_HALT = (1 << 17)
        S_SLEEP = (1 << 18)
        S_LOCKUP = (1 << 19)
        S_RETIRE_ST = (1 << 24)
        S_RESET_ST = (1 << 25)

        # CMSIS-DAP values
        AP_ACC = 1 << 0
        DP_ACC = 0 << 0
        READ = 1 << 1
        WRITE = 0 << 1
        VALUE_MATCH = 1 << 4
        MATCH_MASK = 1 << 5

        DP_0x0 = 0
        DP_0x4 = 1
        DP_0x8 = 2
        DP_0xC = 3
        AP_0x0 = 4
        AP_0x4 = 5
        AP_0x8 = 6
        AP_0xC = 7

        request = WRITE | AP_ACC | (AP_0x0 % 4) * 4
        self.link._link._write(0, 1, request, [CSW_VALUE | CSW_SIZE32])
        self.link._link.flush_reset()
        # self.link._link.write_reg(MEM_AP_CSW, CSW_VALUE | CSW_SIZE32)
        # self.link._link.write_reg(DHCSR, DBGKEY | C_DEBUGEN | C_HALT)
        # self.write_reg(DP_ABORT, 0x0000001E)
        # self.link._link.flush_reset()


        request = WRITE | AP_ACC | (AP_0x4 % 4) * 4
        self.link._link._write(0, 1, request, [DHCSR])
        self.link._link.flush_reset()
        # self.write_reg(DP_ABORT, 0x0000001E)
        # self.link._link.flush_reset()

        request = WRITE | AP_ACC | (AP_0xC % 4) * 4
        self.link._link._write(0, 1, request, [DBGKEY | C_DEBUGEN | C_HALT])
        self.link._link.flush_reset()
        # self.write_reg(DP_ABORT, 0x0000001E)
        # self.link._link.flush_reset()


        request = WRITE | AP_ACC | (AP_0xC % 4) * 4
        self.link._link._write(0, 1, request, [DBGKEY | C_DEBUGEN | C_HALT])
        self.link._link.flush_reset()
        '''

    def init(self):
        # Connect to the target.
        self.link.connect()
        
        try:
            self.read_id_code()
        except exceptions.TransferError:
            pass
        self.set_reset_pin_low()
        
        self.link.swj_sequence()
        
        self.sim_halt()
            
        try:
            self.read_id_code()
        except exceptions.TransferError:
            # If the read of the DP IDCODE fails, retry SWJ sequence. The DP may have been
            # in a state where it thought the SWJ sequence was an invalid transfer.
            self.set_reset_pin_low()
        
            self.link.swj_sequence()
            
            self.sim_halt()
            
            self.read_id_code()
        self.clear_sticky_err()

    def read_id_code(self):
        # Read ID register and get DP version
        self.dpidr = self.read_reg(DP_IDCODE)
        self.dp_version = (self.dpidr & DPIDR_VERSION_MASK) >> DPIDR_VERSION_SHIFT
        self.is_mindp = (self.dpidr & DPIDR_MIN_MASK) != 0
        logging.info("DP IDR = 0x%08x", self.dpidr)
        return self.dpidr

    def flush(self):
        try:
            self.link.flush()
        except exceptions.ProbeError as error:
            self._handle_error(error, self.next_access_number)
            raise

    def read_reg(self, addr, now=True):
        return self.read_dp(addr, now)

    def write_reg(self, addr, data):
        self.write_dp(addr, data)

    def power_up_debug(self):
        # select bank 0 (to access DRW and TAR)
        self.write_reg(DP_SELECT, 0)
        self.write_reg(DP_CTRL_STAT, CSYSPWRUPREQ | CDBGPWRUPREQ)

        while True:
            r = self.read_reg(DP_CTRL_STAT)
            if (r & (CDBGPWRUPACK | CSYSPWRUPACK)) == (CDBGPWRUPACK | CSYSPWRUPACK):
                break

        self.write_reg(DP_CTRL_STAT, CSYSPWRUPREQ | CDBGPWRUPREQ | TRNNORMAL | MASKLANE)
        self.write_reg(DP_SELECT, 0)

    def power_down_debug(self):
        # select bank 0 (to access DRW and TAR)
        self.write_reg(DP_SELECT, 0)
        self.write_reg(DP_CTRL_STAT, 0)

    def reset(self):
        for ap in self.aps.values():
            ap.reset_did_occur()
        self.link.reset()

    def assert_reset(self, asserted):
        if asserted:
            for ap in self.aps.values():
                ap.reset_did_occur()
        self.link.assert_reset(asserted)

    def is_reset_asserted(self):
        return self.link.is_reset_asserted()

    def set_clock(self, frequency):
        self.link.set_clock(frequency)
        
    ## @brief Find valid APs.
    #
    # Scans for valid APs starting at APSEL=0 and stopping the first time a 0 is returned
    # when reading the AP's IDR.
    #
    # Note that a few MCUs will lock up when accessing invalid APs. Those MCUs will have to
    # modify the init call sequence to substitute a fixed list of valid APs. In fact, that
    # is a major reason this method is separated from create_aps().
    def find_aps(self):
        if self.valid_aps is not None:
            return
        apList = []
        ap_num = 0
        while True:
            try:
                isValid = AccessPort.probe(self, ap_num)
                if not isValid:
                    break
                apList.append(ap_num)
            except Exception as e:
                logging.error("Exception while probing AP#%d: %s", ap_num, repr(e))
                break
            ap_num += 1
        
        # Update the AP list once we know it's complete.
        self.valid_aps = apList

    ## @brief Init task that returns a call sequence to create APs.
    #
    # For each AP in the #valid_aps list, an AccessPort object is created. The new objects
    # are added to the #aps dict, keyed by their AP number.
    def create_aps(self):
        seq = CallSequence()
        for ap_num in self.valid_aps:
            seq.append(
                ('create_ap.{}'.format(ap_num), lambda ap_num=ap_num: self.create_1_ap(ap_num))
                )
        return seq
    
    ## @brief Init task to create a single AP object.
    def create_1_ap(self, ap_num):
        try:
            ap = AccessPort.create(self, ap_num)
            logging.info("AP#%d IDR = 0x%08x", ap_num, ap.idr)
            self.aps[ap_num] = ap
        except Exception as e:
            logging.error("Exception reading AP#%d IDR: %s", ap_num, repr(e))
    
    ## @brief Init task that generates a call sequence to init all AP ROMs.
    def init_ap_roms(self):
        seq = CallSequence()
        for ap in [x for x in self.aps.values() if x.has_rom_table]:
            seq.append(
                ('init_ap.{}'.format(ap.ap_num), ap.init_rom_table)
                )
        return seq

    def read_dp(self, addr, now=True):
        num = self.next_access_number

        try:
            result_cb = self.link.read_dp(addr, now=False)
        except exceptions.ProbeError as error:
            self._handle_error(error, num)
            raise

        # Read callback returned for async reads.
        def read_dp_cb():
            try:
                result = result_cb()
                if LOG_DAP:
                    self.logger.info("read_dp:%06d %s(addr=0x%08x) -> 0x%08x", num, "" if now else "...", addr, result)
                return result
            except exceptions.ProbeError as error:
                self._handle_error(error, num)
                raise

        if now:
            return read_dp_cb()
        else:
            if LOG_DAP:
                self.logger.info("read_dp:%06d (addr=0x%08x) -> ...", num, addr)
            return read_dp_cb

    def write_dp(self, addr, data):
        num = self.next_access_number

        # Write the DP register.
        try:
            if LOG_DAP:
                self.logger.info("write_dp:%06d (addr=0x%08x) = 0x%08x", num, addr, data)
            self.link.write_dp(addr, data)
        except exceptions.ProbeError as error:
            self._handle_error(error, num)
            raise

        return True

    def write_ap(self, addr, data):
        assert type(addr) in (six.integer_types)
        num = self.next_access_number

        try:
            if LOG_DAP:
                self.logger.info("write_ap:%06d (addr=0x%08x) = 0x%08x", num, addr, data)
            self.link.write_ap(addr, data)
        except exceptions.ProbeError as error:
            self._handle_error(error, num)
            raise

        return True

    def read_ap(self, addr, now=True):
        assert type(addr) in (six.integer_types)
        num = self.next_access_number

        try:
            result_cb = self.link.read_ap(addr, now=False)
        except exceptions.ProbeError as error:
            self._handle_error(error, num)
            raise

        # Read callback returned for async reads.
        def read_ap_cb():
            try:
                result = result_cb()
                if LOG_DAP:
                    self.logger.info("read_ap:%06d %s(addr=0x%08x) -> 0x%08x", num, "" if now else "...", addr, result)
                return result
            except exceptions.ProbeError as error:
                self._handle_error(error, num)
                raise

        if now:
            return read_ap_cb()
        else:
            if LOG_DAP:
                self.logger.info("read_ap:%06d (addr=0x%08x) -> ...", num, addr)
            return read_ap_cb

    def _handle_error(self, error, num):
        if LOG_DAP:
            self.logger.info("error:%06d %s", num, error)
        # Clear sticky error for fault errors.
        if isinstance(error, exceptions.TransferFaultError):
            self.clear_sticky_err()
        # For timeouts caused by WAIT responses, set DAPABORT to abort the transfer.
        elif isinstance(error, exceptions.TransferTimeoutError):
            self.write_reg(DP_ABORT, ABORT_DAPABORT)

    def clear_sticky_err(self):
        mode = self.link.wire_protocol
        if mode == DebugProbe.Protocol.SWD:
            self.write_reg(DP_ABORT, ABORT_ORUNERRCLR | ABORT_WDERRCLR | ABORT_STKERRCLR | ABORT_STKCMPCLR)
        elif mode == DebugProbe.Protocol.JTAG:
            self.write_reg(DP_CTRL_STAT, CTRLSTAT_STICKYERR | CTRLSTAT_STICKYCMP | CTRLSTAT_STICKYORUN)
        else:
            assert False



