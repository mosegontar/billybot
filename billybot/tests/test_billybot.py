import time
import datetime
import unittest
from unittest.mock import patch, call

from billybot.billybot import MessageTriage


class TestMessageTriage(unittest.TestCase):


    def setUp(self):
        self.thread1 = MessageTriage('USERID1', 'user1', 'Warren', 'testchanl')
        self.thread1.daemon = True
        self.thread2 = MessageTriage('USERID2', 'user2', 'Markey', 'testchanl')
        self.thread2.daemon = True
        self.thread3 = MessageTriage('USERID3', 'user3', 'Capuano', 'testchanl')
        self.thread3.daemon = True

    def test_time_alive(self):

        time.sleep(3)
        time_alive = self.thread1.time_alive

        # Checking that time alive is around 3 but it won't be 3
        # exactly, so we check that it's between 2 and 4
        self.assertTrue(time_alive > 2)
        self.assertTrue(time_alive < 4)

    @patch('billybot.billybot.MessageTriage.run')
    def test_run(self, mock_run):
        mock_run.time_delay = lambda delay: time.sleep(delay)
        mock_run.time_delay(5)
        self.thread1.start()
        self.assertTrue(1 == 2)