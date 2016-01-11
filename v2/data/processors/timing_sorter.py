from v2.data.processors import DataProcessor
from v2.data.processors.resource import ResourceStates


class ResourceTimingSorter(DataProcessor):
    def __init__(self, name, parent_logger=None):
        DataProcessor.__init__(self, name, parent_logger)

    def sort(self, resource, possible_state, queue_service):
        def get_delta():
            # choose the appropriate delta to use based on the status
            if possible_state is ResourceStates.WaitingForInterval:
                return interval_delta
            elif possible_state is ResourceStates.WaitingForReset:
                return reset_delta

        def resource_queue(in_delta, in_resource):
            if 250 > in_delta > 50:
                self.log.debug("resource id: [%s] being put on ice for 50ms" % resource_id)
                return queue_service.put_frozen_50(in_resource)
            elif 500 > in_delta >= 250:
                self.log.debug("resource id: [%s] being put on ice for 250ms" % resource_id)
                return queue_service.put_frozen_250(in_resource)
            elif 1000 > in_delta >= 500:
                self.log.debug("resource id: [%s] being put on ice for 500ms" % resource_id)
                return queue_service.put_frozen_500(in_resource)
            elif 1000 <= in_delta:
                self.log.debug("resource id: [%s] being put on ice for 1000ms" % resource_id)
                return queue_service.put_frozen_1000(in_resource)
            else:
                return queue_service.put_analyze(in_resource)

        resource_id = str(resource.id)
        interval_delta = resource.timings.interval_remaining()
        reset_delta = resource.timings.reset_time_remaining()
        delta = get_delta()

        return resource_queue(delta, resource)
