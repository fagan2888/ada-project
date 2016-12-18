import time
import sys
import requests


class RateController:
    def __init__(self):
        t = time.time()
        self.windowBegins = {
            10: t,
            600: t,
        }
        self.windowLimits = {
            10: 10,
            600: 500,
        }

    def getLimitCounts(self, countsStr):
        x, y = countsStr.split(',')
        count10 = x.split(':')[0]
        count600 = y.split(':')[0]
        return {
            10 : int(count10),
            600: int(count600),
        }

    def controlRate(self, response):
        status_code = response.status_code
        headers = response.headers
        if 'X-Rate-Limit-Count' not in headers:
            return
        print('Limits:', headers['X-Rate-Limit-Count'], file=sys.stderr)

        limitCounts = self.getLimitCounts(headers['X-Rate-Limit-Count'])
        for (windowSize, count) in limitCounts.items():
            if count == 1:
                self.windowBegins[windowSize] = time.time()
                
        if 'Retry-After' in headers:
            print('Rate limit exceeded!', file=sys.stderr)
            waitTime = int(headers['Retry-After'])
            print('Waiting {} seconds...'.format(waitTime), file=sys.stderr)
            time.sleep(waitTime)

        if status_code == 429 and 'Retry-After' not in headers:
            print('Underlying service raised 429 independently of API infrastracture', file=sys.stderr)
            print('Waiting 1 second...', file=sys.stderr)
            time.sleep(1)

        for (windowSize, count) in limitCounts.items():
            if count >= self.windowLimits[windowSize]:
                windowBegin = self.windowBegins[windowSize]
                waitTime = max(windowBegin + windowSize - time.time(), 0)
                if waitTime > 0:
                    print('Rate limit reached for window{}.'.format(windowSize), file=sys.stderr) 
                    print('Waiting {} seconds...'.format(waitTime), file=sys.stderr)
                    time.sleep(waitTime)

    def get(self, *args, **kwargs):
        r = requests.get(*args, **kwargs)
        print(r.url, r.status_code, file=sys.stderr)
        self.controlRate(r)
        return r
