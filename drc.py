#!/usr/bin/env python3

''' CLI implementation of DisneylandReservationChecker class'''

import argparse
import yaml
import logging.config
import sys
from time import sleep
from datetime import date
import disneyland_reservation_checker as drc


def parse_arguments(args):
    ''' Parse command line arguments'''

    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        '-r', '--refresh-rate', dest='refresh_rate', default=30, type=int,
        help='Reservation status refresh rate in seconds'
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
        help='Surpress output from being sent to stdout (default: False)'
    )
    parser.add_argument(
        '--tg', '--telegram', dest='telegram', required=False, default=False,
        action='store_const', const=True,
        help='Send output to telegram (default: False)'
    )
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='Print verbose output'
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

    # Parse arguments
    args = parse_arguments(sys.argv[1:])

    # Configure logging
    log_conf = 'logging.yaml'
    with open(log_conf) as f:
        config = yaml.safe_load(f)

    if args.verbose == 1:
        config['handlers']['console']['level'] = 'INFO'
    elif args.verbose == 2:
        config['handlers']['console']['level'] = 'DEBUG'
    logging.config.dictConfig(config)

    calendar = drc.DisneylandReservationChecker(args.start, args.end)
    while True:
        calendar.refresh()
        calendar.validate()
        notify(calendar, stdout=args.stdout, telegram=args.telegram)
        sleep(args.refresh_rate)


if __name__ == '__main__':
    main()
