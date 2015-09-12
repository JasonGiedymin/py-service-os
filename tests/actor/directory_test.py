# Ext

# Lib
from system.actors import DirectoryActor


# Helpers


# TODO: use ActorMessage, MessageData and send add actor to directory, maybe like "add me"

def create_directory_actor(name):
    return DirectoryActor(name)


def test_directory_actor():
    d_name = "directory"
    d = create_directory_actor(d_name)
    assert d.name == d_name


    # assert d.name == d_name
