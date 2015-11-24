import time


def time_me(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        delta = te - ts

        if delta > 1:
            print('%r (%r, %r) in %2.3f seconds.' % (method.__name__, args, kw, delta))
        else:
            print('%r (%r, %r) in %2.3f ms.' % (method.__name__, args, kw, delta * 1000))

        return result

    return timed
