TODO
----

## v0.0.1.0 - System
- [x] Create Scheduler
- [x] Create Service manager
- [x] Create Services
- [x] Create Output Reader Service
    - [x] Create Output Service(s)
- [x] Create directory service
    - [x] add directory service to service manager
    - [x] integrate directory service to each service
- [x] Access directory within each service
- [x] Unit Test proving outputservice access from a service
- [*] working request service
    - [x] request service
    - [x] request spec or limit spec?
    - [x] request machine
    - [x] request machine states
    - [x] python stats?
    - [*] inherited stats /os/services/request_service/request_machine/
        - [x] latency to base service
        - [x] latency window to base service => part of BaseService
              but may not work until served?
        - [x] reconsider request machine inherit baseservice?
        - [!] fix hierarchical stats with initChild
        - [!] see stats from scheduler onward => see above
        - [!] add to base service state stats like in example => need
              above fixed first, else can't aggregate data.
- [x] add @classmethod => not much to bind to a class with here

## v0.0.2.0 - RequestMachine - [Defer complete]
- [*] Read from the github firehose
    - [x] ~~create request engine class~~ merge into actors
    - [x] create worker
    - [x] mock responses for tests
    - [x] new request getter (RequestMachine)
    - [x] limit spec
    - [x] ~~dict of timings which to check and use to allow or prevent
          running again~~
    - [x] Timings object to keep timings
    - [x] Update timings from resp
    - [x] send send_headers with get, using a copy of the data
    - [x] subsequent calls should use etag
    - [x] subsequent calls should evaluate response code of 304
        - [x] if 304, the state should still be waiting
    - [x] work on can_request
        - [x] subsequent calls to RequestMachine.get() should honor the reset timings
          - [x] if the limit has been reached when remaining = 0
        - [x] subsequent calls to RequestMachine.get() should honor the limit remaining
        - [x] subsequent calls to RequestMachine.get() should honor the poll interval
        - [x] ~~consider sleeping using the diff between (poll - last time)~~ => this
              must be done in the service
    - [x] promote interval to be higher precedence, only if we have a timestamp which
          to do the calculation from.
    - [ ] add RequestMachine to RequestService
        - [ ] add 'some' logging to services
        - [ ] fix bug where logs were duplicated `logging.propagate=False`
    - [ ] if RequestMachine state is waiting, then create method to get proposed interval
          number which service should sleep in event loop and call the method again
    - [ ] consider adding counts to service if continuous calls to get occur but system
          is in error state. Maybe flag the service in an error state?
    - [ ] check for etag?
    - [ ] check for ratelimit reached?
    - [ ] check for poll rate?
    - [ ] check for reset time to ensure? Maybe not, move this to bucket.
    - [?] make into request adapter??
    - [ ] Ensure cache/stats are recorded for above, requests, etc...
    - [ ] consider timings time based checking?
    - [ ] expand on RequestMachine.get() states, with state switch/lambdas

## v0.0.2.1 - RequestMachineMS - [Defer complete]
- [ ] update request machine to handle milliseconds => looks like need to find alternative to time() which is seconds,
need ms or ns.
- [ ] refactor limits to not be string type, upon receiving immediately convert
- [ ] update error code handling based on golang work:
```golang
        case 403:
			log.Errorf("Client credentials are no longer valid or were not able to be verified.")
			resource.SetState(states.Error)
			return g.emptyResponse(resource)
		case 404, 500:
			// update timings
			resource.SetState(states.WaitingForServerAlive)
			return g.emptyResponse(resource)
```

## v0.0.2.1 - V2

- [x] create v2 package
- [x] remove old TODOs
- [x] redo resource and supporting classes
    - [x] add owner (being uuid)
    - [x] create class representing resource
    - [x] ensure it carries over but with milliseconds
    - [x] redo tests
    - [-] create states based on golang work:
- [x] memory based queue for testing
- [x] resource analyzer
    - [x] resource states
    - [x] direct unit test for resource analyzer
    - [x] on first init, resource has bad defaults. send in a spec or find some check to signal first call =>
          checking if timestamp is not None. Initial resource will have None timestamp.
    - [x] convert time to reset to internal milliseconds
    - [x] check that resource can be requested, request_analyzer_test.py:20+
        - [x] test_resource_analyzer_edge_case
        - [x] test with owner
        - [x] test happy path with limit remaining
        - [x] test when limit reached
        - [x] fix bug in logger, where it would not return a logger if logger handlers existed
        - [x] return resource state when calling can request
    - [x] handle cycomatic complexity of can_request    
- [x] response parser
    - [x] convert time to reset to internal milliseconds
    - [x] parse out response status to determine if has error, should be done before timings parsing
    - [x] stub out publish response
    - [x] stub out publish error
    - [x] tests
    - [x] add ability to specify resource is json
- [x] enable pypy, but comment it out
- [x] logging - revisit logging so can have child logs. Preferrably json logging.
    - [x] use structlog
    - [x] with child logging, might have to do something creative with subs
    - [x] when testing, use the test class or verify in test that correct logger name was created
- [x] add proper child logging through out OS => removed new since that
      would clear the context and then bind
    - [x] issue with common parent logger naming 
    - [x] issue with no name appearing in log
- [x] analyzer work
    - [x] check for ownership
    - [-] ~~too many parent/child logs~~ I don't see this as the case any longer.
    - [x] add logging to all v2.system.os components
- [x] create canned os
    - [x] make resource analyzer a service
    - [x] add analyzer service scaffold to canned os
- [x] complete analyzer service
    - [x] break out service_manager into own test
    - [x] add stop service from scheduler (which just proxies to service_manager
    - [x] be able to run => bootup
    - [x] be able to pull from queue interface to in-mem queue
    - [x] tests
- [x] db part 1
    - [x] start on BaseDB interface
    - [x] in mem db
- [x] queues part 1 
    - [x] start on BaseQueue interface
    - [x] in-mem queue
- [x] fixed logging of services hierarchy
- [x] fixed stopping of services to use the `stop_service()` method wrapper rather than the `stop()` service
      directly bound to a service class implementation.
- [x] canned os
    - [x] swap out hard coded db and queue with services
    - [x] fix bug with log name not showing for database, queue, and initializer service entries when stopping
          => might have to do with logs from both service manager and base service stop() methods
    - [x] start of `checks.md` to keep track of simple searches which should modify the build flow
- [x] OS test shows that possible overlap when event loop occurrs and when a service is/has stopped/stopping,
      fix by not looping if stopped.
- [x] Fix OS test mock queue service as it was expecting a quick death. Mock service now takes a quick death
      param.
- [x] Fix `should_loop()` to only look at if a service has started to execute an event loop. An example of
      where this would be a bug is if a service is set to stopped state yet the event loop continues on.
      This is a zombie like process state which we try to prevent.
- [x] Add flag for service recovery on the BaseService class.
- [x] Add zombie detection
- [x] Add code to recover zombie services if `enable_service_recovery` set to `True`
- [x] Add code to `BaseService` with a default event loop, will fix implementors of `BaseService` from having to implement the event loop when one isn't needed
- [x] replace as many event loops possible with new loop `self.should_loop():`
- [x] code requestor service
- [x] add requestor service
- [x] add output service
- [x] fix apparent `interval_timestamp` that is never updated => forgot to make call to update_interval_timestamp()
- [x] delay queue, so that quick cycles are not created within analysis queue. I.e. if a resource is pulled,
      analyzed, and then put back in the queue in the manner of milliseconds then that would cause unnecessary
      cpu timing spent in the loop.
      - [x] add frozen-50 queue for resources in the interval
      - [x] add frozen-250 queue for resources in the interval 
      - [x] add frozen-500 queue for resources in the interval
      - [x] add frozen-1000 queue for resources in the interval
      - [x] code analyzer with new timing sorter
      - [x] fix logs with response parser to actually log the resource id
      - [x] services reading from the frozen queues
      - [x] lots of tests directly with `timing_sorter.py`
      - [x] tests with analyzer using `timing_sorter.py`
      - [x] introduce test dealing with delta with regard to reset timing in the sorter
      - [x] fix `RuntimeException: maximum recursion depth exceeded` => found QueueService to have bad method, was
            calling self method.
- [x] service fail dectection, right now errors and exceptions get swallowed up
- [*] scheduler enhancements:
    - [x] allow service metadata to be stored with scheduler
    - [x] add new method manually specifying service metadata
    - [x] fix all references to add service with new service metadata
    - [x] create service_directory entry that combines service and service metadata
    - [x] allow service start delay within the scheduler
    - [x] keep track of scheduler restart counts
    - [x] Allow Scheduler.start and Scheduler.restart of service
        - [x] enhance scheduler to notice when a stop or start of a service didn't work
        - [x] replace all `service_directory[alias]` calls with get_service()
        - [x] renamed retries to starts, which makes more sense
    - [x] keep track of services that have exceptions (truely dead)
        - [x] "Rename _start_services to monitor_services"
        - [x] fix bug that when exceptions occur the OS service state is set to stop, as I found a log
              entry that said "... was found already stopped." => made all executioner services run a
              single pass event loop by calling upon the parent's BaseService.start() method during the
              CannedOS.bootup() routine.
        - [x] log services that have exceptions => exceptions are logged in service_meta.exceptions[]
        - [x] service is truely dead and upon starting reaches retry limit, code `handle_service_exception()`
            - [x] make universal error_handler, where OS can attach handlers to services as they are added,
                  having an issue where I made a class but wanted a mixin, figure it out, see canned_os
                  where I would mix it in, and the `error_handler_test.py`
            - [x] add handle_service_exception middleware (array of classes with handle() method) that will 
                  process the exception.
            - [x] allow set_logger for error handlers, so that service_manager can attach parent logger
                - [x] add an error_handler factory so we can avoid using protected attributes
            - [?] allow service_manager to handle exceptions as well? => why exactly? Ideally this
                  code needs to be highly tested. The service manager doesn't do much. Defer until
                  more evidence that this is needed.
            - [x] fix starting services with delay where it will not log started state directly after 
            - [x] fix to not allow infinite restarts, unless a delay is enacted.
                - [x] `os.py` uses a delay, and now so does the base_service. Where should a delay be
                      put? Construct a test to see how async this woks.
                - [x] fix start delay, it does not actually work
                    - [x] add new state "Starting", and make service_manager know about it
                - [x] add functionality to make service_manager know that a service didn't start properly
                      according to delay, maybe set a timeout? Service start timeout = delay + some base value?
                      Make meta hold the timeout value, and service hold the time indexes. =>
                      - [x] finish `did_service_timeout`
                      - [x] finish `start_time_delta`
                - [x] redo delay test to actually assert on the time delayed
                - [x] add test for service start timeout
                - [x] fix bug where `os_service_delay_test.py` timesout but it shouldn't happen =>
                      made sure that timeouts had to have a value greater than zero
                - [x] fix bug where retries were not accounted for during service exceptions => now they
                      are and will fall through various zombie/dead checks in `os` service manager
                - [x] fix bug where service is actually in `starting` state rather than started for
                      `base_service` class test
                - [x] apply algorithm to service starts which applies the starts count, the algorithm
                      should have fast restarts up until the 4th or 5th restart where a noticable
                      time delay should occur => meta now includes reference to function which can be
                      used else 0 or no delay will be used
            - [x] add logrithmic delay function to handle sequences of quick restarts =>
                  done see above scheduler enhancements
        - [x] fix bug where error handler does not report what error handler class it is reporting an
              error from
        - [x] create a test that will test for truely dead services that have exceptions
              occur within them. => done see above scheduler enhancements
        - [x] fix service proxy duplication by removing `directory_service_proxy`, and instead use
              use `directory_proxy`
        - [x] To enable OS stop on error, create ExitOnError error handler to be used when testing or in
              production. Since BaseService now has ErrorHandlerMixin as part of the class structure we
              can use the handle error method when an exception occurrs in the CannedOS start or event
              loop method.
            - [x] `services.py:151` commented out try/except. Failures get logged with it.
            - [x] Change CannedOS from ExecutorService to BaseService => especially since we will
                  want to shut it down gracefully, will need an event loop for that
            - [x] However check that it actually logged with some message.  => after modifying `next()`
            - [x] If it didn't should the CannedOS come with a base error handler? => yes
            - [x] When adding it, do the messages show up? => see above 
            - [x] Can the CannedOS then be set to not run the event loop (exit it on exception)?
            - [-] use the CannedOS `should_loop()` to `shutdown` if an exception is detected? => created
                  post event that can be overridden and then set to shutdown the os.
    - [x] consider moving enable_recovery into the service_manager from the service itself => moved to the
          `ServiceMetaData` class.
    - [x] record service failures with meta data => now use starts and metadata stores exceptions in a list
    - [x] add os flag to halt on failures => using the new post handle method that is overriden one can issue
          the OS to shutdown. In the fullstop test there is an example where an assertion is done to ensure
          the os `has_stopped()`.
- [x] integration test framework (bash script?? makefile??) => uses tox

## v0.0.2.0 - RequestMachineMatrix
- [~] store all vars (request spec, timing, etc...) in a dict, key'ed by uri, allowing
      multiple requests to be handled by one machine. First pass should be blocking.
      => not sure what this is. Each resource is represented by an object. If anything it
         should be distributed and stateless. The object has direct O(1) access to fields,
         defer.
- [x] next up make each get spawn and return a future.
      => services are already accessed via proxies, and by nature are services

## Bucket
- [x] "Rename _start_services to monitor_services"
      Pull out the anon methods to the either the service entry object or to the service obj 
      because they need to be tested and the entire monitor service method needs to be 
      rewritten slightly Add to that monitor_services method 'errored' that will exit 
      fast or flag a service as bad.

