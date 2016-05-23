ports = {
    'database': 31337,
    'worker1': 31415,
    'worker2': 27182,
    'worker3': 60221
}


def lookup(process, id):
    """
    Return a Pyro URI based on given ID and process.
    :param process: The process name.
    :param id: The ID of the desired object.
    :return: A URI.
    """

    port = ports[process]
    uri = 'PYRO:{}@localhost:{}'.format(id, port)

    return uri