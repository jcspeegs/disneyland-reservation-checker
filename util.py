''' Disneyland Reservation Checker Utilities'''

import logging
import sys


def get_logger():
    ''' Get logger'''

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Console handler
    console_format = logging.Formatter(
        '%(asctime)s:%(levelname)s:%(name)s:%(lineno)d:%(message)s')
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(console_format)

    # Add handler(s) to logger
    logger.addHandler(console_handler)

    return logger
