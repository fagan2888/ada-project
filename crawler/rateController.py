import time
import sys


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

    def controlRate(self, headers):
        limitCounts = self.getLimitCounts(headers['X-Rate-Limit-Count'])
        for (windowSize, count) in limitCounts.items():
            if count == 1:
                self.windowBegins[windowSize] = time.time()
                
        if 'Retry-After' in headers:
            print('Rate limit exceeded!', file=sys.stderr)
            waitTime = int(headers['Retry-After'])
            print('Waiting {} seconds...'.format(waitTime), file=sys.stderr)
            time.sleep(waitTime)

        for (windowSize, count) in limitCounts.items():
            if count == self.windowLimits[windowSize]:
                windowBegin = self.windowBegins[windowSize]
                waitTime = max(windowBegin + windowSize - time.time(), 0)
                if waitTime > 0:
                    print('Rate limit reached for window{}.'.format(windowSize), file=sys.stderr) 
                    print('Waiting {} seconds...'.format(waitTime), file=sys.stderr)
                    time.sleep(waitTime)
