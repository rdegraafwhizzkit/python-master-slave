import logging


def configure_logging(level=logging.INFO):
    """
    Configure logging

    :param level: log level to set
    """

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=level,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Set log level to warning for some notoriously chatty modules
    for name in [k for k in logging.Logger.manager.loggerDict.keys() if any(['botocore' in k, 'urllib' in k])]:
        logging.getLogger(name).setLevel(logging.WARNING)

    for name in [k for k in logging.Logger.manager.loggerDict.keys() if any(['boto3' in k])]:
        logging.getLogger(name).setLevel(logging.ERROR)
