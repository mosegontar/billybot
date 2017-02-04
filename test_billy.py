import unittest

from billy import LegislatorAPI

class TestLegislatorAPI(unittest.TestCase):

    def setUp(self):
        self.api = LegislatorAPI()

    def test_able_to_query_legislators_by_name(self):
        resp = self.api.get_legislators('Warren')
        self.assertIn('Warren', resp.text)

    def test_able_to_narrow_resp_data_with_more_params(self):
        resp = self.api.get_legislators(last_name='Smith')
        self.assertIn('Jason', resp.text)        
        resp = self.api.get_legislators(last_name='Smith', party='D')
        self.assertNotIn('Jason', resp.text)    

    def test_can_get_legislator_bio_id(self):
        self.api.get_legislators(last_name='Warren')
        self.assertIn('W000817', self.api.get_bio_ids())

    def test_can_get_most_recent_congress(self):
        self.api.get_legislators(last_name='Warren')
        self.assertEqual(self.api.congress, 115)        

#class TestBillParser(BaseTestCase):

    

