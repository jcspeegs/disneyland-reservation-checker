#!/usr/bin/env python3

''' DisneylandReservationChecker tests'''

import unittest
import disneyland_reservation_checker as drc
from datetime import date
import requests


class TestCli(unittest.TestCase):
    ''' Test CLI wrapper'''

    def test_start_default(self):
        ''' Test cli wrapper default value of start option is set to today as yyyy-mm-ddd
            when no arguements are passed to applicaiton
        '''

        parser = drc.parse_arguments([])
        value = parser.start
        expected_value = date.today().strftime('%Y-%m-%d')

        message = f'Expected default value:{expected_value} '\
            + f'does not equal actual default value:{parser.start}'
        self.assertEqual(expected_value, value, message)

    def test_start(self):
        ''' Test cli wrapper start argument passes correctly'''

        parser = drc.parse_arguments(['-s', '2021-12-12'])
        value = parser.start
        expected_value = '2021-12-12'

        message = f'Expected value:{expected_value} '\
            + f'does not equal actual value:{value}'
        self.assertEqual(expected_value, value, message)

    def test_end(self):
        ''' Test cli wrapper end argument passes correctly'''

        parser = drc.parse_arguments(['-e', '2021-12-12'])
        value = parser.end
        expected_value = '2021-12-12'

        message = f'Expected value:{expected_value} '\
            + f'does not equal actual value:{value}'
        self.assertEqual(expected_value, value, message)


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
