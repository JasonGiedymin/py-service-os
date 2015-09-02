# Ext
import gevent

# Lib
from data.actors import Actor, Directory, WorkerSupervisor, Scheduler, Messages, States, RoundRobinIndexer

# Helpers
import mock


class MockActor(Actor):
    def __init__(self, actor_id):
        Actor.__init__(self)
        self.name = "mock-actor-%d" % actor_id
        self.start = False
        self.message = None

    def start(self):
        self.start = True

    def receive(self, message):
        self.message = message

    def received(self):
        return self.inbox.qsize() > 0


class MockScheduler(Scheduler):
        def __init__(self, name, directory):
            Scheduler.__init__(self, name, directory)
            self.did_ack = False
            self.did_loop = False
            self.supervisor = None

        def ack(self):
            self.did_ack = True

        def loop(self, supervisor):
            self.did_loop = True
            self.supervisor = supervisor


def test_roundrobin():
    # should fail with n <= 1
    try:
        rr = RoundRobinIndexer(1)
    except Exception:
        pass

    # should pass
    rr = RoundRobinIndexer(2)
    assert rr.next() == 0
    assert rr.next() == 1

    rr = RoundRobinIndexer(3)
    assert rr.next() == 0
    assert rr.next() == 1
    assert rr.next() == 2
    assert rr.next() == 0
    assert rr.next() == 1
    assert rr.next() == 2


def test_directory():
    directory = Directory()
    mock_actor_1 = MockActor(1)
    mock_actor_2 = MockActor(2)

    directory.add_actor("mock-actor-1", mock_actor_1)
    directory.add_actor("mock-actor-2", mock_actor_2)

    assert(mock_actor_1 == directory.get_actor("mock-actor-1"))
    assert(mock_actor_2 == directory.get_actor("mock-actor-2"))


def test_worker_supervisor():
    worker1 = MockActor(1)
    worker2 = MockActor(2)
    worker3 = MockActor(3)
    workers = [worker1, worker2, worker3]

    # supervisor by default uses roundrobin
    # on manually calling recieve I expect work
    # to be evenly distributed.
    supervisor = WorkerSupervisor("supervisor", workers)

    # mock actors have convience method if they receive work
    # from the supervisor
    supervisor.receive("test")
    assert worker1.received()

    supervisor.receive("test")
    assert worker2.received()


def test_worker_scheduler():
    curr_supervisor = WorkerSupervisor('supervisor', [MockActor(1), MockActor(2)])

    curr_directory = Directory()
    curr_directory.add_actor('supervisor', curr_supervisor)

    scheduler = MockScheduler("scheduler", curr_directory)

    # -- Test receive() --
    # blocks until greenlet is complete
    # --> Done
    gevent.joinall([gevent.spawn(scheduler.receive, Messages.Done)])
    assert scheduler.did_ack
    # --> Start
    gevent.joinall([gevent.spawn(scheduler.receive, Messages.Start)])
    assert scheduler.state == States.Running
    assert scheduler.did_loop
    assert scheduler.supervisor == curr_supervisor
    # --> Stop
    gevent.joinall([gevent.spawn(scheduler.receive, Messages.Stop)])
    assert scheduler.state == States.Stopped
