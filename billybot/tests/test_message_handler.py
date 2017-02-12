import unittest

from billybot.message_handler import VoteQueryMessageHandler


class TestMessageHandler(unittest.TestCase):

    def test_can_import_slack_attachment_config(self):
        import billybot.message_handler as billy_handler
        self.assertEqual(type(billy_handler.slack_attachment), dict)


class TestVoteQueryMessageHandler(unittest.TestCase):

    def create_handler(self, data=None):

        if not data:
            data = {'query': 'Warren',
                    'results': ['Elizabeth Warren (MA)', 'Elizabeth Warren (ME)'],
                    'msg_num': 0}

        handler = VoteQueryMessageHandler(**data)
        return handler

    def test_can_create_handler(self):
        handler = self.create_handler()
        self.assertEqual(handler.query, 'Warren')
        self.assertTrue(len(handler.results) == 2)

    def test_can_get_correct_message(self):
        handler = self.create_handler()
        self.assertEqual(handler.message, "Okay, ")

        data = {'query': 'Warren',
                'results': ['Elizabeth Warren (MA)', 'Elizabeth Warren (ME)'],
                'msg_num': 1}

        handler = self.create_handler(data)

        self.assertTrue(handler.message.startswith('I found multiple matches '))




