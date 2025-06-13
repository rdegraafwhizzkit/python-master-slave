from lib.slave import Slave, Queue
from boto3 import client


class ExampleSlave(Slave):

    def __init__(self, in_queue: Queue, out_queue: Queue, timeout: float = 0.1):
        super().__init__(in_queue, out_queue, timeout)
        self.client = None

    def setup(self):
        self.client = self.client or client('s3')

    def work(self, payload):
        return {
            'pid': self.pid,
            'result': 0
        } | payload
