import gevent
from gevent.queue import Queue
from enum import Enum
from gevent import Greenlet

from system.strategies import RoundRobinIndexer


class ActorStates(Enum):
    Idle = 0
    Stopped = 1
    Running = 2
    Failed = 3


class ActorMessages(Enum):
    Start = 0
    Stop = 1
    Done = 2
    Work = 3
    Status = 4


class MessageData:
    def __init__(self, actor_ref, message):
        self.actor_ref = actor_ref
        self.message = message


class ActorMessage:
    def __init__(self, from_actor_ref, message_data):
        self.from_actor_ref = from_actor_ref
        self.message_data = message_data


class Actor(gevent.Greenlet):

    def __init__(self, name):
        self.name = name
        self.inbox = Queue()
        self.running = False  # internal field specifying if this Actor is running
        Greenlet.__init__(self)

    def receive(self, message):
        raise NotImplemented("Be sure to implement this.")

    def _run(self):
        """
        Greenlet execution method.
        """
        self.running = True

        while self.running:
            message = self.inbox.get()
            self.receive(message)

    # TODO: implement Actor.send(), Actor.ask()
    # def send(self, actor, message_data):


class Worker(Actor):
    def __init__(self, name, directory_ref):
        Actor.__init__(self, name)
        self.name = name
        self.directory_ref = directory_ref
        self.state = ActorStates.Idle

    def receive(self, message):
        self.state = ActorStates.Running
        print("I %s was told to do '%s' [%d]" % (self.name, message, self.inbox.qsize()))
        gevent.sleep(3)
        client = self.directory_ref.get_actor("client")
        client.inbox.put(ActorMessages.Done)
        self.state = ActorStates.Idle


class Supervisor(Actor):
    def __init__(self, name, workers):
        Actor.__init__(self, name)
        self.workers = workers
        self.supervisor_strategy = RoundRobinIndexer(len(workers))
        self.state = ActorStates.Idle

    def start(self):
        Actor.start(self)

        for w in self.workers:
            w.start()

    def receive(self, message):
        if -1 == len(self.workers) - 1:
            raise Exception("Supervisor received work but no workers to give it to!")

        index = self.supervisor_strategy.next()
        print("Sending work to worker %s [%d]" % (self.workers[index].name, self.inbox.qsize()))

        self.workers[index].inbox.put(message)
