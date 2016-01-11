# Ext

# Lib
from system.actors.directory import DirectoryActor


# Helpers


def create_directory_actor(name):
    return DirectoryActor(name)


def test_directory_actor():
    d_name = "directory"
    d = create_directory_actor(d_name)
    assert d.name == d_name


    # assert d.name == d_name
