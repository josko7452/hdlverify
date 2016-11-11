# hdl_verify.py
# Author: Bruno Kremel (CERN BE-RF-FB)
# Date: 2016-11-08

"""
HDLVerify allows to seamlessly simulate VHDL/Verilog units
from python utilising MyHDL cosimulation capabity.
"""

from hdlverify.hdl_library import HDLLibrary
from hdlverify.hdl_instance import HDLInstance
from hdlverify import simulator
from debug import Debug


class HDLVerify():

    @classmethod
    def init_argv(cls, argv=None):
        pass

    @classmethod
    def init_args(cls, args=None):
        if hasattr(args, 'verbose') and args.verbose:
            Debug.enable()
        else:
            Debug.disable()
        return cls(simulator.factory(args).from_args(args))

    def __init__(self, sim):
        self.simulator = sim

    def instance(self):
        return HDLInstance(self)

    def library(self, name):
        return HDLLibrary(name, self)
