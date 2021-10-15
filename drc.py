#!/usr/bin/env python3

''' CLI implementation of DisneylandReservationChecker class'''

import argparse
import sys
from time import sleep
from datetime import date
import util
import disneyland_reservation_checker as drc


def parse_arguments(args):
    ''' Parse command line arguements'''

    parser = argparse.ArgumentParser(
        description=main.__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '-s', '--start', dest='start', required=False,
        default=date.today().strftime('%Y-%m-%d'),
        help='Start date for reservation query as yyyy-mm-dd (default: today)'
    )
    parser.add_argument(
        '-e', '--end', dest='end', required=False,
        help='End date for reservation query as yyyy-mm-dd (default: start)'
    )
    parser.add_argument(
        '-q', '--quiet', dest='stdout', required=False, default=True,
        action='store_const', const=False,
        help='Send output to stdout (default: True)'
    )
    parser.add_argument(
        '--tg', '--telegram', dest='telegram', required=False, default=False,
        action='store_const', const=True,
        help='Send output to telegram (default: False)'
    )

    return parser.parse_args(args)


def notify(calendar, stdout, telegram):
    ''' Send reservation availability status to specified target'''

    if stdout:
        print(calendar)
    if telegram:
        notify_telegram(calendar)


def notify_telegram(calendar):
    ''' Send reservation status to telegram'''

    print('Telegram, one day...')


def main():
    ''' Check reservation availability at Disneyland and California Adventure
    '''

    logger = util.get_logger()
    args = parse_arguments(sys.argv[1:])

    calendar = drc.DisneylandReservationChecker(logger, args.start, args.end)
    while True:
        calendar.refresh()
        calendar.validate()
        notify(calendar, stdout=args.stdout, telegram=args.telegram)
        sleep(30)


if __name__ == '__main__':
    main()