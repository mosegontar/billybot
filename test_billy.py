import unittest

from billy import SunlightAPI, SunlightParser, LegislatorParser

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.api = SunlightAPI()

class TestSunlightAPI(BaseTestCase): 

    def test_able_to_query_legislators_by_name(self):
        resp = self.api.get_legislators('Warren')
        self.assertIn('Warren', resp.text)

    def test_able_to_narrow_resp_data_with_more_params(self):
        resp = self.api.get_legislators(last_name='Smith')
        self.assertIn('Jason', resp.text)        
        resp = self.api.get_legislators(last_name='Smith', party='D')
        self.assertNotIn('Jason', resp.text)

    def test_can_get_most_recent_congress(self):
        resp = self.api.get_most_recent_congress()
        parser = SunlightParser(resp.text)
        congress = parser.get_most_recent_congress()
        self.assertEqual(congress, 115)


class TestLegislatorParser(BaseTestCase):

    def test_can_get_legislator_bio_id(self):
        resp = self.api.get_legislators(last_name='Warren')
        parser = LegislatorParser(resp.text)
        self.assertIn('W000817', parser.get_bio_ids())

#class TestBillParser(BaseTestCase):

    

