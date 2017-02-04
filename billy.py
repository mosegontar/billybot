import json
import requests

class SunlightAPI(object):
    """https://sunlightlabs.github.io/congress/"""

    def __init__(self):
        self.domain = 'https://congress.api.sunlightfoundation.com/'
        self.congress = self.get_results(self.get_current_congress())[0]['congress']

    def get_results(self, data):
        return json.loads(data)['results']

    def get_current_congress(self):
        resp = requests.get(self.domain + 'bills')
        return resp.text

    def get_legislators(self, last_name, party='', chamber=''):
        url = self.domain + 'legislators?query={}&party={}&chamber={}'.format(last_name, 
                                                                              party, 
                                                                              chamber)
        resp = requests.get(url)
        return self.get_results(resp.text)

    def get_bio_ids(self, data):
        return [member['bioguide_id'] for member in data]    

class LegislatorAPI(SunlightAPI):

    def __init__(self, bioguide_id):
        super().__init__()
        self.bioguide_id = bioguide_id

    def get_roll_call_vote(self, roll_id):
        url = self.domain + 'votes?roll_id={}&fields=voters.{}.vote'.format(roll_id,
                                                                             self.bioguide_id)
        resp = requests.get(url)
        data = self.get_results(resp.text)
        vote = data[0]['voters'][self.bioguide_id]['vote']
        return vote





