__author__ = 'jason'


from limits import Limit


class GHRequestEngine:
    """
    Basic GitHub request engine.
    """

    def __init__(self, session):
        self.session = session

        # Cache to store data
        self.cache = {}

        # Markers used in operation
        self.limit = Limit()

    def get(self, url):
        resp = self.session.get(url)
        self.limit = Limit(resp)
        return resp
