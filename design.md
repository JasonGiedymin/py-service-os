Design
=======

## V2

Goal is to prep the app, will need to startup either real or mock kafka.
Real: plain install
Mock: look at kakfa interface, see what is returned.

### Decomposition

Xi - Initializer. For now file based, but can be DB based.
Xa - Analyzer.
Xr - Requestor.
Xp - Publisher.
Q -  Queue

- [ ] app Xi Read from config file, URIs
    - [ ] each URI becomes a resource
- [ ] app Xi (init) saves reference to db (cassandra, or redis) as a resource entry
- [ ] app Xi push to queue topic "analyze"
- [ ] app Xa pull from queue topic "analyze"
- [ ] app Xa analyzes entry to see if it should be requested
- [ ] app Xa saves data to resource entry, sends to "request" queue topic, else app pushes to queue topic "analyze-errors" if errors exist 
- [ ] app Xr pulls from "request" queue topic, and commences request of resource
- [ ] app Xr gathers response, or gets an error and puts on "request-error" queue topic
- [ ] app Xr saves data to resource entry based on response (parses it) 
- [ ] app Xr sends body to "publish" queue topic
- [ ] app Xp pulls from "publish" queue topic
- [ ] app Xp sends data to db, or puts errors on "publish-errors"
- [ ] app Xp sends resource back to "analyze" queue topic
- [ ] add resolution scale to resource, either seconds or ms. This way
      analyzer can quickly determine if it should skip. Maybe based on
      last checkpoint, or may last analysis checkpoint.
- [ ] add current owner to resource
- [ ] add so that owner info is adjusted based on state change?

### Performance

The various X apps will exist as greenlets, specified by the main system.

- [ ] each X app should be Base System, part of an OS.

### States

- Should i record states? One could say that the very topics themselves are
  states. In a simplistic world that is true, and this code base with v2 is
  aiming for simplicity. If I was continuing with a state machine then I'd
  continue using states and a state machine. Avoid creating a state machine
  unless absolutely necessary. See learnings.


## V1
```text
OS -> Scheduler -> ServiceManager -> DirectoryService
                                  -> Services

Options:
  give servicemanager ref to all services?
  create a base service, which is managed by service manager
  and inject that to all services?
```

## Learnings

1. state machines
    - I like them a lot which is why I tried to continue using them
    - They require lots of testing, especially the transitions of state
    - Make mocking systems complicated
    - Can be implemented simply but integrate with complexity
    - Can help maintain a highly complex event scenario.
    = Should only be used if you first desire a state machine.
    = If data should be living on a single machine without sharing
      operations, then it can be a state machine simply. Otherwise
      there might be un-needed complexity being built.
    = It is still a good technique but may be heavy handed. Use
      as a last resort.
1. keep methods close to data (duh)
