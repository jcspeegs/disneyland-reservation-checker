#!/usr/bin/env python3

''' DisneylandReservationChecker tests'''

import unittest
import disneyland_reservation_checker as drc
from datetime import date


class TestCli(unittest.TestCase):
    ''' Test CLI wrapper'''

    def test_start_default(self):
        ''' Test default value of start option is set to today as yyyy-mm-ddd
            when no arguements are passed to applicaiton
        '''

        parser = drc.parse_arguments([])
        calendar = drc.DisneylandReservationChecker(logger=None)
        value = calendar.start

        expected_value = date.today().strftime('%Y-%m-%d')

        message = f'Expected default value:{expected_value} '\
            + f'does not equal actual default value:{parser.start}'
        self.assertEqual(expected_value, value, message)
