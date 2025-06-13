from lib.master import Master


class ExampleMaster(Master):
    def __init__(self, slave, parallelism: int = -1, backlog: list = None, timeout: float = 0.1):
        super().__init__(slave, parallelism, backlog, timeout)
        self.results = []

    def result(self, result):
        self.results.append(result)
