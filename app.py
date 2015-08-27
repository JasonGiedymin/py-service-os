__author__ = 'jason'

# Ext
import requests

# Lib
# from data import limits

# Global Cache
# CacheControl will use DictCache by default


def main():
    """
    Main
    :return:
    """

    session = requests.session()
    # cached_sess = CacheControl(sess)
    # cache_adapter = CacheControlAdapter(cache_etags=True, heuristic=PublicHeuristic())
    # session.mount('https://', cache_adapter)

    # todo: lift token to config
    token = 'c0698ac78b8f29412f9a358bacd2d34711cdf217'
    headers = {
        'Authorization': "token %s" % token
    }

    # https://developer.github.com/v3/activity/events/
    req = session.get('https://api.github.com/events', headers=headers)
    # status = req.status_code
    # etag = req.headers.get('etag')
    # xpoll_interval = req.headers.get('X-Poll-Interval')
    # xrate_limit = req.headers.get('X-RateLimit-Limit')
    # xrate_limit_remaining = req.headers.get('X-RateLimit-Remaining')
    # next_reset = req.headers.get('X-RateLimit-Reset')
    #
    # req_data = limits.Limit(status, etag, xpoll_interval, xrate_limit, xrate_limit_remaining, next_reset)
    # req = session.get('https://api.github.com/events', headers=headers)

    print(req.content)

    # headers['If-None-Match'] = etag
    # req = requests.get('https://api.github.com/events', headers=headers)

    # print req.status_code


main()
