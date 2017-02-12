import unittest

from billybot.billybot import MessageTriage
from billybot.vote_query import VoteQuery

class TestVoteQuery(unittest.TestCase):

    def setUp(self):
        message = "vote member: Warren bill: S.Con.Res.3"
        self.errors, self.resp = VoteQuery.query_setup(message)

    def test_query_setup(self):
        self.assertFalse(self.errors)
        self.assertIn("member: Warren bill: S.Con.Res.3", repr(self.resp))

    def test_query_errors(self):
        message = "vote member: Gandalf bill: S.Con.Res.3"
        self.errors, self.resp = VoteQuery.query_setup(message)
        self.assertTrue(self.errors)
        self.assertEqual(self.resp, "Sorry, I wasn't able to find matches for 'Gandalf'")

        message = "vote Gandalf bill: S.Con.Res.3"
        self.errors, self.resp = VoteQuery.query_setup(message)
        self.assertEqual(self.resp, "Sorry, your query is not properly formatted")

    def test_parse_query(self):
        self.assertEqual(self.resp.query_data['member'], 'Warren')
        self.assertEqual(self.resp.query_data['bill_votes'], 'S.Con.Res.3')
