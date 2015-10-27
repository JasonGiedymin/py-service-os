from v2.data.processors import Processor


__author__ = 'jason'


class ResponseParser(Processor):
    def __init__(self, name):
        Processor.__init__(self, name)

    def parse(self, response, resource):
        resource.timings.update(response, resource.headers)
