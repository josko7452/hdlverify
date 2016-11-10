# hdl_verify.py
# Author: Bruno Kremel (CERN BE-RF-FB)
# Date: 2016-11-08

"""
HDLVerify allows to seamlessly simulate VHDL/Verilog units
from python utilising MyHDL cosimulation capabity.
"""

from hdlverify.hdl_library import HDLLibrary
from hdlverify.hdl_instance import HDLInstance
from hdlverify.simulator import simulator

class HDLVerify():

    @classmethod
    def init_argv(cls, argv=None):
        pass

    @classmethod
    def from_args(cls, args=None):
        return cls(simulator.factory(args.sim))

    def __init__(self, sim):
        self.simulator = sim

    def instance():
        return HDLInstance(self)

    def library(name):
        return HDLLibrary(name, self)
