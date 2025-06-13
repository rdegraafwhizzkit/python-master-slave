import logging
import signal
from multiprocessing import Queue, cpu_count
from queue import Empty


class Master():
    def __init__(self, slave, parallelism: int = -1, backlog: list = None, timeout: float = 0.1):
        self.running = True
        signal.signal(signal.SIGINT, self.exit_gracefully)

        self.slave = slave
        self.backlog = backlog or []
        self.timeout = timeout
        self.parallelism = max(parallelism, cpu_count() - 1)

        # Create the work- and result-queue
        self.work_queue = Queue()  # The master process puts work items on this queue
        self.result_queue = Queue()  # The master process gets results on this queue

    def result(self, result):
        pass

    def run(self):
        processes = []
        # Start the worker processes
        logging.info(f'Starting {self.parallelism} decrypter processes')
        for _ in range(0, self.parallelism):
            processes.append(self.slave(
                in_queue=self.work_queue,
                out_queue=self.result_queue,
                timeout=self.timeout
            ))
            processes[len(processes) - 1].start()

        # At this point, the worker processes are ready to start receiving 'work'
        working = 0
        done = 0
        to_be_done = len(self.backlog)
        modulo = int(to_be_done / 100)
        logging.info(f'Starting to work on {to_be_done} items')

        # Start looping while there is still work to be done and CTRL-C is not pressed
        while done < to_be_done and self.running:

            # Send a new work item if there are inactive workers and there is still work to be done
            if working < self.parallelism and len(self.backlog) > 0:
                self.work_queue.put(self.backlog.pop())
                working += 1

            try:
                # Try to get a result item from the queue
                result = self.result_queue.get(block=False, timeout=self.timeout)
                logging.debug(f'Process {result["pid"]} finished some work')
                self.result(result)
                working -= 1
                done += 1
                if 0 != modulo and 0 == done % modulo:
                    logging.info(f'Progress: {100 * done / to_be_done:.0f}%')
            except Empty:
                # No item found on the result queue, which is ok
                pass
            except Exception as exception:
                logging.error(f'{exception.__class__.__name__}: {exception}')
                self.running = False

        # No more work or shutdown requested. Send a special work item so the spawned processes can stop gracefully
        for _ in range(0, self.parallelism):
            self.work_queue.put({'poison': 'pill'})

        # Wait for all the processes to have stopped
        for process in processes:
            process.join()

        logging.info('Finished working')

    def exit_gracefully(self, s, f):
        """
        Signal handler that sets the global run variable to false so spawned processes can be stopped

        :param s: Signal number
        :param f: Stack frame

        :return: None
        """
        logging.info(f'Received {s}/{f}')
        self.running = False
