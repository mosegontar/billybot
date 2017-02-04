import json
import requests

class SunlightAPI(object):
    """https://sunlightlabs.github.io/congress/"""

    def __init__(self):
        self.domain = 'https://congress.api.sunlightfoundation.com/'
        self.congress = str(self.get_results(self.get_current_congress())[0]['congress'])

    def get_results(self, data):
        return json.loads(data)['results']

    def get_current_congress(self):
        url = self.domain + 'bills'
        resp = requests.get(url)
        return resp.text

    def search_legislators(self, last_name, first_name='', party='', chamber=''):
        query = 'legislators?'\
                'last_name={}&first_name={}&party={}&chamber={}'.format(last_name,
                                                                        first_name, 
                                                                        party, 
                                                                        chamber)
        url = self.domain + query
        resp = requests.get(url)
        return self.get_results(resp.text)

    def get_roll_call_vote(self, roll_id, bioguide_id):
        url = self.domain + 'votes?roll_id={}&fields=voters.{}.vote'.format(roll_id,
                                                                            bioguide_id)
        resp = requests.get(url)
        return self.get_results(resp.text)

    def get_legislator_recent_votes(self, bioguide_id):
        url = self.domain + 'votes?voter_ids.{}__exists=true&per_page=50'.format(bioguide_id)
        resp = requests.get(url)        
        return self.get_results(resp.text)

    def get_all_bill_votes(self, bill_id):
        url = self.domain + 'votes?bill_id={}&per_page=50'.format(bill_id)
        resp = requests.get(url)
        return self.get_results(resp.text)

    def get_official_bill_title(self, bill_id):
        url = self.domain + 'bills?bill_id={}&fields=official_title'.format(bill_id)
        resp = requests.get(url)
        return self.get_results(resp.text)

    def get_short_bill_title(self, bill_id):
        url = self.domain + 'bills?bill_id={}&fields=short_title'.format(bill_id)
        resp = requests.get(url)
        return self.get_results(resp.text)



class LegislatorParser(SunlightAPI):

    def __init__(self, bioguide_id):

        super().__init__()
        self.bioguide_id = bioguide_id

    @staticmethod
    def get_bio_ids(data):
        if not data:
            return None

        if len(data) == 1:
            return data[0]['bioguide_id']
        else:
            return [member['bioguide'] for member in data]


    def parse_roll_call_vote(self, roll_id):
        
        data = self.get_roll_call_vote(roll_id, self.bioguide_id)
        
        try:
            vote = data[0]['voters'][self.bioguide_id]['vote']
        except IndexError:
            return None

        return vote

    def get_most_recent_votes(self):
        pass

class BillParser(SunlightAPI):

    def __init__(self, bill_id, congress=None):
        super().__init__()
        if congress:
            self.congress = congress
        self.bill_id = bill_id
        self.sanitize_bill_id()
        
        self._votes = None
        self._official_title = None
        self._short_title = None

    @property
    def votes(self):
        if not self._votes:
            self._votes = self.get_all_bill_votes(self.bill_id)
        return self._votes

    @property
    def official_title(self):
        if not self._official_title:
            data = self.get_official_bill_title(self.bill_id)
            if not data:
                self._official_title = None
            self._official_title = data[0].get('official_title')
        return self._official_title

    @property
    def short_title(self):
        if not self._short_title:
            data = self.get_short_bill_title(self.bill_id)
            if not data:
                self._short_title = None
            self._short_title = data[0].get('short_title')
        return self._short_title

    def sanitize_bill_id(self):

        if not self.bill_id.endswith('-'+self.congress):
            self.bill_id += '-' + self.congress

        self.bill_id = self.bill_id.lower().replace('.', '')











