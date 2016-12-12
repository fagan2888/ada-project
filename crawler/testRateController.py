from rateControl import RateController


def test():
    r = RateController()
    print(r.windowBegins)
    headers1 = {
        'X-Rate-Limit-Count': '1:10,2:600',
    }
    print(r.getLimitCounts(headers1['X-Rate-Limit-Count']))
    r.controlRate(headers1)
    print(r.windowBegins)
    headers2 = {
            'X-Rate-Limit-Count': '10:10,10:600',
    }
    r.controlRate(headers2)
    headers3 = {
            'Retry-After' : '10',
            'X-Rate-Limit-Count': '10:10,10:600',
    }
    r.controlRate(headers1)
    r.controlRate(headers3)


if __name__ == '__main__':
    test()
