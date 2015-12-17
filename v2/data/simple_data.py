

class ServiceMetaData:
    def __init__(self, alias, delay=0, retry_enabled=-1, recovery_enabled=False):
        """

        :param alias: service name also known as alias
        :param delay: milliseconds to delay the start of the service (applies to recovery)
        :param retry_enabled: allowed number of retries. -1 is infinite. 0 is no retries. >1 the scheduler
                      will allow this number of retries.
        :param recovery_enabled: enables the service to be recovered. Both this value and
                                 retry need to be enabled for recovery to work. This value
                                 takes precendece. It will then rely on the retry count.
                                 This allows quick modification to the service if in prod
                                 without modifying the retry count (i.e. an external
                                 service which is relied upon is down temporarily).
        :return:
        """
        # base info
        self.alias = alias  # name of the service
        self.delay = delay  # how long to delay the start of the service
        self.retry_enabled = retry_enabled  # how many times to retry
        self.recovery_enabled = recovery_enabled  # if the service is allowed to recover

        # runtime info
        self.retries = 0
        self.exception = None
        self.failed = False


class ServiceDirectoryEntry:
    def __init__(self, service, service_meta):
        self.service = service
        self.service_meta = service_meta
