from v2.data.queue import MemQueue

__author__ = 'jason'


def test_mem_queue():
    queue = MemQueue()
    assert queue.put_analyze("test1") == 1
    assert queue.put_analyze("test2") == 2

    assert queue.get_analyze() == "test1"
    assert queue.get_analyze() == "test2"
