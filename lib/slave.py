from multiprocessing import Queue, Process
from queue import Empty
import logging
import signal


class Slave(Process):
    """
    Slave process to parallelize
    """

    def __init__(self, in_queue: Queue, out_queue: Queue, timeout: float = 0.1):
        """
        Object initialization

        :param in_queue: The queue to get work from
        :param out_queue: The queue to put results on
        :param timeout: Queue timeout
        :return: Slave object
        """
        super().__init__()
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.timeout = timeout

    def setup(self):
        pass

    def work(self, payload):
        """
        Method to implement

        :param value: the payload to work on
        """
        raise NotImplementedError()

    def teardown(self):
        pass

    def run(self) -> None:
        """
        Entrypoint for the slave process

        """
        # Get the pid and start ignoring SIGINT signals as stopping the process is controlled by the spawning process
        # by means of a poison pill on the incoming queue
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        logging.info(f'Process {self.pid} started')

        self.setup()

        worked = 0
        while True:
            try:
                # Get work from the incoming queue
                value = self.in_queue.get(block=False, timeout=self.timeout)

                # If a poison pill was found, it means all work is done and this process may be ended
                if 'pill' == value.get('poison', ''):
                    logging.info(f'Process {self.pid} received poison pill')
                    break

                try:
                    # Do the work
                    result = self.work(value)
                except Exception as exception:
                    logging.error(f'Exception occurred in pid {self.pid}: {exception}')
                    result = {
                        'pid': self.pid,
                        'result': -1,
                        'error': str(exception)
                    }
                # Perform administration and write the result back on the outgoing queue
                worked += 1
                self.out_queue.put(result)
            except Empty:
                # No work found on the incoming queue
                pass

        self.teardown()

        logging.info(f'Process {self.pid} worked on {worked} items')
