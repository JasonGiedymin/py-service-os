import gevent

from v2.actors import Actor, ActorStates, ActorMessages


class Scheduler(Actor):
    """
    Sample client which sends actors work.
    """
    def __init__(self, name, directory, supervisor):
        Actor.__init__(self, "scheduler")
        self.name = name
        self.directory = directory
        self.state = ActorStates.Idle
        self.greenlet = None
        self.supervisor = supervisor

    def loop(self):
        while self.state == ActorStates.Running:
            gevent.sleep(.5)
            print("...Requesting work...")
            self.supervisor.inbox.put(ActorMessages.Work)

    def ack(self):
        print("\n !! Thanks worker !!\n")

    def receive(self, message):
        if message == ActorMessages.Done:  # message from another actor
            gevent.spawn(self.ack)
        elif message == ActorMessages.Stop:  # message for scheduler
            self.state = ActorStates.Stopped
            if self.greenlet is not None:
                gevent.kill(self.greenlet)
        elif message == ActorMessages.Start:
            print("Requestor starting...")
            self.state = ActorStates.Running
            # supervisor = self.directory.get_actor('supervisor')
            self.greenlet = gevent.spawn(self.loop)


# class Pool(Actor):
#     def __init__(self, n):
#         Actor.__init__(self)
#         self.workers = []
#
#         for i in range(0, n):
#             self.workers.append(Worker("worker-%d" % i))
#
#         self.supervisor = WorkerSupervisor("Supervisor", self.workers)
#         self.requestor = Scheduler('Client')
#
#         directory.add_actor("supervisor", self.supervisor)
#         directory.add_actor("client", self.requestor)
#
#     def start(self):
#         self.requestor.start()
#         self.supervisor.start()
#         self.requestor.inbox.put(ActorMessages.Start)
#         gevent.joinall([self.requestor, self.supervisor])
#
#     def get_actors(self):
#         return [self.requestor, self.supervisor]
#
#
# # If you didn't like pool
# def go():
#     scheduler = Scheduler('Client')
#     worker = Worker("Worker-1")
#     worker2 = Worker("Worker-2")
#     supervisor = WorkerSupervisor("Supervisor", [worker, worker2])
#
#     directory.add_actor("supervisor", supervisor)
#     directory.add_actor("client", scheduler)
#
#     scheduler.start()
#     supervisor.start()
#
#     scheduler.inbox.put(ActorMessages.Start)
#
#     gevent.joinall([scheduler, supervisor])

# directory = Directory()
# gevent.joinall([gevent.spawn(go)])

# pool = Pool(2)  # try 2, 3, 5, 8...
# gevent.joinall([gevent.spawn(pool.start)])
