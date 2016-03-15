README
-----------------

This is a simple python app which tries to deal with services, has good logging, and generally very far from what I did end up doing. In the end it was a experiment.

## Deps
This project can make use of pypy.
```shell
brew install pypy

mkvirtualenv --python $(which pypy) pypy-git-pub
# then always use pypy in place of python
# you can also use pip, which should be referenced by
# the new virtualenv

```

Upgrade Pip to the lastest:
```shell
pip install --upgrade pip
```

Below is the manual list which should match the requirements.txt file.
Note that the below are ABSOLUTELY REQUIRED.
```shell
pip install -U --pre github3.py
pip install -U requests
pip install -U CacheControl
pip install -U pytest
pip install -U requests_mock
pip install -U futures
# pypy already provides, pip install -U greenlet
pip install gevent==1.1b6 # get latest release from https://github.com/gevent/gevent/releases
# non pypy: pip install -U gevent
pip install -U enum34
pip install -U scales
pip install -U flask
pip install -U pytest-flask
# pip install -U gipc # may require `xcode-select --install` to be run
pip install -U tox
pip install -U structlog
pip install -U ipython
pip install -U jupyter
pip install -U python-igraph
pip install -U matplotlib
pip install -U Jinja2
pip install -U numpy
pip install -U pyzmq
pip install -U tornado
pip install -U sympy
pip install -U six
pip install -U pyparsing
pip install -U radon # https://radon.readthedocs.org/en/latest/commandline.html
pip install -U xenon
```

## Tests

### Unit Tests
Uses py.test:
```shell
# make sure your in the root of the project
./py.test
```

### Integration Tests
Uses tox. See:
  1. `tox.ini`
  1. `requirements.ini`
  1. `setup.py`

Usage:
```shell
tox
```

## Development/Usage

### Generate Requirements
```shell
pip freeze > requirements.txt
```

