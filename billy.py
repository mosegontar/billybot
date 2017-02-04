import json
import requests

class SunlightAPI(object):
    """https://sunlightlabs.github.io/congress/"""

    def __init__(self):
        self.domain = 'https://congress.api.sunlightfoundation.com/'
        self.data = None

    def get_current_congress(self):
        resp = requests.get(self.domain + 'bills')
        return resp.text 

class SunlightParser(SunlightAPI):

    def __init__(self):
        super().__init__()
        self.data = None
        self.congress = self.get_results(self.get_current_congress())[0]['congress']

    def get_results(self, data):
        return json.loads(data)['results']

class LegislatorAPI(SunlightParser):

    def get_legislators(self, last_name, party='', chamber=''):
        url = self.domain + 'legislators?query={}&party={}&chamber={}'.format(last_name, party, chamber)
        resp = requests.get(url)
        self.data = self.get_results(resp.text)
        return resp     

    def get_bio_ids(self):
        return [member['bioguide_id'] for member in self.data]