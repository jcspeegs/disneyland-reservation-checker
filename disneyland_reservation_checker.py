#!/usr/bin/env python3

import logging
import argparse
import sys
import requests
from datetime import datetime, date
from time import sleep


class DisneylandReservationChecker():
    ''' Check reservation availability at Disneyland and California Adventure
    '''

    url = 'https://disneyland.disney.go.com/availability-calendar/api/calendar'

    def __init__(self, logger, start: str = None, end: str = None):
        self.logger = logger
        self.start = start
        self.end = end
        self.available = None
        self.time = None

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start):
        if start:
            self._start = start
        else:
            self._start = date.today().strftime('%Y-%m-%d')

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, end):
        if end:
            self._end = end
        else:
            self._end = self.start

    def __str__(self):
        ''' String representation of Disneyland availability calendar object'''

        message = [f'{self.time}', ]
        if self.available:
            for day in self.available:
                park = ' and '.join(day['parks'])
                message += [f'{day["date"]} is available for: {park}', ]
        else:
            message += ['No availability :(', ]

        width = max(map(len, message))
        message = '\n'.join(message)

        return f'{message}\n{"~"*width}'

    def refresh(self):
        ''' Check the calendar'''
        payload = {'segment': 'ticket',
                   'startDate': self.start,
                   'endDate': self.end,
                   }
        headers = {'User-Agent':
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                   + 'AppleWebKit/537.36 (KHTML, like Gecko) '
                   + 'Chrome/91.0.4472.77 Safari/537.36',
                   }

        time = datetime.now().strftime('%H:%M:%S')

        resp = requests.get(self.url, params=payload, headers=headers)

        if resp.status_code != 200:
            self.logger.exception('Error retrieving calendar')
            sys.exit(1)

        results = resp.json()

        available = [result for result in results
                     if result.get('availability') != 'none']

        self.time = time
        self.available = available

    def notify(self, stdout=False, telegram=False):
        ''' Send reservation availability status to specified target'''

        if stdout:
            self.notify_stdout()
        elif telegram:
            self.notify_telegram()

    def notify_stdout(self):
        ''' Send reservation status to stdout'''

        print(self)

    def notify_telegram(self):
        ''' Send reservation status to telegram'''

        pass


def get_logger():
    ''' Get logger'''

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Console handler
    console_format_string = \
        '%(asctime)s:%(levelname)s:%(name)s:%(lineno)d:%(message)s'
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(console_format_string)

    # Add handler(s) to logger
    logger.addHandler(console_handler)

    return logger


def parse_arguments(args):
    ''' Parse command line arguements'''

    parser = argparse.ArgumentParser(
        description=main.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '-s', '--start', dest='start', required=False,
        help='Check Disneyland for availability starting on this date')
    parser.add_argument(
        '-e', '--end', dest='end', required=False,
        help='Check Disneyland for availability until this date')

    return parser.parse_args(args)


def main():
    ''' Check reservation availability at Disneyland and California Adventure

        Arguments:
           -s, --start  Starting date for reservation query as yyyy-mm-dd
                        (default: today)
           -e, --end    End date for reservation query as yyyy-mm-dd
                        (default: start)
    '''

    logger = get_logger()
    args = parse_arguments(sys.argv[1:])

    calendar = DisneylandReservationChecker(logger, args.start, args.end)
    while True:
        calendar.refresh()
        calendar.notify(stdout=True)
        sleep(30)


if __name__ == '__main__':
    main()
