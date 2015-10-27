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
- [*] resource analyzer
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
    - [ ] parse out response status to determine if has error, should be done before timings parsing
    - [ ] check for errors?
- [*] analyzer app
    - [x] check for ownership
    - [ ] make resource analyzer a service with supervisor?
    - [ ] too many parent/child logs
    - [ ] start of db interface (resource store)
- [ ] single app cli that can start any number of services
    - [ ] single VM service cat?
- [ ] resource requestor
    - [ ] do request
    - [ ] parse response
- [ ] publisher

## v0.0.2.0 - RequestMachineMatrix
- [ ] store all vars (request spec, timing, etc...) in a dict, key'ed by uri, allowing
      multiple requests to be handled by one machine. First pass should be blocking.
- [ ] next up make each get spawn and return a future, saved in


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


## Bucket
- [ ] ...