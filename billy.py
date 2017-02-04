import json
import requests

class SunlightAPI(object):
    """https://sunlightlabs.github.io/congress/"""

    def __init__(self):
        self.domain = 'https://congress.api.sunlightfoundation.com/'

    def get_current_congress(self):
        resp = requests.get(self.domain + 'bills')
        return resp.text

    def get_legislators(self, last_name, party='', chamber=''):
        url = self.domain + 'legislators?query={}&party={}&chamber={}'.format(last_name, party, chamber)
        resp = requests.get(url)
        return resp  

class SunlightParser(SunlightAPI):

    def __init__(self, json_data):
        super().__init__()
        self.data = self.get_results(json_data)
        self.congress = self.get_results(self.get_current_congress())[0]['congress']

    def get_results(self, data):
        return json.loads(data)['results']

class LegislatorParser(SunlightParser):

    def get_bio_ids(self):
        return [member['bioguide_id'] for member in self.data]