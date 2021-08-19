from typing import List, Dict, Union
from re import search, compile, findall, sub
from datetime import datetime
from dataclasses import dataclass

from django.conf import settings
from django.urls import reverse_lazy

from tyne_utils.funcs import turn_string_to_datetime


@dataclass()
class LogActionIds:
    def __init__(self):
        self.ADD_STAFF = 'add_staff'
        self.REMOVE_STAFF = 'remove_staff'
        self.ADD_TO_GROUP = 'add_to_group'
        self.REMOVE_FROM_GROUP = 'remove_from_group'
        self.CREATE_ARTICLE = 'create_article'
        self.EDIT_ARTICLE = 'edit_article'
        self.DELETE_ARTICLE = 'delete_article'


class Log:
    """This is a log message class"""

    def __init__(self, action_date=None, action_time=None, raw_message=None, action_id=None, done_by=None,
                 done_to=None, action_type=None, action_receiver=None):
        self.action_receiver = action_receiver
        self.action_type = action_type
        self.done_to = done_to
        self.done_by = done_by
        self.action_id = action_id
        self.raw_message = raw_message
        self.clean_message = None
        self.time = None
        self.clean_by = None
        self.clean_to = None
        self.__pk_pattern = compile(r'(?P<pk>\d+)')
        self.__pk_strip_pattern = compile(r'\(\d+\)+')

        if self.raw_message:
            mss = self.raw_message.split(':')
            ms = mss[-1] if len(mss) > 0 else ''
            self.clean_message = sub(r'\(\d+\)+\s', ' ', ms.strip())

        if type(action_time) == str and type(action_date) == str:
            self.time = turn_string_to_datetime(f'{action_date} {action_time}')

        if self.done_by:
            self.clean_by = sub(self.__pk_strip_pattern, ' ', self.done_by)

        if self.done_to:
            self.clean_to = sub(self.__pk_strip_pattern, ' ', self.done_to)

    def full_time(self, tw_4h=True):
        if self.time:
            return self.time.strftime(f"%A %B %d, %Y at {'%H:%M' if tw_4h else '%I:%M %p'}")

    def to_url(self):
        url = ''
        if self.done_to and self.action_id:
            to_pks = search(self.__pk_pattern, self.done_to)
            if to_pks:
                to_pk = to_pks.group('pk')
                url = self.__manufacture_urls(self.action_id, to_pk)
        return url

    def by_url(self):
        url = ''
        if self.done_by and self.action_id:
            by_pks = search(self.__pk_pattern, self.done_by)
            if by_pks:
                by_pk = by_pks.group('pk')
                url = self.__manufacture_urls(self.action_id, by_pk, to=False)
        return url

    @staticmethod
    def __manufacture_urls(action: str, pk: str, to: bool = True) -> str:
        """Create a ur based on the item"""
        url = ''
        user_url = f"{reverse_lazy('staff:staff-view')}?staff-id={str(pk)}"
        article_url = reverse_lazy("staff:help-article", kwargs={"article_pk": str(pk)})

        if 'staff' in action:
            url = user_url

        elif 'article' in action:
            url = article_url if to else user_url

        elif 'group' in action:
            url = user_url

        return url

    def __str__(self):
        return f'Log message from {self.full_time()}'

    def __repr__(self):
        return f'<LogMessage: from \'{self.full_time()}\'>'

    def __eq__(self, other):
        res = False

        if type(other) == type(self):
            exp = [getattr(self, key) == getattr(other, key) for key in self.__dict__.keys()]
            res = all(exp)

        return res


class LogMaster:

    def __init__(self, file_name):
        self.log_file_name = file_name
        self.logs = []
        self.p_logs = []
        self.__raw_logs = []
        self.__log_number_max = 0
        self.__patterns = {
            'date_time': compile(r'(?P<date>\d{4}-\d{2}-\d{2})\s(?P<time>\d{2}:\d{2}:\d{2},\d+)'),
            'action_id': compile(r'ID:\s(\w+):'),
            'done_by': compile(r':(\w+\(\d+\)+)'),
            'done_to': compile(r'[^:]\s(\w+\(\d+\))'),
            'action_type': compile(r':\w+\(\d+\)+\s(.*?)\s\w+\(\d+\)'),
            'action_receiver': compile(r'[^:]\s\w+\(\d+\)(.*?)$'),
        }

        if self.log_file_name:
            self.__load_logs()
            self.__process_logs()

    def __load_logs(self):
        try:
            with open(self.log_file_name, 'r') as file:
                self.__raw_logs = file.readlines()
        except FileNotFoundError:
            pass

    def __process_logs(self):
        for log in self.__raw_logs[self.__log_number_max:]:
            # get log time
            date_time = search(self.__patterns.get('date_time'), log)
            date_time = date_time.groupdict() if date_time else {}

            # get action id
            action_ids = findall(self.__patterns.get('action_id'), log)
            action_id = action_ids[0] if len(action_ids) > 0 else None

            # get done by
            done_bys = findall(self.__patterns.get('done_by'), log)
            done_by = done_bys[0] if len(done_bys) > 0 else None

            # get done to
            done_tos = findall(self.__patterns.get('done_to'), log)
            done_to = done_tos[0] if len(done_tos) > 0 else None

            # get action type
            action_types = findall(self.__patterns.get('action_type'), log)
            action_type = action_types[0] if len(action_types) > 0 else None

            # get action receiver
            action_receivers = findall(self.__patterns.get('action_receiver'), log)
            action_receiver = action_receivers[0] if len(action_receivers) > 0 else None

            log_x = {
                'action_date': date_time.get('date'),
                'action_time': date_time.get('time'),
                'action_id': action_id,
                'action_receiver': action_receiver,
                'action_type': action_type,
                'done_to': done_to,
                'done_by': done_by,
                'raw_message': log,
            }
            self.logs.append(log_x)
            self.p_logs.append(Log(**log_x))
        self.__log_number_max = len(self.logs)

    def get_logs(self, info=False) -> Union[List[Dict], List[Log]]:
        """Retrieve all logs, add arg info=True to get them as a list of dicts else a list of Log objects"""
        self.__load_logs()
        self.__process_logs()
        return self.logs if info else self.p_logs

    def search(self, by: str=None, to: str=None, start_time: datetime=None, end_time: datetime=None,
               action: str=None, user: str=None) -> List[Log]:
        """
        search logs using
        1. name or id of done_by
        2. name or id of done_to
        3. name or id of action receiver
        4. time: start_time, end_time => both need to be datetime.datetime which are timezone aware
        """
        logs = self.get_logs()

        if type(user) == str:
            logs = filter(lambda log: user in log.raw_message, logs)

        else:
            if type(action) == str:
                logs = filter(lambda log: log.action_id == action, logs)

            if type(by) == str:
                logs = filter(lambda log: by in log.done_by, logs)

        if type(to) == str:
            logs = filter(lambda log: to in log.done_to, logs)

        if type(start_time) == datetime and start_time.tzinfo:
            logs = filter(lambda log: log.time > start_time, logs)

        if type(end_time) == datetime and end_time.tzinfo:
            logs = filter(lambda log: log.time < end_time, logs)

        return list(logs)


log_action_ids = LogActionIds()
staff_logs = LogMaster(str(settings.BASE_DIR / 'logs/staff/info_log.log'))
