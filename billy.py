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

   
class BillParser(SunlightAPI):

    def __init__(self, bill_id, congress=None):
        super().__init__()
        if congress:
            self.congress = congress
        self.bill_id = bill_id
        self.sanitize_bill_id()
        
        # Get data on first request to avoid unnecessary API calls
        self._votes = None
        self._official_title = None
        self._short_title = None

    def sanitize_bill_id(self):

        if not self.bill_id.endswith('-'+self.congress):
            self.bill_id += '-' + self.congress

        # Turn bill_id into proper format for Sunlight lookup:
        # E.g.: "S. Con. Res. 3." => "sconres3-115"
        self.bill_id = self.bill_id.lower().replace(' ', '').replace('.', '')

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


class LegislatorParser(SunlightAPI):

    def __init__(self, bioguide_id):

        super().__init__()
        self.bioguide_id = bioguide_id
        self._recent_votes = None

    @staticmethod
    def get_bio_data(data):

        if not data:
            return None

        if len(data) == 1:
            return data[0]['bioguide_id']
        else:
            return [(member.first_name, member.last_name, member['bioguide']) for member in data]

    @property
    def recent_votes(self):
        if not self._recent_votes:
            self._recent_votes = self.get_legislator_recent_votes(self.bioguide_id)
        return self._recent_votes

    def parse_roll_call_vote(self, roll_id):
        
        data = self.get_roll_call_vote(roll_id, self.bioguide_id)
        
        try:
            vote = data[0]['voters'][self.bioguide_id]['vote']
        except IndexError:
            return None

        return vote

class UserInterface(object):

    def main(self):
        billquery = input('Which bill would you like to look up?\n')
        bill = BillParser(billquery)
        title = bill.short_title if bill.short_title else bill.official_title
        if len(bill.votes) > 1:
            response = input('There were many bills associated with {}, {}\n See them all? y/n'.format(bill.bill_id, title))
            if response.lower() == 'y':
                for v in bill.votes:
                    print(v['roll_id']+': '+v['question'])
        vote = input('Pick: ').lower()
        query = input('Would you like to look up how a particular congress member voted? y/n')
        if query.lower() == 'y':
nose            name = input('Name: ').replace('.', '')
            results = SunlightAPI.search_legislators(last_name=name)
            bio_id = LegislatorParser.get_bio_ids(results)
            if type(bio_id) == list:
                print('Found more than one match. Select one by entering their bio_id:\n')
                for i in bio_id:
                    print(i)
                bio_id = input('> ')
            member = LegislatorParser(bio_id)
            print(member.parse_roll_call_vote(vote))




if __name__=='__main__':
    ui = UserInterface()
    ui.main()

