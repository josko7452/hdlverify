# error.py
# Author: Bruno Kremel (CERN BE-RF-FB)
# Date: 2016-11-09

"""
Definition of exceptions
"""


class SimulatorNotAvailError(Exception):
    def __init__(self, sim):
        msg = (('Simulator %s not available in system.' % str(sim)) +
                   'Check installation and check if it exists in PATH')
        super(SimulatorNotAvailError, self).__init__(msg)


class UnitNotFoundError(Exception):
    def __init__(self, lib, unit):
        msg = ('Unit %s not found in library %s lib') % (unit, lib)
        super(UnitNotFoundError, self).__init__(msg)


class LibraryNestingError(Exception):
    def __init__(self, spec):
        msg = 'Nested library is not supported %s' % spec
        super(LibraryNestingError, self).__init__(msg)

