#!/usr/bin/env python3

''' DisneylandReservationChecker tests'''

import unittest
import disneyland_reservation_checker as drc
from datetime import date


class TestInitOptions(unittest.TestCase):
    ''' Test class initialization options'''

    def test_start_default(self):
        ''' Test default start option value during class initialization'''

        calendar = drc.DisneylandReservationChecker()
        value = calendar.start
        expected_value = date.today().strftime('%Y-%m-%d')

        message = f'Expected default value:{expected_value} '\
            + f'does not equal actual default value:{value}'
        self.assertEqual(expected_value, value, message)

    def test_start(self):
        ''' Test start argument passes correctly'''

        calendar = drc.DisneylandReservationChecker(start='2021-12-21')
        value = calendar.start
        expected_value = '2021-12-21'

        message = f'Expected value:{expected_value} '\
            + f'does not equal actual value:{value}'
        self.assertEqual(expected_value, value, message)

    def test_end(self):
        ''' Test end argument passes correctly during class initialization'''

        calendar = drc.DisneylandReservationChecker(end='2021-12-21')
        value = calendar.end
        expected_value = '2021-12-21'

        message = f'Expected value:{expected_value} '\
            + f'does not equal actual value:{value}'
        self.assertEqual(expected_value, value, message)


class TestResponse(unittest.TestCase):
    ''' Test API response'''

    def test_invalid_start_parameter(self):
        start = 'asdf'
        calendar = drc.DisneylandReservationChecker(start=start)
        calendar.refresh()
        message = f'Start parameter:{start} should not be valid.'
        self.assertFalse(calendar.check_response(calendar.resp), message)

    def test_valid_start_parameter(self):
        start = date.today().strftime('%Y-%m-%d')
        calendar = drc.DisneylandReservationChecker(start=start)
        calendar.refresh()
        message = f'Start parameter:{start} should be valid.'
        self.assertTrue(calendar.check_response(calendar.resp), message)
