import unittest

from billy.sunlightparsers import MemberParser


class TestMemberParser(unittest.TestCase):

    def setUp(self):
        self.parser = MemberParser

    def test_find_member_by_zip(self):
        results = self.parser.find_member_by_zip('02052')
        self.assertTrue(all([member['state'] == 'MA' for member in results]))

    def test_look_up_all_members_of_congress(self):
        results = self.parser.lookup_members('senate')
        self.assertEqual(len(results), 100)
        results = self.parser.lookup_members('house')
        expected_results = len(self.parser.MEMBERS_OF_CONGRESS) - 100
        self.assertEqual(len(results), expected_results)

    def test_look_up_members_of_congress_from_specified_list(self):
        items = self.parser.find_member_by_zip('02052')
        results = self.parser.lookup_members('senate', items)
        self.assertEqual(len(results), 2)

    def test_formalize_name(self):        
        items = self.parser.find_member_by_zip('02052')
        results = self.parser.lookup_members('Warren', items)
        self.assertEqual(len(results), 1)
        
        member = results[0]
        formalized_name = self.parser.formalize_name(member)
        self.assertEqual(formalized_name, 'Sen. Elizabeth Warren (D-MA)')

    def test_summarize_bio(self):
        items = self.parser.find_member_by_zip('02052')
        members = self.parser.lookup_members('senate', items)
        results = self.parser.summarize_bio(members[0])
        self.assertEqual(len(results), 2)
        self.assertEqual(type(results[0]), str)
        self.assertEqual(type(results[1]), dict)

    def test_find_members(self):
        results = self.parser.find_members('senate D')
        self.assertTrue(len(results) > 2)
        results = self.parser.find_members('senate D', '02052')
        self.assertEqual(len(results), 2)




