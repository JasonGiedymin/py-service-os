from v2.data.processors import Processor
from v2.data.states import ResourceStates


__author__ = 'jason'


class ResponseParser(Processor):
    def __init__(self, name):
        Processor.__init__(self, name)

    @staticmethod
    def parse_headers(response, resource):
        resource.timings.update(response, resource.headers)

    # @staticmethod
    def parse(self, response, resource):
        status_code = response.status_code

        def publish_results(response, resource):
            content = None

            if resource.is_json():
                content = response.json()
            else:
                content = response.content

        def publish_error(content):
            pass

        def default():
            msg = "Found a response code which didn't expect, setting resource to error state: %+v", status_code
            self.log.error(msg)
            resource.set_error_state()

        def res200():
            msg = "200 response code received."
            self.log.debug(msg)
            ResponseParser.parse_headers(response, resource)
            publish_results(response, resource)

        def res304():
            msg = "304 not modified received, waiting for next interval"
            ResponseParser.parse_headers(response, resource)

        def res403():
            msg = "Client credentials are no longer valid or were not able to be verified."
            resource.set_error_state()
            publish_error()

        def res404():
            msg = "Response received noting resource does not exist, or does not exist any longer."
            resource.set_error_state()
            publish_error()

        def res500():
            msg = "Response received noting resource does not exist, or does not exist any longer."
            resource.set_error_state()
            publish_error()

        handler = {
            200: res200,
            304: res304,
            403: res403,
            404: res404,
            500: res500
        }

        handle = handler.get(status_code, default)

        handle()

        # ResponseParser.parse_headers(response, resource)
        # only if response good:
        # resource.timings.update(response, resource.headers)
