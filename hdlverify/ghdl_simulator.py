# ghdl_simulator.py
# Author: Bruno Kremel (CERN BE-RF-FB)
# Date: 2016-11-10

"""

"""

from hdlverify.simulator import Simulator


class GHDLSimulator(Simulator):

    name = 'ghdl'
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

    def __init__(self, workdir='ghdl_work'):
        if workdir:
            self._exec('%s %s' % (self.library_exec, workdir))
        super(GHDLSimulator, self).__init__(self)
