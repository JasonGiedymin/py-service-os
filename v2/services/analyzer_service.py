# Lib
from v2.system.services import BaseService

# System
from uuid import uuid4

__author__ = 'jason'


class AnalyzerService(BaseService):
    def __init__(self, name):
        BaseService.__init__(self, name)