import json
import requests

class SunlightParser(object):

    def __init__(self, json_data):
        self.data = json.loads(json_data)['results']

    def get_most_recent_congress(self):
        return self.data[0]['congress']

class LegislatorParser(SunlightParser):

    def get_bio_ids(self):
        return [member['bioguide_id'] for member in self.data]

class SunlightAPI(object):
    """https://sunlightlabs.github.io/congress/"""

    def __init__(self):
        self.domain = 'https://congress.api.sunlightfoundation.com/'
        self.congress = self.get_most_recent_congress()

    def get_most_recent_congress(self):
        resp = requests.get(self.domain + 'bills')
        return resp

    def get_legislators(self, last_name, party='', chamber=''):
        url = self.domain + 'legislators?query={}&party={}&chamber={}'.format(last_name, party, chamber)
        resp = requests.get(url)
        return resp  

