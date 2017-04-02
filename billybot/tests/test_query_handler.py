import unittest

from billy.sunlightparsers import MemberParser
from billybot.message_handler import ContactQueryMessageHandler
from billybot.query_handler import MemberQuery


class TestMemberQuery(unittest.TestCase):

    def test_narrow_results_by_keyword(self):
        data = MemberParser.find_members('D', '02052')
        query = MemberQuery(ContactQueryMessageHandler)
        query._query_results = data
        matches = query._narrow_results('Elizabeth')
        self.assertEqual(len(matches), 1)
        self.assertTrue(matches[0][0], "Sen. Elizabeth Warren (D-MA)")

    def test_validate_results(self):
        data = MemberParser.find_members('D', '02052')
        query = MemberQuery(ContactQueryMessageHandler)
        query._query_results = data

        valid, found = query._validate_results()
        self.assertTrue(valid)
        self.assertFalse(found)

    def test_initialize_results_without_zipcode(self):

        query = MemberQuery(ContactQueryMessageHandler)
        query._initialize_results('Elizabeth')
        self.assertTrue(len(query._query_results) > 1)
        self.assertTrue(all(['Elizabeth' in member[0]
                        for member in query._query_results]))

    def test_initialize_results_with_zipcode(self):

        query = MemberQuery(ContactQueryMessageHandler)
        query._initialize_results('Elizabeth 02052')
        self.assertEqual(len(query._query_results), 1)

    def test_extract_results(self):

        query = MemberQuery(ContactQueryMessageHandler)
        query._initialize_results('Elizabeth 02052')
        self.assertEqual(query.member_summary, None)
        query._extract_results()
        self.assertEqual(query.member_summary, "Sen. Elizabeth Warren (D-MA)")
        self.assertTrue(type(query.member_data) == dict)
