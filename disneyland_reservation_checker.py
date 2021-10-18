import logging
import sys
import requests
from datetime import datetime, date
from exceptions import (
    StatusCodeError,
    EmptyResponseError,
)


class DisneylandReservationChecker():
    ''' Check reservation availability at Disneyland and California Adventure
    '''

    BASEURL = 'https://disneyland.disney.go.com/availability-calendar/api/calendar'

    HEADERS = {'User-Agent':
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
               + 'AppleWebKit/537.36 (KHTML, like Gecko) '
               + 'Chrome/91.0.4472.77 Safari/537.36', }

    def __init__(self, start: str = None, end: str = None):
        self.logger = logging.getLogger(__name__)
        self.start = start
        self.end = end
        self.available = None
        self.time = None
        self.payload = {'segment': 'ticket',
                        'startDate': self.start,
                        'endDate': self.end, }
        self.logger.info(f'{type(self).__name__} initialized')
        self.logger.info(f'start:{self.start}')
        self.logger.info(f'end:{self.end}')

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start):
        self.logger.debug(f'raw start:{start}')
        if start:
            start_date = self.cleanse_date_arg(start)
        else:
            start_date = date.today()

        self._start = start_date.strftime('%Y-%m-%d')

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, end):
        self.logger.debug(f'raw end:{end}')
        if end:
            end_date = self.cleanse_date_arg(end)
            self._end = end_date.strftime('%Y-%m-%d')
        else:
            self._end = self.start

    def __str__(self):
        ''' String representation of Disneyland availability calendar object'''

        message = [f'{self.time}', ]
        if self.available:
            park_format = {'DLR_CA': 'CA Adv', 'DLR_DP': 'DisneyLand'}
            for day in self.available:
                park = ' and '.join(day['parks'])
                for key, val in park_format.items():
                    park = park.replace(key, val)
                message += [f'{day["date"]} is available for: {park}', ]
        else:
            message += ['No availability :(', ]

        width = max(map(len, message))
        message = '\n'.join(message)

        return f'{message}\n{"~"*width}'

    @staticmethod
    def cleanse_date_arg(date: str) -> date:
        ''' Cleanse a date string and return a date'''

        try:
            date = datetime.strptime(date, '%Y-%m-%d')
        except ValueError as DateFormatError:
            try:
                date = datetime.strptime(date, '%y-%m-%d')
            except ValueError:
                raise DateFormatError

        return date

    def refresh(self):
        ''' Check the calendar'''

        self.time = datetime.now().strftime('%H:%M:%S')
        self.logger.debug(f'BASEURL:{self.BASEURL}')
        self.logger.debug(f'payload:{self.payload}')
        self.logger.debug(f'HEADERS:{self.HEADERS}')
        self.resp = requests.get(self.BASEURL, params=self.payload,
                                 headers=self.HEADERS)
        self.logger.debug(f'query:{self.resp.url}')
        results = self.resp.json()
        self.logger.debug(f'status_code:{self.resp.status_code}')
        self.logger.debug(f'json:{results}')
        self.available = [result for result in results
                          if result.get('availability') != 'none']

    def validate(self):
        if self.resp.status_code != 200:
            raise StatusCodeError(resp.status_code)
        elif self.resp.text == '[{}]':
            raise EmptyResponseError()
