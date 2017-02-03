import requests


class SunlightAPI(object):
    """https://sunlightlabs.github.io/congress/"""

    def __init__(self):
        self.domain = 'https://congress.api.sunlightfoundation.com/'

    def make_request(self):
        resp = requests.get(self.domain)
        return resp
