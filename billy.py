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

    def search_legislators(self, last_name, party='', chamber=''):
        url = self.domain + 'legislators?query={}&party={}&chamber={}'.format(last_name, 
                                                                              party, 
                                                                              chamber)
        resp = requests.get(url)
        return self.get_results(resp.text)

    def get_roll_call_vote(self, roll_id, bioguide_id):
        url = self.domain + 'votes?roll_id={}&fields=voters.{}.vote'.format(roll_id,
                                                                            bioguide_id)
        resp = requests.get(url)
        return self.get_results(resp.text)



class LegislatorParser(SunlightAPI):

    def __init__(self, bioguide_id):

        super().__init__()
        self.bioguide_id = bioguide_id

    @staticmethod
    def get_bio_ids(data):
        return [member['bioguide_id'] for member in data]

    def parse_roll_call_vote(self, roll_id):
        
        data = self.get_roll_call_vote(roll_id, self.bioguide_id)
        
        try:
            vote = data[0]['voters'][self.bioguide_id]['vote']
        except IndexError:
            return None

        return vote

class BillParser(SunlightAPI):

    def __init__(self, bill_id):
        super().__init__()
        self.bill_id = bill_id
        self.sanitize_bill_id()

    def sanitize_bill_id(self):

        if not self.bill_id.endswith('-'+self.congress):
            self.bill_id += '-' + self.congress

        self.bill_id = self.bill_id.lower().replace('.', '')











