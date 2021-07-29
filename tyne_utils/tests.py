from unittest import TestCase

from .funcs import is_string_true_or_false


class UtilsTestCase(TestCase):
    def test_is_string_true_or_false(self):
        self.assertTrue(is_string_true_or_false('1'))
        self.assertTrue(is_string_true_or_false('3'))
        self.assertTrue(is_string_true_or_false('-1'))
        self.assertTrue(is_string_true_or_false('false'))
        self.assertFalse(is_string_true_or_false('0'))
        self.assertFalse(is_string_true_or_false(''))
        with self.assertRaisesRegex(ValueError, 'Only str allowed'):
            is_string_true_or_false(1)
