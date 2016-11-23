# hdl_instance.py
# Author: Bruno Kremel (CERN BE-RF-FB)
# Date: 2016-11-04

"""
HDLUnit allows to seamlessly simulate VHDL/Verilog units
from python utilising MyHDL cosimulation capabity.
"""

import logging
from myhdl import Cosimulation
from hdlverify import Direction
from simulator import SimulatorInterface
from error import LibraryNestingError, UnitNotFoundError
import os
import binascii

RANDOM_PREFIX_LEN = 2


class _CosimGen(object):

    VLOG_WRAPPER_TPL = (
        'module {wrapper};\n' +
        '\n' +
        '{declarations}' +
        '\n' +
        'initial begin\n' +
        '    $from_myhdl({from_myhdl});\n' +
        '    $to_myhdl({to_myhdl});\n' +
        'end\n' +
        '\n' +
        '{unit} {param}wrapper_dut (\n{assigns}' +
        '\n);\n' +
        'endmodule\n'
    )

    DECL_TPL = '{kind} {array}{signal};\n'
    KIND_TO = 'wire'
    KIND_FROM = 'reg'
    ARRAY_TPL = '[{w}-1:0] '

    INDENT = 15
    LIST_TPL = INDENT*' ' + '{signal},\n'

    ASSIGN_TPL = INDENT*' ' + '.{target}({src}),\n'
    PARAM_TPL = '#(\n{param}\n) '

    PARAM_VAL = INDENT*' ' + '.{par}({val}),\n'

    def __init__(self, top, param, port, sim):
        self.__top = top
        self.__top_name = '%s.%s' % (str(top[0]), top[1])
        self.__random_prefix = binascii.b2a_hex(os.urandom(RANDOM_PREFIX_LEN))
        self.__wrapper = 'dut_wrapper_%s_%s' % (self.__random_prefix, self.__top[1])
        self.__param = param
        self.__port = port
        self.__sim = sim

    def _generate_verilog_wrapper(self):
        decl = ''
        from_myhdl = ''
        to_myhdl = ''
        assigns = ''
        for k, v in self.__port.items():
            sig, direction = v
            arr = '' if type(sig.val) == bool\
                  else self.ARRAY_TPL.format(w=len(sig))
            l = self.LIST_TPL.format(signal=k)
            assigns += self.ASSIGN_TPL.format(target=k, src=k)
            if direction == Direction.IN:
                decl += self.DECL_TPL.format(kind=self.KIND_FROM,
                                             array=arr, signal=k)
                from_myhdl += ' '+l
            elif direction == Direction.OUT:
                decl += self.DECL_TPL.format(kind=self.KIND_TO,
                                             array=arr, signal=k)
                to_myhdl += l[1:]
            else:
                raise NotImplementedError
        assigns = assigns[:-2]
        to_myhdl = to_myhdl[self.INDENT-1:-2]
        from_myhdl = from_myhdl[self.INDENT+1:-2]
        params = ''
        for k, v in self.__param.items():
            if type(v) == bool:
                v = 1 if v else 0
            if type(v) == str:
                v = '"%s"' % v
            params += self.PARAM_VAL.format(par=k, val=v)
        params = self.PARAM_TPL.format(param=params[:-2])

        wrapper = self.VLOG_WRAPPER_TPL.format(wrapper=self.__wrapper,
                                               unit=self.__top[1],
                                               declarations=decl,
                                               from_myhdl=from_myhdl,
                                               to_myhdl=to_myhdl,
                                               assigns=assigns,
                                               param=params)
        wrapper_path = '%s.v' % self.__wrapper
        with open(wrapper_path, 'w') as f:
            f.write(wrapper)
        self.__sim.add_lib('work')
        self.__sim.add_src(wrapper_path, 'work', replace=True)

    def _generate_vhdl_wrapper(self):
        raise NotImplementedError

    def _prepare_cosim(self):
        if self.__sim.interface == SimulatorInterface.VERILOG_VPI:
            self._generate_verilog_wrapper()
        elif self.__sim.interface == SimulatorInterface.GHDL_VPI:
            self._generate_vhdl_wrapper()

    def _cosim(self):
        self._prepare_cosim()
        cmd = self.__sim.get_run_cmd(self.__wrapper)
        cosim_kwargs = {k: v[0] for k, v in self.__port.items()}
        logging.debug('[%s] Cosim kwargs: %s', self, cosim_kwargs)
        cosim = Cosimulation(cmd, **cosim_kwargs)
        return cosim

class HDLInstance(object):

    def __init__(self, ver=None):
        self.__ver = ver
        self.__libs = {}

    def add_library(self, lib):
        self.__libs[lib.name] = lib

    def get_instance(self, top_name, param=None, port=None):
        spl = top_name.split('.')
        if len(spl) > 2:
            raise LibraryNestingError(top_name)
        elif len(spl) == 2:
            if spl[0] in self.__libs:
                top = (self.__libs[spl[0]], spl[1])
            else:
                raise UnitNotFoundError(spl[0], spl[1])
        elif 'work' in self.__libs:
            logging.info('Library not specified, assuming "work"' +
                         'for instance lookup')
            top = (self.__libs['work'], top_name)
        else:
            raise UnitNotFoundError('work', top_name)

        for k, v in self.__libs.items():
            v._compile()

        gen = _CosimGen(top, param, port, self.__ver.simulator)
        instance = gen._cosim()
        return instance
