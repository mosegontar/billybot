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

    def get_roll_call_vote(self, roll_id, bioguide_id):
        url = self.domain + 'votes?roll_id={}&fields=voters.{}.vote'.format(roll_id,
                                                                            bioguide_id)
        resp = requests.get(url)
        return SunlightAPI.get_results(resp.text)

    def get_legislator_recent_votes(self, bioguide_id):
        url = self.domain + 'votes?voter_ids.{}__exists=true&per_page=50'.format(bioguide_id)
        resp = requests.get(url)        
        return SunlightAPI.get_results(resp.text)

    def get_all_bill_votes(self, bill_id):
        url = self.domain + 'votes?bill_id={}&per_page=50'.format(bill_id)
        resp = requests.get(url)
        return SunlightAPI.get_results(resp.text)

    def get_official_bill_title(self, bill_id):
        url = self.domain + 'bills?bill_id={}&fields=official_title'.format(bill_id)
        resp = requests.get(url)
        return SunlightAPI.get_results(resp.text)

    def get_short_bill_title(self, bill_id):
        url = self.domain + 'bills?bill_id={}&fields=short_title'.format(bill_id)
        resp = requests.get(url)
        return SunlightAPI.get_results(resp.text)