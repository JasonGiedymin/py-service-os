from v2.data.processors import DataProcessor
from v2.data.states import ResourceStates


__author__ = 'jason'


class ResponseParser(DataProcessor):
    def __init__(self, name, parent_logger=None):
        DataProcessor.__init__(self, name, parent_logger)

    @staticmethod
    def parse_headers(response, resource):
        resource.timings.update(response, resource.headers)

    # @staticmethod
    def parse(self, response, resource):
        status_code = response.status_code

        def publish_results(resp, res):
            content = None

            if res.is_json():
                content = resp.json()
            else:
                content = resp.content

            return True

        def publish_error():
            return False

        def default():
            msg = "Found a response code which didn't expect, setting resource to error state."
            self.log.error(msg, status_code=status_code)
            resource.set_error_state()
            return publish_error()

        def res200():
            msg = "200 response code received."
            self.log.debug(msg, status_code=status_code)
            ResponseParser.parse_headers(response, resource)
            return publish_results(response, resource)

        def res304():
            msg = "304 not modified received, waiting for next interval"
            self.log.debug(msg, status_code=status_code)
            ResponseParser.parse_headers(response, resource)
            return True

        def res403():
            msg = "Client credentials are no longer valid or were not able to be verified."
            self.log.debug(msg, status_code=status_code)
            resource.set_error_state()
            return publish_error()

        def res404():
            msg = "Response received noting resource does not exist, or does not exist any longer."
            self.log.error(msg, status_code=status_code)
            resource.set_error_state()
            return publish_error()

        def res500():
            msg = "Response received noting resource does not exist, or does not exist any longer."
            self.log.debug(msg, status_code=status_code)
            resource.set_error_state()
            return publish_error()

        handler = {
            200: res200,
            304: res304,
            403: res403,
            404: res404,
            500: res500
        }

        handle = handler.get(status_code, default)

        return handle()
