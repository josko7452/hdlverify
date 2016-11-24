# modelsim_simulator.py
# Author: Bruno Kremel (CERN BE-RF-FB)
# Date: 2016-11-09

"""

"""

from hdlverify.debug import Debug
from hdlverify.simulator import Simulator
from hdlverify.simulator import SimulatorInterface
import os
import logging


VLOG_EXT = '.v'
SVER_EXT = '.sv'
VHDL_EXT = '.vhd'


class ModelsimSimulator(Simulator):

    name = 'msim'
    sim_exec = 'vsim'
    interface = SimulatorInterface.VERILOG_VPI

    __vhdl_compile_exec = 'vcom'
    __vlog_compile_exec = 'vlog'
    __library_exec = 'vlib'
    __map_exec = 'vmap'
    __vpi_bin = 'modelsim_vpi'

    std = {'V1995': '-vlog95compat',
           'V2001': '-vlog01compat',
           'V2005': None,
           'SV2005': '-sv05compat',
           'SV2009': '-sv09compat',
           'SV2012': '-sv12compat',
           'VHDL-1987': '-87',
           'VHDL-1993': '-93',
           'VHDL-2002': '-2002',
           'VHDL-2008': '-2008'}

    @classmethod
    def from_args(cls, args=None):
        workdir = 'msim_work'
        modelsim_ini = 'modelsim_ini'
        gui = False
        if hasattr(args, 'workdir'):
            workdir = args.workdir
        elif hasattr(args, 'modelsim_ini'):
            modelsim_ini = args.modelsim_ini
        elif hasattr(args, 'gui'):
            gui = args.gui
        return cls(workdir, modelsim_ini, gui)

    def __init__(self, workdir='msim_work', modelsim_ini='modelsim_ini',
                 gui=False):
        self.__modelsim_ini = modelsim_ini
        self.__gui = gui
        super(ModelsimSimulator, self).__init__(workdir)
        if workdir:
            self._exec([os.path.join(self._path, self.__library_exec), workdir])


    def _compile_vhdl_cmd(self, path, lib, std, include):
        if not std:
            std = self.std['VHDL-2008']
        quiet = None if Debug.enabled else '-quiet'
        return [os.path.join(self._path, self.__vhdl_compile_exec), std,
                quiet, '-work', lib, path]

    def _compile_verilog_cmd(self, path, lib, std, include, defines=None):
        if not std:
            std = self.std['SV2012']
        defn = ''
        if defines:
            defn += '+define'
            for k, v in defines:
                defn += '+%s=%s' % (k, v)
        quiet = None if Debug.enabled else '-quiet'
        return [os.path.join(self._path, self.__vlog_compile_exec), std,
                quiet, '-work', lib, path]

    def _add_lib(self, lib):
        self._libs.add(lib)
        if self._workdir:
            self._exec([os.path.join(self._path, self.__library_exec), '%s/%s' %
                        (self._workdir, lib)])
            self._exec([os.path.join(self._path, self.__map_exec), lib, '%s/%s' %
                        (self._workdir, lib)])
        else:
            self._exec([os.path.join(self.path, self.__library_exec), lib])

    def _add_src(self, path, src_tup):
        lib, std, include, defines = src_tup
        ext = os.path.splitext(path)[1]
        if ext == VLOG_EXT or ext == SVER_EXT:
            self._exec(self._compile_verilog_cmd(path, lib, std,
                                                 include, defines))
        elif ext == VHDL_EXT:
            if len(defines) > 0:
                logging.warning('[%s] Defines are not applicable for VHDL', self)
            self._exec(self._compile_vhdl_cmd(path, lib, std,
                                              include))
        else:
            logging.error('[%s] File: %s has uknown type: %s', self, path, ext)

    def _get_dofile(self):
        dofile = os.path.join(self._workdir, 'msim_cosim.do')
        with open(dofile, 'w') as f:
            if not self.__gui:
                f.write('run -all\n')
                f.write('quit')
        return dofile

    def _get_fli(self):
        ext = '.dll' if os.name == 'nt' else '.so'
        return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'bin', self.__vpi_bin+ext)

    def get_run_cmd(self, top, lib='work', fli=None):
        c = '' if self.__gui else '-c'
        dbg = '' if Debug.enabled else '-quiet'
        do = self._get_dofile()
        fli = self._get_fli() if fli is None else fli
        libs = ' '.join(['-L '+str(l) for l in self._libs])
        cmd = ('%s %s %s %s -pli %s -do %s %s.%s'
               % (self.sim_exec, libs, c, dbg, fli, do, lib, top))
        logging.debug('[%s] cmd for cosim: %s' % (self, cmd))
        return cmd

    def __str__(self):
        return self.name
