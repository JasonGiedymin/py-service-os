from v2.data.processors import DataProcessor
from v2.utils.loggers import Logger

__author__ = 'jason'


def test_processor():
    class TestClass(DataProcessor):
        def __init__(self, name, parent_logger):
            DataProcessor.__init__(self, name, parent_logger)
            self.passed = True

    t = TestClass("test-processor", None)
    assert t.log._context["name"] == "processor/test-processor"

    t.log.info("Testing 1, 2, 3...")


def test_processor_with_child_logging():
    class TestClass(DataProcessor):
        def __init__(self, name, parent_logger):
            DataProcessor.__init__(self, name, parent_logger)
            self.passed = True

    root_logger = Logger.get_logger("processor/test-processor")
    t = TestClass("child", root_logger)

    t.log.info("Testing with child logger...")

    assert t.log._context["name"] == "processor/test-processor/child"
