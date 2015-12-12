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
- [*] delay queue, so that quick cycles are not created within analysis queue. I.e. if a resource is pulled,
      analyzed, and then put back in the queue in the manner of milliseconds then that would cause unnecessary
      cpu timing spent in the loop.
      - [x] add frozen-250 queue for resources in the interval 
      - [x] add frozen-500 queue for resources in the interval
      - [x] add frozen-1000 queue for resources in the interval
      - [x] code analyzer with new timing sorter
      - [x] fix logs with response parser to actually log the resource id
      - [ ] lots of tests directly with `timing_sorter.py`
      - [ ] tests with analyzer using `timing_sorter.py`
      - [ ] introduce test dealing with reset timing, as I believe `delta` only takes into consideration
            the interval time. It may be prudent to modify interval_timestamp to the reset time?
- [ ] db part 2
    - [ ] cassandra
- [ ] queue part 2
    - [ ] kafka queue
- [ ] single app cli that can start any number of services
    - [ ] single VM service cat?
- [ ] resource requestor
    - [ ] do request
    - [ ] parse response
- [x] publisher

## v0.0.2.0 - RequestMachineMatrix
- [~] store all vars (request spec, timing, etc...) in a dict, key'ed by uri, allowing
      multiple requests to be handled by one machine. First pass should be blocking.
      => not sure what this is. Each resource is represented by an object. If anything it
         should be distributed and stateless. The object has direct O(1) access to fields,
         defer.
- [x] next up make each get spawn and return a future.
      => services are already accessed via proxies, and by nature are services

## v0.0.3.0 - UniqueClass
- [?] UniqueService class?
- [ ] Remove uuid from BaseService to UniqueService and inherit from it

## v0.0.4.0 - Run System
- [ ] Create app.py and run system

## v0.0.5.0 - Pub to Kafka
- [ ] Service to publish data to Kafka raw

## v0.0.x.0 - Rest Live Data
- [ ] Need better logging
- [ ] rest api to see stats
- [ ] logging to graphite
    - [ ] revisit greplin/Cue/scales and turn on gaphited data

## v0.0.x.0 - Service Supervisors and Uptime
- [ ] Health endpoint
- [ ] stop only when work is complete
- [ ] pool request services using gevent pool
- [?] Create service checker
    - [ ] allow stop of service and checker keeps up

## v0.0.x.0 - Cleanup
- [ ] Config file
- [ ] Commandline params
- [ ] stop passing around parent logger, just use lineage or some such

## Bucket
- [ ] convert tuple to an class object within the for publish service (response_parser.py)
- [ ] services that die should have an option to store some kind of state, maybe through a interface method
      `saveState()` so that upon re-animating it will resume from the previous? Maybe discourage this type
      of state service.
- [ ] service cop to detect bad behaving services
    - [ ] may involve the service window timings be accessed via a service proxy rather than directly
          embedded within the service as it is now, this way the timing state isn't lost when the service
          is destroyed accidently
- [ ] modify scheduler to accept timings for future or inteval like work, see if any open py libraries exist
- [ ] create more friendly service supervisor for use with execution like services (may negate the need for below)
- [ ] truely create a non event loop service (code only)
