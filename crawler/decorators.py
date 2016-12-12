from functools import wraps


def rateControlled(rateController):
    def rateControlledDecorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            r = func(*args, **kwargs)
            rateController.controlRate(r.headers)
            return r
        return wrapper
    return rateControlledDecorator


def ignoreStatusCodes(statusCodes):
    def ignoreStatusCodesDecorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            while True:
                r = func(*args, **kwargs)
                if r.status_code not in statusCodes:
                    return r
        return wrapper
    return ignoreStatusCodesDecorator
