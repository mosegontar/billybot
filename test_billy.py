import unittest

import billy

class TestSunlightAPI(unittest.TestCase):

    def test_can_get_resp_200(self):
        resp = billy.get_response()
        self.assertEqual(resp.status_code, 200)    
