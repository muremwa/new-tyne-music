from datetime import datetime
from pytz import timezone
from re import search

from tyne.settings import TIME_ZONE

tz = timezone(TIME_ZONE)


def is_string_true_or_false(item: str) -> bool:
    """Takes a string and returns whether it's True or False"""
    res = False
    if type(item) == str:
        if item.isdigit():
            item = int(item)
        if item in ['false', 'False']:
            item = 0
        res = bool(item)
    else:
        raise ValueError('Only str allowed')

    return res


def turn_string_to_datetime(string: str) -> datetime:
    if not search(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d+', string):
        raise TypeError('Wrong string format.')

    string_x = string.split(' ')
    date_ = [int(d) for d in string_x[0].split('-')]
    time_ = [int(t) for t in string_x[1].translate(str.maketrans(',', ':')).split(':')]
    return datetime(*date_, *time_, tz)
