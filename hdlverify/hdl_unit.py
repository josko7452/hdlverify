# hdl_unit.py
# Author: Bruno Kremel (CERN BE-RF-FB)
# Date: 2016-11-04

"""
HDLUnit allows to seamlessly simulate VHDL/Verilog units
from python utilising MyHDL cosimulation capabity.
"""

class _HDLLibrary():

    def __init__(self, name):
        self.name = name

    def add_source_files(self, path):
        pass

    def get_unit(self, name):
        pass

class HDLUnit():

    def __init__(self, param, port):
        self.param = param
        self.port = port
        self.libs = {}
        self.top = None

    def add_library(self, name):
        self.libs['name'] = _HDLLibrary(name)

    def set_top(self, name):
        spl = name.split('.')
        if len(spl) > 2:
            raise _LibraryNestingError
        elif len(spl) == 2:
            self.top = self.libs[spl[0]].get_unit(spl[1])
        else:
            raise _LibraryNotSpecifiedError

    def get_instance(self):
        return None
