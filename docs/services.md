# Services

## Monitoring

### Starting
Services are started by the `ServiceManager`. A service manager is not interacted with direclty but through a 
class named `Scheduler`.

Services are naturally efficient. Services when controlled by the service manager are killed automatically
when stopped. There is no means of stopping a service and expecting it to hang around in some buffer.

    Note: there does exist a halt flag on the stop_service_pid() method but this will only halt the
          service for one event loop. Long enough to gather data or handle it before it is picked
          up and flagged to be recovered.

### Restarts
If a service is killed, the service manager will automatically restart it if the scheduler is setup for 
service recovery. You can try this by issuing a command to `self.stop()` in the event loop of a service. 
You will immediately find that the next event loop of the `ServiceManager` will try and restart the service.

Services that store state in memory should be discouraged. Determine carefully if your service needs to
store state and if it should recover from a kill.

    Note: if service recovery is enabled, you may find that if a service was not properly shutdown
    and if it depends on other services which are shutdown, it may come back online trying to
    connect to those 'dead' services.

Services and their meta data are stored as a ServiceDirectoryEntry. The Meta data object within that
entry stores various information about services. Some of these fields are:

  1. alias: name of the service
  1. delay: how long to delay the start of the service
  1. retry_enabled:  how many times to retry
  1. recovery_enabled : if the service is allowed to recover
  1. starts: how many times the service was started
  1. exception: an exception (the last) which is part of the service if it failed
  1. failed: whether a service is marked as a failed service

### Creating

1. When creating services, do not call the constructor within a method. This has been proven to cause issues with
services dying. Don't do:
```python
doSomething(MyService())
```

Instead do:
```python
pid = MyService()
doSomething(pid)
```

### States

Services have three states:
    1. idle - meaning the service was just created
    1. stopped - the service was just stopped
    1. started - the service was just started

The idle state of a service is used only at the start or beginning of service creation. Once it
has been created it will never go back into the idle state. Stopping a service will put it in a
stopped state, never back to idle. Unless it was destroyed.

    Note: In some of the unit tests there exists code which manually puts services in the idle state
    via `service.idle()`. This is for testing various methods and again is not recommended.
    In the future this function may be private for completness sake.

### Event Loop

When creating a service, you must inherit BaseService. A default and safe event loop is provided.

    Note: that if recovery is enabled and if you supply a bad event loop (one which may zombie
    a service by executing and exiting without properly going through the state machine and thus
    setting the appropriate service states) it will be continually seen in the logs as recovering.