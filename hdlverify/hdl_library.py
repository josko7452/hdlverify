# hdl_library.py
# Author: Bruno Kremel (CERN BE-RF-FB)
# Date: 2016-11-08

"""

"""

import glob
import logging


class HDLLibrary():

    def __init__(self, name, ver=None):
        self.__ver = ver
        self.__name = name
        self.__sources = []
        self.__compiled = False

    @property
    def name(self):
        return self.__name

    def add_source_files(self, path, std=None, include=None):
        l = glob.glob(path)
        if len(l) < 1:
            logging.error('[%s] Source(s) not found at path %s' % (self, path))
        for f in l:
            logging.debug('[%s] Adding src: %s to simulator: %s'
                          % (self, f, self.__ver.simulator))
            self.__sources.append((f, std, include))

    def _compile(self):
        if not self.__compiled:
            self.__ver.simulator.add_lib(self.__name)
            for f, std, include in self.__sources:
                self.__ver.simulator.add_src(f, self.__name, std, include)
            self.__compiled = True

    def __str__(self):
        return self.__name
