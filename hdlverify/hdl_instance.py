# hdl_instance.py
# Author: Bruno Kremel (CERN BE-RF-FB)
# Date: 2016-11-04

"""
HDLUnit allows to seamlessly simulate VHDL/Verilog units
from python utilising MyHDL cosimulation capabity.
"""

import logging
from MyHDL import Cosimulation

class _CosimGen(object):

    VLOG_WRAPPER_TPL = (
        'module ${wrapper}\n' +
        '\n' +
        '${declarations}' +
        '\n' +
        'initial begin\n' +
        '    $$from_myhdl(${from_myhdl}));\n' +
        '    $$to_myhdl(${to_myhdl}));\n' +
        'end\n' +
        '${unit} ${param}wrapper_dut (${assigs}' +
        '                     );\n+
        'endmodule\n'
    )

    DECL_TPL = '${kind} ${array}${signal};\n'
    KIND_TO = 'wire'
    KIND_FROM = 'reg'
    ARRAY_TPL = '[`${w}-1:0] '

    LIST_TPL = 15*' ' + '${signal},\n'

    ASSIGN_TPL = 21*' ' + '.{target}({src}),\n'
    PARAM_TPL = '#(\n${param}\n)'

    PARAM_VAL = 21*'' + '.${par}(${val}),\n'

    def __init__(self, top_name, param, port, sim):
        self.top_name = top_name
        self.wrapper_module = 'dut_wrapper_%s' % top_name
        self.param = param
        self.port = port
        self.sim = sim

    def _generate_verilog_wrapper(self):
        decl = ''
        from_myhdl = ''
        to_myhdl = ''
        assigns = ''
        for k,v in self.port:
            sig, direction = v
            arr = '' if type(sig.val) == bool else ARRAY_TPL.format(w=len(sig))
            l += LIST_TPL.format(signal=signal)
            assigns += ASSIGN_TPL.format(target=k, src=k)
            if direction == Direction.IN:
                decl += DECL_TPL.format(kind=KIND_FROM, array=arr, signal=k)
                from_myhdl += l
            elif direction == Direction.OUT:
                decl += DECL_TPL.format(kind=KIND_TO, array=arr, signal=k)
                to_myhdl += l
            else:
                raise NotImplementedError
            assigns = assigns[:-2]
            to_myhdl = to_myhdl[:-2]
            from_myhdl = from_myhdl[:-2]
        params = ''
        for k,v in self.param:
            params += PARAM_VAL.format(par=k, val=v)
        params = params[:-2]

        wrapper = VLOG_WRAPPER_TPL.format(wrapper=self.wrapper_module,
                                          unit=self.top_name,
                                          declarations=decl,
                                          from_myhdl=from_myhdl,
                                          to_myhdl=to_myhdl,
                                          assigns=assigs)
        wrapper_path = '%s.v' % self.wrapper_module
        with open(wrapper_path, 'w') as f:
            f.write(wrapper)
        self.sim.add_lib('work')
        self.sim.add_src(wrapper_path, 'work')

    def _generate_vhdl_wrapper(self):
        raise NotImplementedError

    def _prepare_cosim(self):
        if self.sim.interface == SimulatorInterface.VERILOG_VPI:
            self._generate_verilog_wrapper()
        elif self.sim.interface == SimulatorInterface.GHDL_VPI:
            self._generate_vhdl_wrapper()

    def _cosim(self)
        self._prepare_cosim()
        cmd = self.sim.get_run_cmd()
        cosim = Cosimulation(cmd, 

class HDLInstance(object):

    def __init__(self, ver=None):
        self.ver = ver
        self.libs = {}

    def add_library(self, lib):
        self.libs[lib.name] = lib

    def get_instance(self, top_name, param=None, port=None):
        spl = top_name.split('.')
        if len(spl) > 2:
            raise LibraryNestingError(top)
        elif len(spl) == 2:
            if spl[0] in self.libs:
                top = (self.libs[spl[0]], spl[1])
            else:
                raise UnitNotFoundError(spl[0], spl[1])
        elif 'work' in self.libs:
            logging.info('Library not specified, assuming "work"' +
                         'for instance lookup')
            top = (self.libs['work'], top_name)
        else:
            raise UnitNotFoundError('work', top_name)

        gen = _CosimGen(top_name, param, port, self.ver.simulator)
        instance = self._cosim()
        return instance
