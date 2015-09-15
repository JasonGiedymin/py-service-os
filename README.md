Py-Git-Pub README
-----------------

This is a simple python app which does the following:

  - [ ] Read from the github firehose
  - [ ] Publishes the data to Kafka raw
  - [ ] Stats endpoint
  - [ ] Health endpoint
  - [ ] Logging
  - [ ] Commandline params
  - [ ] Config file
  - [ ] Distributed? No deploy this specifying a replication controller scale of 1
  - [ ] Futures/async

It should not do any data inspection unless for the most absolute basic of
filtering or statistics. The stats should be meant for health and performance,
not for data inspection.

## Deps
```shell
pip install --upgrade pip
```

Below is the manual list which should match the requirements.txt file.
```shell
pip install -U --pre github3.py
pip install -U requests
pip install -U CacheControl
pip install -U pytest
pip install -U requests_mock
pip install -U futures
pip install -U greenlet
pip install -U gevent
pip install -U enum34
pip install -U scales
pip install -U flask
pip install -U pytest-flask
```

## Tests
Uses py.test.
```shell
# make sure your in the root of the project
./py.test
```

## Additional Info
Most APIs can be and should be driven by tokens.
This app should use a personal token which is generated manually by the UI.
It could be done via automation but at the time does not.

## Limits

Respect the following limits:

1. Most github APIs have a rate-limit of 5000 req/hr. Otherwise it will follow the rate limit header.
1. `X-RateLimit-Limit` is the limit.
1. `X-RateLimit-Remaining` is the remaining limit.
