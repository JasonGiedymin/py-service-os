import gevent
from gevent.queue import Queue
from enum import Enum
from gevent import Greenlet


class States(Enum):
    Idle = 0
    Stopped = 1
    Running = 2
    Failed = 3


class Messages(Enum):
    Start = 0
    Stop = 1
    Done = 2
    Work = 3


class RoundRobinIndexer:
    def __init__(self, n):
        if n <= 1:
            raise Exception("RoundRobinIndexer count must be > 1")

        self.queue = Queue(maxsize=n)

        for i in range(0, n):
            self.queue.put(i)

    def next(self):
        value = self.queue.get()
        self.queue.put(value)
        return value


class Actor(gevent.Greenlet):

    def __init__(self):
        self.inbox = Queue()
        Greenlet.__init__(self)

    def receive(self, message):
        raise NotImplemented("Be sure to implement this.")

    def _run(self):
        """
        Upon calling run, begin to receive items from actor's inbox.
        """
        self.running = True

        while self.running:
            message = self.inbox.get()
            self.receive(message)


class Scheduler(Actor):
    def __init__(self, name, directory):
        Actor.__init__(self)
        self.name = name
        self.directory = directory
        self.state = States.Idle
        self.greenlet = None

    def loop(self, supervisor):
        while self.state == States.Running:
            gevent.sleep(.5)
            print("...Requesting work...")
            supervisor.inbox.put(Messages.Work)

    def ack(self):
        print("\n !! Thanks worker !!\n")

    def receive(self, message):
        if message == Messages.Done:  # message from another actor
            gevent.spawn(self.ack)
        elif message == Messages.Stop:  # message for scheduler
            self.state = States.Stopped
            if self.greenlet is not None:
                gevent.kill(self.greenlet)
        elif message == Messages.Start:
            print("Requestor starting...")
            self.state = States.Running
            supervisor = self.directory.get_actor('supervisor')
            self.greenlet = gevent.spawn(self.loop, supervisor)


class Worker(Actor):
    def __init__(self, name):
        Actor.__init__(self)
        self.name = name
        self.state = States.Idle

    def receive(self, message):
        self.state = States.Running
        print("I %s was told to do '%s' [%d]" %(self.name, message, self.inbox.qsize()))
        gevent.sleep(3)
        client = directory.get_actor("client")
        client.inbox.put(Messages.Done)
        self.state = States.Idle


class WorkerSupervisor(Actor):
    def __init__(self, name, workers):
        Actor.__init__(self)
        self.name = name
        self.workers = workers
        self.supervisor_strategy = RoundRobinIndexer(len(workers))
        self.state = States.Idle

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


class Directory:
    def __init__(self):
        self.actors = {}

    def add_actor(self, name, actor):
        self.actors[name] = actor

    def get_actor(self, name):
        if name in self.actors:
            return self.actors[name]


class Pool(Actor):
    def __init__(self, n):
        Actor.__init__(self)
        self.workers = []

        for i in range(0, n):
            self.workers.append(Worker("worker-%d" % i))

        self.supervisor = WorkerSupervisor("Supervisor", self.workers)
        self.requestor = Scheduler('Client')

        directory.add_actor("supervisor", self.supervisor)
        directory.add_actor("client", self.requestor)

    def start(self):
        self.requestor.start()
        self.supervisor.start()
        self.requestor.inbox.put(Messages.Start)
        gevent.joinall([self.requestor, self.supervisor])

    def get_actors(self):
        return [self.requestor, self.supervisor]


# If you didn't like pool
def go():
    scheduler = Scheduler('Client')
    worker = Worker("Worker-1")
    worker2 = Worker("Worker-2")
    supervisor = WorkerSupervisor("Supervisor", [worker, worker2])

    directory.add_actor("supervisor", supervisor)
    directory.add_actor("client", scheduler)

    scheduler.start()
    supervisor.start()

    scheduler.inbox.put(Messages.Start)

    gevent.joinall([scheduler, supervisor])

# directory = Directory()
# gevent.joinall([gevent.spawn(go)])

# pool = Pool(2)  # try 2, 3, 5, 8...
# gevent.joinall([gevent.spawn(pool.start)])
