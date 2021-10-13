#!/usr/bin/env python3

''' Tests for drc.py - DisneylandReservationChecker class CLI'''

import unittest
from datetime import date
import drc


class TestCli(unittest.TestCase):
    ''' Test CLI argument passing'''

    def test_start_default(self):
        ''' Test cli default value of start argument is set to today,
            formatted as yyyy-mm-ddd when no arguements are set
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
