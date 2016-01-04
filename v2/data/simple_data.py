from v2.services.retry_delays import no_delay


class ServiceMetaData:
    def __init__(self, alias, delay=0, retries=-1, retry_delay_fx=no_delay,
                 start_timeout=0, recovery_enabled=False):
        """

        :param alias: service name also known as alias
        :param delay: milliseconds to delay the start of the service. This does not apply to recovery.
                      In recovery, the standard delay is purely a function of based on starts.
        :param retries: allowed number of retries. -1 is infinite. 0 is no retries. >1 the scheduler
                      will allow this number of retries. Infinite restarts will apply the restart
                      delay. No exception to this.
        :param start_timeout: the amount of time to wait for a service to start. 0 value is none.
                              Note that this will take into account the delay as well. So if a
                              delay is 1, and you set the `start_timeout` to 1, then effectively
                              a timeout will end up being 2 (1 delay + 1 timeout).
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
        self.delay = delay  # how long to delay the start of the service THE FIRST TIME

        self.retries = retries  # how many times to retry
        # a function representing the amount of time to wait on a retry will use self.starts as input
        self.retry_delay_fx = retry_delay_fx

        self.recovery_enabled = recovery_enabled  # if the service is allowed to recover
        self.start_timeout = start_timeout  # the amount of time to wait for the service to start

        # runtime info
        self.starts = 0
        self.exceptions = []
        self.failed = False  # this might not be in sync with service state, thus might not be useful at all

    def retry_limit_reached(self):
        # infinite retries
        if self.retries == -1:
            return False

        return (self.starts - 1) >= self.retries

    def add_exception(self, exception):
        # use named arg so that it doesn't throw any errors with exceptions that don't yet
        # specify it.
        self.exceptions.append(exception(alias=self.alias))

    def next_delay(self):
        return self.retry_delay_fx(self.starts)


class ServiceDirectoryEntry:
    def __init__(self, service, service_meta):
        self.service = service
        self.service_meta = service_meta
