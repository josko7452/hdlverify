# hdl_library.py
# Author: Bruno Kremel (CERN BE-RF-FB)
# Date: 2016-11-08

"""

"""

import glob
import logging


class HDLLibrary():

    def __init__(self, name, ver=None):
        self.ver = ver
        self.name = name
        self.ver.simulator.add_lib(name)

    def add_source_files(self, path, std=None, include=None):
        for f in glob.glob(path):
            logging.debug('[%s ]Adding src: %s to simulator: %s'
                          % (self, f, self.ver.simulator))
            self.ver.simulator.add_src(f, self.name, std, include)

    def __str__(self):
        return self.name
