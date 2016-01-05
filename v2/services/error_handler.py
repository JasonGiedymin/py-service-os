from abc import ABCMeta, abstractmethod

from v2.system.exceptions import HandlerException
from v2.system.states import BaseStates


class ErrorHandler(object):
    def __init__(self):
        self.log = None

    def set_logger(self, logger):
        self.log = logger

    @abstractmethod
    def next(self, service_meta):
        """
        Method MUST return the service_meta object
        :param service_meta:
        :return:
        """
        raise NotImplementedError("Please Implement this method")


class ErrorHandlerFactory:
    def __init__(self):
        pass

    @staticmethod
    def create(error_handler_class, parent):
        """
        Note: the buck stops here at the Error Handler, so it must work.
              The code must run correctly, so test it!
        :param error_handler_class:
        :param parent:
        :return:
        """

        handler = error_handler_class()  # the handler after construction
        handler_cls_name = handler.__class__.__name__  # classname of handler
        parent_logger = parent.log  # logger we'll use from parent
        unique_name = parent.unique_name  # also need the parent's unique name

        # create name for handler that we'll use in the logs
        error_handler_name = "%s/error-handlers/%s" % (unique_name, handler_cls_name)

        handler.set_logger(parent_logger.bind(name=error_handler_name, handler=handler_cls_name))

        return handler


class ErrorHandlerMixin:
    """
    Must be mixed in with a BaseService.
    Note: priority order is reversed, right to left.
    """
    def __init__(self):
        self.error_handlers = []

    def add_error_handler(self, handler):
        self.error_handlers.append(handler)
        return len(self.error_handlers)

    def add_error_handler_class(self, handler_class):
        """
        Add the following error handlers to this service.
        :param handler_class: a class which represents an error handler to create and attach to this service.
        :return:
        """
        return self.add_error_handler(ErrorHandlerFactory.create(handler_class, self))

    def add_error_handlers(self, handler_classes):
        """
        Add the following list of error handlers to this service.
        :param handler_classes: a list of classes which are error handlers that will be
                                created and attach to this service.
        :return:
        """
        handlers = 0
        for handler_class in handler_classes:
            handlers = self.add_error_handler_class(handler_class)

        return handlers

    def handle_error(self):
        service_meta = self.get_directory_service_proxy().get_service_meta(self.alias)

        self.log.debug("running error handlers...")

        for handler in self.error_handlers:
            try:
                service_meta = handler.next(service_meta)
            except Exception as ex:
                # Note: this log entry will origininate from a service, so the name will reflect as such,
                #       NOT from a handler. Don't expect to see this entry's name be that of a handler.
                #       Remember that this is a mixin to a service!
                self.log.error("Exception occurred while trying to execute error handler routine. Inner exception: [%s]"
                               % ex,
                               handler=handler.__class__.__name__,
                               handler_parent=self.unique_name)
                self.set_state(BaseStates.Stopped)  # set to stop whatever service it is
                raise HandlerException(ex)

        self.log.debug("error handlers complete")

        return service_meta
