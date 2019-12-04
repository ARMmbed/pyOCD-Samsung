# pyOCD debugger
# Copyright (c) 2006-2013 Arm Limited
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

import logging
from ...flash.flash import Flash
from ...core.coresight_target import CoreSightTarget
from ...core.memory_map import (FlashRegion, RamRegion, MemoryMap)
from ...coresight.cortex_m import CortexM
from ...debug.svd.loader import SVDFile

LOG = logging.getLogger(__name__)

FLASH_ALGO = { 'load_address' : 0x00100000,
               'instructions' : [
                                  0xE00ABE00, 0x062D780D, 0x24084068, 0xD3000040, 0x1E644058, 0x1C49D1FA, 0x2A001E52, 0x4770D1F2,
								  0x280a49fa, 0x698ad10a, 0x7f80f012, 0x698ad1fb, 0x0f7ff412, 0x220dd1fb, 0x2020f881, 0xf012698a,
								  0xd1fb7f80, 0xf412698a, 0xd1fb0f7f, 0x0020f881, 0xb1284770, 0x70116802, 0x1c496801, 0x47706001,
								  0x48eab2ca, 0xd10a2a0a, 0xf0116981, 0xd1fb7f80, 0xf4116981, 0xd1fb0f7f, 0xf880210d, 0x69811020,
								  0x7f80f011, 0x6981d1fb, 0x0f7ff411, 0xf880d1fb, 0x47702020, 0x41f0e92d, 0x460e1e14, 0xf04f4680,
								  0xf04f0500, 0xdd100720, 0x21007832, 0xb1224630, 0x2f01f810, 0x2a001c49, 0x42a1d1fa, 0x2400bfac,
								  0xf0131a64, 0xbf180f02, 0xf0132730, 0xd1090f01, 0xdd072c00, 0x46404639, 0xffbbf7ff, 0x1c6d1e64,
								  0xdcf72c00, 0xb1407830, 0x4640b2c1, 0xffb1f7ff, 0x0f01f816, 0x28001c6d, 0x2c00d1f6, 0x4639dd07,
								  0xf7ff4640, 0x1e64ffa6, 0x2c001c6d, 0x4628dcf7, 0x81f0e8bd, 0x45f0e92d, 0x469cb083, 0xe9dd4680,
								  0x2000730b, 0x46059e0a, 0xb1294682, 0x0f00f1bc, 0x2a0ad016, 0xe013d00e, 0xf88d2030, 0xf88d0000,
								  0x463ba001, 0x46694632, 0xf7ff4640, 0xb003ffa3, 0x85f0e8bd, 0x0c00f1b1, 0x2001bfbc, 0x0100f1cc,
								  0x040bf10d, 0xa00bf88d, 0xfbb1b189, 0xfb02fcf2, 0xf1bc1c1c, 0xbfa40f0a, 0xf1ac449c, 0xf10c0c3a,
								  0xfbb10c30, 0xf804f1f2, 0x2900cd01, 0xb178d1ed, 0xbf182e00, 0x0f02f017, 0xf04fd007, 0x4640012d,
								  0xff57f7ff, 0x1e761c6d, 0x202de002, 0x0d01f804, 0x4632463b, 0x46404621, 0xff6cf7ff, 0x4428b003,
								  0x85f0e8bd, 0xe92db40f, 0xb0844df0, 0x9c0c2700, 0xad0d463e, 0x28007820, 0xf04fd075, 0xf04f0b41,
								  0x46ba0861, 0x2825b2c0, 0x2200d17b, 0x0f01f814, 0x28004613, 0x2825d07f, 0x282dd073, 0x2301bf04,
								  0x78201c64, 0xd1052830, 0x0f01f814, 0x0302f043, 0xd0f92830, 0x3830b2c0, 0xd80a2809, 0x0082eb02,
								  0xf8140040, 0x38301b01, 0x7820180a, 0x28093830, 0x7820d9f4, 0xd00a2873, 0xd0112864, 0xd01c2878,
								  0xd0272858, 0xd0322875, 0xd03f2863, 0xf855e04e, 0x29001b04, 0xa16ebf08, 0xf7ff4638, 0xe024ff1b,
								  0x2300e9cd, 0x8008f8cd, 0x1b04f855, 0x220a2301, 0xf7ff4638, 0x4406ff4f, 0xe9cde038, 0xf8cd2300,
								  0xf8558008, 0x23001b04, 0x46382210, 0xff42f7ff, 0xe02b4406, 0x2300e9cd, 0xb008f8cd, 0x1b04f855,
								  0x22102300, 0xf7ff4638, 0x4406ff35, 0xe9cde01e, 0xf8cd2300, 0xf8558008, 0x23001b04, 0x4638220a,
								  0xff28f7ff, 0xe01be7f1, 0xe014e00b, 0x0b04f815, 0x000cf88d, 0xa00df88d, 0x4638a903, 0xfedaf7ff,
								  0xb2c1e7e3, 0xf7ff4638, 0x1c76feb4, 0x0f01f814, 0xf47f2800, 0x2f00af77, 0x6838bf1c, 0xa000f880,
								  0xb0044630, 0x0df0e8bd, 0xfb14f85d, 0xea236803, 0x43110101, 0x47706001, 0x42812100, 0x1c49bfb8,
								  0x4770dbfb, 0xf44f493c, 0xf84140c6, 0x60480f70, 0x60c86088, 0x61486108, 0x21014838, 0x21006741,
								  0x49376781, 0x21646041, 0x1c402000, 0xdbfc4288, 0xf04f4770, 0x48334202, 0xf8c24934, 0x48320100,
								  0x49336008, 0x60081200, 0x12001d09, 0x49316008, 0x1d096008, 0x3001f04f, 0x210a6008, 0x1c402000,
								  0xdbfc4288, 0x2136482c, 0x21106241, 0x21706281, 0xf24062c1, 0x63013101, 0x60012155, 0x210a4827,
								  0x0100f8c2, 0x1c402000, 0xdbfc4288, 0xf3bf4770, 0xf3bf8f6f, 0x49228f4f, 0x60082000, 0x8f6ff3bf,
								  0x8f4ff3bf, 0x481f4920, 0x47706008, 0x8f6ff3bf, 0x8f4ff3bf, 0x21e0f04f, 0x61082000, 0x8f6ff3bf,
								  0x8f4ff3bf, 0xf3bf4770, 0xf3bf8f6f, 0x20008f4f, 0xf1004601, 0x1d0022e0, 0x1100f8c2, 0xdbf82820,
								  0x8f6ff3bf, 0x8f4ff3bf, 0x00004770, 0x83015000, 0x6c756e28, 0x0000296c, 0x82021000, 0x85020000,
								  0x8660061a, 0xc1900d01, 0x01000001, 0x82000a04, 0x83000a00, 0x85000a00, 0x85024000, 0xc1900d11,
								  0xe000ef50, 0x00040200, 0xe000ed14, 0x20e0f04f, 0xf8402100, 0x4aac1f10, 0x7100f04f, 0x17516011,
								  0x1170f8c0, 0x1174f8c0, 0x1270f8c0, 0x1274f8c0, 0x4ba64770, 0xf0406818, 0x60180002, 0x680849a4,
								  0x0001f040, 0x49a36008, 0xf0406808, 0x60080001, 0xf8d149a1, 0xb1780118, 0xf8c12200, 0x200f2100,
								  0x0104f8c1, 0x0108f8d1, 0xd1fb280f, 0x2104f8c1, 0x0108f8d1, 0xd1fb2800, 0x20002264, 0x42901c40,
								  0xf8d1dbfc, 0xf0200110, 0xf8c10003, 0xf8d10110, 0xf0200118, 0xf8c10003, 0xf8d10118, 0xf0200114,
								  0xf8c10003, 0x68180114, 0x0002f020, 0x47706018, 0x2000498a, 0x47706008, 0x45f0e92d, 0xf04f4887,
								  0xf8c00c00, 0xf7ffc000, 0xf3bfff24, 0xf3bf8f6f, 0x48838f4f, 0xc000f8c0, 0x8f6ff3bf, 0x8f4ff3bf,
								  0x48804981, 0xf3bf6008, 0xf3bf8f6f, 0xf04f8f4f, 0xf3bf20e0, 0xf3bf8f6f, 0xf8c08f4f, 0x4a72c010,
								  0x7100f04f, 0x17516011, 0x1180f8c0, 0x1184f8c0, 0x1280f8c0, 0x1284f8c0, 0x8f6ff3bf, 0x8f4ff3bf,
								  0xf1002000, 0x1d0021e0, 0xc100f8c1, 0xdbf82820, 0x8f6ff3bf, 0x8f4ff3bf, 0xff7bf7ff, 0x81b0f8df,
								  0x486a2201, 0xf8c84b6b, 0xf2472038, 0xf8c03101, 0xf8c3c0c4, 0xf8c31130, 0xe9c01134, 0x26032c02,
								  0xe9c02406, 0xe9c04c04, 0xf243c206, 0xf04f3785, 0xe9c04502, 0xf8d56700, 0xf0155100, 0xf04f4f00,
								  0xbf190504, 0x6aa1f44f, 0xa20ae9c0, 0x0aa8f04f, 0xa50ae9c0, 0x0a07f04f, 0xc038f8c0, 0x20c4f8c0,
								  0x2038f8c8, 0xc0c4f8c0, 0x1130f8c3, 0x1134f8c3, 0x60476006, 0x2121f240, 0xf8c06081, 0x6104c00c,
								  0xc014f8c0, 0xc018f8c0, 0x216a61c2, 0x62c46281, 0x63456305, 0xc03cf8c0, 0xa008f8c0, 0x20002164,
								  0x42881c40, 0xf44fdbfc, 0x671840c6, 0x67986758, 0xf8c367d8, 0xf8c30080, 0x483f0084, 0x6041493f,
								  0x2c1de9c0, 0x20002164, 0x42881c40, 0x2000dbfc, 0x85f0e8bd, 0xb5104938, 0x60484839, 0xf7ffa039,
								  0x2000fdb1, 0xb510bd10, 0xf7ffa038, 0x4932fdab, 0x60484832, 0xf7ffa038, 0x2000fda5, 0xb570bd10,
								  0x46054c2d, 0x6060482d, 0x46296862, 0xf7ffa034, 0xf894fd99, 0xf01220dc, 0xd1fa0f01, 0x4080f1a5,
								  0x20ff6120, 0x005ef884, 0x00dcf894, 0x0f01f010, 0x4835d1fa, 0x68616060, 0xf7ffa034, 0x2000fd83,
								  0xe92dbd70, 0x4e1c41f0, 0x44a0f100, 0x4615481b, 0x6070460f, 0x460a6873, 0xa0314621, 0xfd72f7ff,
								  0xf0301cf8, 0xd0050003, 0x1b04f855, 0x1b04f844, 0xd1f91f00, 0x60704824, 0xa0246871, 0xfd62f7ff,
								  0xe8bd2000, 0x000081f0, 0xe000ed04, 0x82020460, 0x82020500, 0x82020520, 0x82020000, 0x83011000,
								  0xe000ef50, 0x00040200, 0xe000ed14, 0x83015000, 0x85041000, 0x82021000, 0x85020000, 0x8660061a,
								  0x0660860a, 0x6e696e55, 0x000a7469, 0x53415245, 0x48432045, 0x000a5049, 0x454e4f44, 0x0000000a,
								  0x20337773, 0x53415245, 0x45532045, 0x524f5443, 0x7830202c, 0x202c7825, 0x73616c66, 0x78305b68,
								  0x0a5d7825, 0x00000000, 0x0660061a, 0x656e6f64, 0x616c6620, 0x305b6873, 0x5d782578, 0x0000000a,
								  0x676f7250, 0x206d6172, 0x3d726461, 0x78257830, 0x7a73202c, 0x2578303d, 0x66202c78, 0x6873616c,
								  0x2578305b, 0x000a5d78, 0x00000000
                                ],
               'pc_init'          : 0x001004F9,
               'pc_eraseAll'      : 0x00100667,
               'pc_erase_sector'  : 0x0010067F,
               'pc_program_page'  : 0x001006C3, 
               'static_base'      : 0x00100001,
               'begin_data'       : 0x00100000, 
               'page_buffers'    : [0x00101000, 0x00101800],  
               'begin_stack'      : 0x00102800,
               'analyzer_supported' : False,
               'analyzer_address' : 0x00000000 
              }

class S5JS100(CoreSightTarget):

    VENDOR = "Samsung"
    AP_NUM = 0
    
    memoryMap = MemoryMap(
        FlashRegion(    start=0x00000000,  length=0x20000,      blocksize=0x100, is_boot_memory=True,
            algo=FLASH_ALGO),
        RamRegion(      start=0x20000000,  length=0x4000)
        )

    def __init__(self, link):
        super(S5JS100, self).__init__(link, self.memoryMap)
        LOG.info("S5JS100.__init__ c")
        self.AP_NUM = 0 

    def create_init_sequence(self):
        seq = super(S5JS100, self).create_init_sequence()
        LOG.info("S5JS100.create_init_sequence c")
        seq.replace_task('find_aps', self.find_aps)
        seq.replace_task('create_cores', self.create_s5js100_core)
        return seq

    def find_aps(self):
        LOG.info("S5JS100.find_aps c")
        if self.dp.valid_aps is not None:
            return

        self.dp.valid_aps = (self.AP_NUM,)

    def create_s5js100_core(self):
        LOG.info("S5JS100.create_s5js100_core c")
        core = CortexM_S5JS100(self.session, self.aps[self.AP_NUM], self.memory_map, 0)
        core.default_reset_type = self.ResetType.SW_SYSRESETREQ
        self.aps[self.AP_NUM].core = core
        core.init()
        self.add_core(core)

class CortexM_S5JS100(CortexM):
    def reset(self, reset_type=None):
        LOG.info("Reset target...")
        self.session.notify(Target.EVENT_PRE_RESET, self)

        self._run_token += 1

        if reset_type is Target.ResetType.HW:
            self.session.probe.reset()
            self.reinit_dap()
            self.fpb.enable()

        else:
            if reset_type is Target.ResetType.SW_VECTRESET:
                mask = CortexM.NVIC_AIRCR_VECTRESET
            else:
                mask = CortexM.NVIC_AIRCR_SYSRESETREQ

            try:
                self.write_memory(CortexM.NVIC_AIRCR, CortexM.NVIC_AIRCR_VECTKEY | mask)
                self.flush()
            except exceptions.TransferError:
                self.flush()

        with Timeout(5.0) as t_o:
            while t_o.check():
                try:
                    self._ap.dp.init()
                    self._ap.dp.power_up_debug()
                    dhcsr_reg = self.read32(CortexM.DHCSR)
                    if (dhcsr_reg & CortexM.S_RESET_ST) == 0:
                        break
                    self.flush()
                except exceptions.TransferError:
                    sleep(0.01)

        self.session.notify(Target.EVENT_POST_RESET, self)

    def wait_halted(self):
        LOG.info("Wait_halted target...")

    def reinit_dap(self):
        LOG.info("Reinit target...")

    def acquire(self):
        LOG.info("Acquiring target...")

    def reset_and_halt(self, reset_type=None):
        LOG.info("Reset and Acquiring target...")

    def resume(self):
        LOG.info("Resume target...")

