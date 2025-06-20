import logging
from lib import configure_logging
from example_slave import ExampleSlave
from example_master import ExampleMaster

configure_logging(logging.INFO)

if '__main__' == __name__:
    my_master = ExampleMaster(
        ExampleSlave,
        backlog=[{'id': i} for i in range(0, 1000)],
        parallelism=2

    )

    my_master.run()

    print(my_master.results)
