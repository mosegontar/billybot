import unittest

from billy import SunlightAPI, LegislatorParser, BillParser


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

    def test_can_get_legislator_bio_id(self):
        data = self.api.search_legislators(last_name='Warren')
        self.assertIn('W000817', LegislatorParser.get_bio_ids(data))


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
        self.api = BillParser('S.Con.Res.3')

    def test_sanitize_bill_id_if_congress_left_out(self):
        self.assertEqual(self.api.bill_id, 'sconres3-115')

    def test_sanitize_bill_id_if_congress_included(self):
        self.api.bill_id = 'S.Con.Res.3-115'
        self.api.sanitize_bill_id()
        self.assertEqual(self.api.bill_id, 'sconres3-115')

    def test_get_roll_call_votes_for_bill(self):
        votes = self.api.parse_bill_votes()
        self.assertEqual(len(votes), 28)

    def test_get_official_title(self):
        expected_title = "A concurrent resolution setting forth the congressional budget for the United States Government for fiscal year 2017 and setting forth the appropriate budgetary levels for fiscal years 2018 through 2026."
        self.assertEqual(self.api.official_title, expected_title)

