import sys
import requests
from datetime import datetime, date


class DisneylandReservationChecker():
    ''' Check reservation availability at Disneyland and California Adventure
    '''

    URL = 'https://disneyland.disney.go.com/availability-calendar/api/calendar'

    HEADERS = {'User-Agent':
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
               + 'AppleWebKit/537.36 (KHTML, like Gecko) '
               + 'Chrome/91.0.4472.77 Safari/537.36', }

    def __init__(self, logger=None, start: str = None, end: str = None):
        self.logger = logger
        self.start = start
        self.end = end
        self.available = None
        self.time = None
        self.payload = {'segment': 'ticket',
                        'startDate': self.start,
                        'endDate': self.end, }

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

    @staticmethod
    def check_response(resp):
        code = resp.status_code == 200
        text = resp.text != '[{}]'
        return code & text

    def refresh(self):
        ''' Check the calendar'''

        self.time = datetime.now().strftime('%H:%M:%S')
        self.resp = requests.get(self.URL,
                                 params=self.payload, headers=self.HEADERS)
        results = self.resp.json()
        self.available = [result for result in results
                          if result.get('availability') != 'none']

    def validate(self):
        if not self.check_response(self.resp):
            self.logger.exception('Error retrieving calendar')
            sys.exit(1)
