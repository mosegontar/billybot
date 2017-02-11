import json
import requests

class SunlightAPI(object):
    """https://sunlightlabs.github.io/congress/"""

    DOMAIN = 'https://congress.api.sunlightfoundation.com/'
    
    def __init__(self):
        self.domain = SunlightAPI.DOMAIN
        self.congress = str(SunlightAPI.get_results(self.get_current_congress())[0]['congress'])

    @staticmethod
    def get_results(data):
        return json.loads(data)['results']

    def get_current_congress(self):
        url = self.domain + 'bills'
        resp = requests.get(url)
        return resp.text

    @classmethod
    def search_legislators(cls, last_name, first_name='', party='', chamber=''):
        query = 'legislators?'\
                'last_name={}&first_name={}&party={}&chamber={}'.format(last_name,
                                                                        first_name, 
                                                                        party, 
                                                                        chamber)
        url = cls.DOMAIN + query
        resp = requests.get(url)
        return SunlightAPI.get_results(resp.text)

    def get_member_data(self, bioguide_id):
        url = self.domain + 'legislators?bioguide_id'.format(bioguide_id)
        resp = requests.get(url)
        return SunlightAPI.get_results(resp.text)

    def get_roll_call_vote(self, roll_id, bioguide_id):
        url = self.domain + 'votes?roll_id={}&fields=voters.{}.vote'.format(roll_id,
                                                                            bioguide_id)
        resp = requests.get(url)
        return SunlightAPI.get_results(resp.text)

    def get_legislator_recent_votes(self, bioguide_id):
        url = self.domain + 'votes?voter_ids.{}__exists=true&per_page=50'.format(bioguide_id)
        resp = requests.get(url)        
        return SunlightAPI.get_results(resp.text)

    def get_bill_data(self, bill_id):
        url = self.domain + 'bills?bill_id={}'.format(bill_id)
        resp = requests.get(url)
        return SunlightAPI.get_results(resp.text)

    def get_all_bill_votes(self, bill_id):
        url = self.domain + 'votes?bill_id={}&per_page=50'.format(bill_id)
        resp = requests.get(url)
        return SunlightAPI.get_results(resp.text)
