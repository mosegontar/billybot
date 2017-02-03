import unittest

import billy

class TestSunlightAPI(unittest.TestCase):

    def test_can_get_resp_200(self):
        resp = billy.getresponse()
        self.assertEqual(resp.status, 200)    
