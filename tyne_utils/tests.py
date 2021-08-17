from unittest import TestCase
from datetime import datetime
from pytz import timezone

from .funcs import is_string_true_or_false, turn_string_to_datetime


class UtilsTestCase(TestCase):
    def test_is_string_true_or_false(self):
        self.assertTrue(is_string_true_or_false('1'))
        self.assertTrue(is_string_true_or_false('3'))
        self.assertTrue(is_string_true_or_false('-1'))
        self.assertFalse(is_string_true_or_false('false'))
        self.assertFalse(is_string_true_or_false('False'))
        self.assertFalse(is_string_true_or_false('0'))
        self.assertFalse(is_string_true_or_false(''))
        with self.assertRaisesRegex(ValueError, 'Only str allowed'):
            is_string_true_or_false(1)

    def test_turn_string_to_datetime(self):
        t_str = '2020-08-10 12:14:30,283'
        with self.assertRaisesRegex(TypeError, 'Wrong string format.'):
            turn_string_to_datetime('2020-08-10 12:14:30')

        p_time = turn_string_to_datetime(t_str)
        m_time = datetime(2020, 8, 10, 12, 14, 30, 283, timezone('Africa/Nairobi'))
        self.assertEqual(p_time.tzinfo, m_time.tzinfo)
        self.assertEqual(p_time.date(), m_time.date())
        self.assertEqual(p_time.time(), m_time.time())
