# Ext

# Lib
from system.actors import Actor, Supervisor


# Helpers


class MockActor(Actor):
    def __init__(self, actor_id):
        Actor.__init__(self, "mock-actor-%d" % actor_id)
        self.has_started = False
        self.message = None

    def start(self):
        self.has_started = True

    def receive(self, message):
        self.message = message

    def received(self):
        return self.inbox.qsize() > 0


def test_mock_actor():
    mock1 = MockActor(1)
    assert mock1.name == "mock-actor-1"
    assert mock1.has_started is False

    mock1.start()
    assert mock1.has_started is True

    msg = "test"
    mock1.inbox.put(msg)
    assert mock1.received() is True

    mock1.start()
    print mock1.message


def test_worker_supervisor():
    worker1 = MockActor(1)
    worker2 = MockActor(2)
    worker3 = MockActor(3)
    workers = [worker1, worker2, worker3]

    # supervisor by default uses roundrobin
    # on manually calling recieve I expect work
    # to be evenly distributed.
    supervisor = Supervisor("supervisor", workers)

    # mock actors have convience method if they receive work
    # from the supervisor
    supervisor.receive("test")
    assert worker1.received()

    supervisor.receive("test")
    assert worker2.received()

    supervisor.receive("test")
    assert worker3.received()

# def test_directory_actor():
