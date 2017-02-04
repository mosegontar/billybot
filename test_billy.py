import unittest

from billy import SunlightAPI, LegislatorAPI

class TestSunlightAPI(unittest.TestCase):

    def setUp(self):
        self.api = SunlightAPI()

    def test_can_get_most_recent_congress(self):
        self.assertEqual(self.api.congress, 115)           

    def test_able_to_query_legislators_by_name(self):
        data = self.api.get_legislators('Warren')
        matches = [result['last_name'] == 'Warren' for result in data]
        self.assertTrue(any(matches))

    def test_able_to_narrow_resp_data_with_more_params(self):
        data = self.api.get_legislators(last_name='Smith')
        matches = [result['first_name'] == 'Jason' for result in data]
        self.assertTrue(any(matches))
        data = self.api.get_legislators(last_name='Smith', party='D')
        matches = [result['first_name'] == 'Jason' for result in data]
        self.assertFalse(any(matches))    

    def test_can_get_legislator_bio_id(self):
        data = self.api.get_legislators(last_name='Warren')
        self.assertIn('W000817', self.api.get_bio_ids(data))


class TestLegislatorAPI(unittest.TestCase):

    def setUp(self):
        self.api = LegislatorAPI('W000817')

    def test_can_get_particular_roll_call_vote(self):
        vote = self.api.get_roll_call_vote('s26-2017')
        self.assertEqual(vote, 'Nay')
