from timeit import Timer


# Implements a decorator for quick timing of functions.
# Note that this will not provide any return value.
def time_me(count):
    def time_me_decorator(function):
        def function_wrapper(*args, **kwargs):
            t = Timer(lambda: function(*args, **kwargs))
            time = t.timeit(count)

            delta = time / count

            if delta > 1:
                print('%r (%r, %r) | %sx | average %2.3f seconds per run'
                      % (function.__name__, args, kwargs, count, delta))
            else:
                print('%r (%r, %r) | %sx | average %2.3f ms per run'
                      % (function.__name__, args, kwargs, count, delta * 1000))
        return function_wrapper
    return time_me_decorator
