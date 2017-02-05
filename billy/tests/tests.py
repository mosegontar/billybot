import unittest

from billy.sunlightapi import SunlightAPI
from billy.sunlightparsers import LegislatorParser, BillParser


class TestSunlightAPI(unittest.TestCase):

    def setUp(self):
        self.api = SunlightAPI()

    def test_can_get_most_recent_congress(self):
        self.assertEqual(self.api.congress, '115')           

    def test_able_to_query_legislators_by_name(self):
        data = self.api.search_legislators('Warren')
        matches = [result['last_name'] == 'Warren' for result in data]
        self.assertTrue(any(matches))

    def test_able_to_narrow_resp_data_with_more_params(self):
        data = self.api.search_legislators(last_name='Smith')
        matches = [result['first_name'] == 'Jason' for result in data]
        self.assertTrue(any(matches))
        data = self.api.search_legislators(last_name='Smith', party='D')
        matches = [result['first_name'] == 'Jason' for result in data]
        self.assertFalse(any(matches))    

    def test_can_get_bio_data(self):
        data = self.api.search_legislators(last_name='Warren')
        query_function, matches = LegislatorParser.get_bio_data(data)
        self.assertTrue(any(['W000817' in item for item in matches]), 
                        "'W000817' not in {}".format(matches))


class TestLegislatorParser(unittest.TestCase):

    def setUp(self):
        self.api = LegislatorParser('W000817')

    def test_can_get_particular_roll_call_vote(self):
        vote = self.api.parse_roll_call_vote('s26-2017')
        self.assertEqual(vote, 'Nay')

    def test_return_None_if_roll_call_vote_not_found(self):
        vote = self.api.parse_roll_call_vote('x26-2017')
        self.assertEqual(vote, None)

class TestBillParser(unittest.TestCase):

    def setUp(self):
        self.bill = BillParser('S.Con.Res.3')

    def test_sanitize_bill_id_if_congress_left_out(self):
        self.assertEqual(self.bill.bill_id, 'sconres3-115')

    def test_sanitize_bill_id_if_congress_included(self):
        self.bill.bill_id = 'S.Con.Res.3-115'
        self.bill.sanitize_bill_id()
        self.assertEqual(self.bill.bill_id, 'sconres3-115')

    def test_get_roll_call_votes_for_bill(self):
        self.assertEqual(len(self.bill.votes), 28)

    def test_get_official_title(self):
        expected_title = "A concurrent resolution setting forth the congressional budget for the United States Government for fiscal year 2017 and setting forth the appropriate budgetary levels for fiscal years 2018 through 2026."
        self.assertEqual(self.bill.official_title, expected_title)

    def test_official_title(self):
        self.bill = BillParser('H.R.72')
        self.assertFalse(self.bill._official_title)
        self.assertEqual(self.bill.official_title, 'To ensure the Government Accountability Office has adequate access to information.')
        self.assertTrue(self.bill._official_title)

    def test_short_title(self):
        self.bill = BillParser('H.R.72')
        self.assertFalse(self.bill._short_title)
        self.assertEqual(self.bill.short_title, 'GAO Access and Oversight Act of 2017')
        self.assertTrue(self.bill._short_title)




