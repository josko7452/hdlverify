# simulator.py
# Author: Bruno Kremel (CERN BE-RF-FB)
# Date: 2016-11-08

"""

"""

from hdlverify.modelsim_simulator import ModelsimSimulator
from hdlverify.ghdl_simulator import GHDLSimulator
from hdlverify.icarus_simulator import IcarusSimulator
from hdlverify.error import SimulatorNotAvailError
from hdlverify import util
import os
import subprocess
import logging
from enum import Enum

SIM_ENV = 'HDLVERIFY_SIM'

class SimulatorInterface(Enum):
    VERILOG_VPI = 0
    GHDL_VPI = 1

class Simulator(object):

    name = None
    sim_exec = None
    interface = None

    std = {'V1995': None,
           'V2001': None,
           'V2005': None,
           'SV2005': None,
           'SV2009': None,
           'SV2012': None,
           'VHDL-1987': None,
           'VHDL-1993': None,
           'VHDL-2002': None,
           'VHDL-2008': None}

    @classmethod
    def _find_in_path(cls):
        return os.path.dirname(util.which(cls.sim_exec))

    @classmethod
    def _find_path(cls):
        lookup = 'HDLVERIFY_' + cls.name.upper() + '_PATH'
        path = os.environ.get(lookup)
        if path is None:
            logging.info('[%s] %s variable is not specified, trying PATH',
                         cls, lookup)
            path = cls.find_in_path()
        return path

    @classmethod
    def available(cls):
        return cls._find_path() is not None

    def __init__(self, workdir='tmp'):
        self.libs = set([])
        self.srcs = {}
        self.workdir = workdir
        self.path = self._find_path()

    def _exec(self, cmd, *args, **kwargs):
        logging.debug('[%s] Running: %s', self, ' '.join(cmd))
        kwargs.setdefault('env', {})
        subprocess.check_call(cmd, *args, **kwargs)

    def _add_lib(self, lib):
        raise NotImplementedError

    def _add_src(self, path, src_tup):
        raise NotImplementedError

    def add_lib(self, lib):
        if lib in self.libs:
            logging.warning('[%s] Library %s does already exists', self, lib)
        else:
            self.libs.add(lib)
            self._add_lib()

    def add_src(self, path, lib, std=None, include=None, defines={}):
        if path in self.srcs:
            logging.warning('[%s] Source %s does already exists', self, path)
        else:
            self.srcs[path] = (lib, std, include)
            self._add_src(path, (lib, std, include, defines))

    def get_run_cmd(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


avail = [ModelsimSimulator,
         GHDLSimulator,
         IcarusSimulator]

env_sim = os.environ[SIM_ENV] if os.environ[SIM_ENV] else None


def factory(args):
    selected_sim = args.sim if args.sim else env_sim

    for sim in avail:
        if sim.name == selected_sim:
            if sim.available:
                return sim
            else:
                raise SimulatorNotAvailError(sim)
