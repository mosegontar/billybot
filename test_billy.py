import unittest

from billy import SunlightAPI

class TestSunlightAPI(unittest.TestCase):

    def test_can_200_resp_from_sunlight_domain(self):
        api = SunlightAPI()
        resp = api.make_request()
        self.assertEqual(resp.status_code, 200)   
