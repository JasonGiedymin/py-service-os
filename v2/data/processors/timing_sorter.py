from v2.data.processors import DataProcessor
from v2.data.processors.resource import ResourceStates


class ResourceTimingSorter(DataProcessor):
    def __init__(self, name, parent_logger=None):
        DataProcessor.__init__(self, name, parent_logger)

    def sort(self, resource, possible_state, queue_service):
        resource_id = str(resource.id)
        interval_delta = resource.timings.interval_remaining()
        reset_delta = resource.timings.reset_time_remaining()
        delta = 0

        # choose the appropriate delta to use based on the status
        if possible_state is ResourceStates.WaitingForInterval:
            delta = interval_delta
        elif possible_state is ResourceStates.WaitingForReset:
            delta = reset_delta

        if 250 > delta > 50:
            self.log.debug("resource id: [%s] being put on ice for 50ms" % resource_id)
            return queue_service.put_frozen_50(resource)
        elif 500 > delta >= 250:
            self.log.debug("resource id: [%s] being put on ice for 250ms" % resource_id)
            return queue_service.put_frozen_250(resource)
        elif 1000 > delta >= 500:
            self.log.debug("resource id: [%s] being put on ice for 500ms" % resource_id)
            return queue_service.put_frozen_500(resource)
        elif 1000 <= delta:
            self.log.debug("resource id: [%s] being put on ice for 1000ms" % resource_id)
            return queue_service.put_frozen_1000(resource)
        else:
            return queue_service.put_analyze(resource)
