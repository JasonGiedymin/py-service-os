__author__ = 'jason'

from enum import Enum
from v2.actors import Actor, ActorMessages


class Directory:
    def __init__(self):
        self.actors = {}

    def add_actor(self, name, actor):
        self.actors[name] = actor

    def get_actor(self, name):
        if name in self.actors:
            return self.actors[name]


class DirectoryMessages(Enum):
    GetActor = 0
    GetActors = 1


class DirectoryActor(Actor):
    def __init__(self, name):
        Actor.__init__(self, name)
        self.directory = Directory()

    def receive(self, message):
        if message == ActorMessages.Status:
            print "good"
