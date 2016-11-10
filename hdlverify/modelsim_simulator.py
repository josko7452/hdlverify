# modelsim_simulator.py
# Author: Bruno Kremel (CERN BE-RF-FB)
# Date: 2016-11-09

"""

"""

from hdlverify.simulator import Simulator
from hdlverify.debug import Debug
from hdlverify.simulator import SimulatorInterface
import os
import logging


VLOG_EXT = 'v'
SVER_EXT = 'sv'
VHDL_EXT = 'vhdl'


class ModelsimSimulator(Simulator):

    name = 'msim'
    sim_exec = 'vsim'
    vhdl_compile_exec = 'vcom'
    vlog_compile_exec = 'vlog'
    library_exec = 'vlib'
    map_exec = 'vmap'
    interface = SimulatorInterface.VERILOG_VPI

    std = {'V1995': '-vlog95compat',
           'V2001': '-vlog01compat',
           'V2005': None,
           'SV2005': '-sv05',
           'SV2009': '-sv09',
           'SV2012': '-sv12',
           'VHDL-1987': '-87',
           'VHDL-1993': '-93',
           'VHDL-2002': '-2002',
           'VHDL-2008': '-2008'}

    def __init__(self, workdir='msim_work', modelsim_ini='modelsim_ini'):
        self.modelsim_ini = modelsim_ini
        if workdir:
            self._exec('%s %s' % (self.library_exec, workdir))
        super(ModelsimSimulator, self).__init__(self)

    def _compile_vhdl_cmd(self, path, lib, std, include):
        if not std:
            std = self.std['VHDL-2008']
        quiet = '-quiet' if Debug.enabled else ''
        return [os.path.join(self.path, std, self.vhdl_compile_exec),
                quiet, '-work %s' % lib, path]

    def _compile_verilog_cmd(self, path, lib, std, include, defines=None):
        if not std:
            std = self.std['SV2012']
        defn = ''
        if defines:
            defn += '+define'
            for k, v in defines:
                defn += '+%s=%s' % (k, v)
        quiet = '-quiet' if Debug.enabled else ''
        return [os.path.join(self.path, std, self.vlog_compile_exec),
                quiet, '-work %s' % lib, path]

    def _add_lib(self, lib):
        if self.workdir:
            self._exec([self.library_exec, '%s/%s' % (self.workdir, lib)])
            self._exec([self.library_exec, lib, '%s/%s' % (self.workdir, lib)])
        else:
            self._exec([self.library_exec, lib])

    def _add_src(self, path, src_tup):
        lib, std, include, defines = src_tup
        ext = os.path.splitext(path)[1]
        if ext == VLOG_EXT or ext == SVER_EXT:
            self._exec(self._compile_verilog_cmd(path, lib, std,
                                                 include, defines))
        elif ext == VHDL_EXT:
            if len(defines) > 0:
                logging.warning('[%s] Defines are not applicable for VHDL')
            self._exec(self._compile_vhdl_cmd(path, lib, std,
                                              include, defines))
        else:
            logging.error('[%s] File: %s has uknown type: %s', self, path, ext)

    def _get_dofile(self):
        pass

    def get_run_cmd(self, top, fli=None):
        c = '-c' if self.gui else ''
        dbg = '' if Debug.enabled else '-quiet'
        do = self._get_dofile()
        cmd = ('%s %s %s -pli %s -do %s %s'
               % (self.sim_exec, c, dbg, fli, do, top))
        return cmd

    def __str__(self):
        return self.name
