import unittest
from django.conf import settings

from staff.logs_processing import log_action_ids, Log, LogMaster


class LogProcessingTestCase(unittest.TestCase):
    def setUp(self):
        self.test_logs = LogMaster(file_name=str(settings.BASE_DIR / 'staff/tests/test_files/test_log.log'))

    def test_log_action_ids(self):
        self.assertEqual(log_action_ids.ADD_STAFF, 'add_staff')
        self.assertEqual(log_action_ids.REMOVE_STAFF, 'remove_staff')
        self.assertEqual(log_action_ids.ADD_TO_GROUP, 'add_to_group')
        self.assertEqual(log_action_ids.REMOVE_FROM_GROUP, 'remove_from_group')
        self.assertEqual(log_action_ids.CREATE_ARTICLE, 'create_article')
        self.assertEqual(log_action_ids.EDIT_ARTICLE, 'edit_article')
        self.assertEqual(log_action_ids.DELETE_ARTICLE, 'delete_article')

    def test_logs_master(self):
        self.assertEqual(len(self.test_logs.logs), 10)
        self.assertEqual(len(self.test_logs.get_logs()), 10)

    def test_log_object(self):
        message = "INFO 2021-08-12 20:58:38,142 ID: remove_staff:muremwa(1) removed kim(4) from staff\n"
        log = Log(
            action_date='2021-08-12',
            action_time='20:58:38,142',
            action_id='remove_staff',
            done_by='muremwa(1)',
            done_to='kim(4)',
            action_receiver=' from staff',
            action_type='removed',
            raw_message=message
        )
        p_log = self.test_logs.p_logs[0]
        self.assertEqual(p_log, log)
        self.assertEqual(log.full_time(), p_log.full_time())


if __name__ == '__main__':
    unittest.main()
