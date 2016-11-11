# debug.py
# Author: Bruno Kremel (CERN BE-RF-FB)
# Date: 2016-11-09

"""

"""

import logging


class Debug(object):

    enabled = False

    @classmethod
    def enable(cls):
        logging.basicConfig(level=logging.DEBUG)
        cls.enabled = True

    @classmethod
    def disable(cls):
        logging.basicConfig(level=logging.INFO)
        cls.enabled = False
