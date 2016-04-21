class Dummy:
    """
    Implements a dummy class that is completely inert.
    """

    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, item):
        return self.dummy_function

    def __setattr__(self, key, value):
        pass

    def dummy_function(*args, **kwargs):
        pass
