# simulator.py
# Author: Bruno Kremel (CERN BE-RF-FB)
# Date: 2016-11-08

"""

"""

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
    def from_args(cls):
        raise NotImplementedError

    @classmethod
    def _find_in_path(cls):
        return os.path.dirname(util.which(cls.sim_exec))

    @classmethod
    def _find_path(cls):
        lookup = 'HDLVERIFY_' + cls.name.upper() + '_PATH'
        path = os.environ.get(lookup)
        if path is None:
            logging.info('%s variable is not specified, trying PATH', lookup)
            path = cls._find_in_path()
        return path

    @classmethod
    def available(cls):
        return cls._find_path() is not None

    def __init__(self, workdir='tmp'):
        self._libs = set([])
        self._srcs = {}
        self._workdir = workdir
        self._path = self._find_path()

    def _exec(self, cmd, *args, **kwargs):
        cmd = [i for i in cmd if i is not None]
        logging.debug('[%s] Running: %s', self, ' '.join(cmd))
        kwargs.setdefault('env', {})
        subprocess.check_call(cmd, *args, **kwargs)

    def _add_lib(self, lib):
        raise NotImplementedError

    def _add_src(self, path, src_tup):
        raise NotImplementedError

    def add_lib(self, lib):
        if lib in self._libs:
            logging.warning('[%s] Library %s does already exists', self, lib)
        else:
            self._libs.add(lib)
            self._add_lib(lib)

    def add_src(self, path, lib, std=None, include=None, defines={}, replace=False):
        if path in self._srcs and not replace:
            logging.warning('[%s] Source %s does already exists', self, path)
        else:
            self._srcs[path] = (lib, std, include)
            self._add_src(path, (lib, std, include, defines))

    def get_run_cmd(self, top, fli=None):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

from hdlverify.modelsim_simulator import ModelsimSimulator
from hdlverify.ghdl_simulator import GHDLSimulator
from hdlverify.icarus_simulator import IcarusSimulator

avail = [ModelsimSimulator,
         GHDLSimulator,
         IcarusSimulator]

env_sim = os.environ[SIM_ENV] if SIM_ENV in os.environ else None


def factory(args):
    selected_sim = args.sim if args.sim else env_sim

    for sim in avail:
        if sim.name == selected_sim:
            if sim.available:
                return sim
            else:
                raise SimulatorNotAvailError(sim)
