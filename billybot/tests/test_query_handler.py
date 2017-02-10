import unittest

from billybot.query_handler import MessageTriage

class TestVoteQuery(unittest.TestCase):

    def setUp(self):
        self.message = "vote member: Bishop bill: S. Con. Res. 3"
        triage = MessageTriage(self.message)
        self.query = triage.identify_query()
        
    def test_can_correctly_triage_vote_query(self):
        self.assertEqual(repr(self.query), 'VoteQuery({})'.format('member: Bishop bill: S. Con. Res. 3'))

    def test_can_correctly_parse_query(self):
        self.query.parse_query()
        self.assertEqual(self.query.member_query, 'Bishop')
        self.assertEqual(self.query.bill_query, 'S. Con. Res. 3')

    def test_find_member(self):
        self.query.parse_query()
        data = self.query.find_member()
        self.assertTrue(len(data) > 1)  
