__author__ = 'jason'

# Lib
from v2.system.os import CannedOS

# Ext
import gevent

# Global Cache
# CacheControl will use DictCache by default


def main():
    """
    Main
    :return:
    """

    token = 'c0698ac78b8f29412f9a358bacd2d34711cdf217'
    headers = {
        'Authorization': "token %s" % token
    }

    os = CannedOS("CannedOS")
    os.bootup()

    def stop():
        os.shutdown()

    stop_event = gevent.spawn_later(2, stop)
    gevent.joinall([os.start(), stop_event])

main()
