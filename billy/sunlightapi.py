import json
import requests

import sunlight
from sunlight.pagination import PagingService

class SunlightAPI(object):
    """https://sunlightlabs.github.io/congress/"""

    DOMAIN = 'https://congress.api.sunlightfoundation.com/'

    def __init__(self):
        self.domain = SunlightAPI.DOMAIN
        self.congress = str(sunlight.congress.upcoming_bills()[0]['congress'])

    @staticmethod
    def get_results(data):
        return json.loads(data)['results']

    @staticmethod
    def get_all_members_of_congress():
        return sunlight.congress.all_legislators_in_office()

    @classmethod
    def search_legislators(cls, **kwargs):
        return sunlight.congress.legislators(**kwargs)

    @classmethod
    def search_legislators_by_zip(cls, zipcode):
        return sunlight.congress.locate_legislators_by_zip(zipcode)

    def get_member_data(self, bioguide_id):
        return sunlight.congress.legislator(bioguide_id)

    def get_bill_data(self, bill_id):
        return sunlight.congress.bill(bill_id=bill_id)

    def get_vote_data(self, roll_id):
        return sunlight.congress.votes(roll_id=roll_id)

    def get_all_bill_votes(self, bill_id):
        paging_congress = PagingService(sunlight.congress)
        return paging_congress.votes(bill_id=bill_id, limit=100)

    # The methods below don't use Python-Sunlight

    def get_roll_call_vote(self, roll_id, bioguide_id):
        url = self.domain + 'votes?roll_id={}&fields=voters.{}.vote'.format(roll_id,
                                                                            bioguide_id)
        resp = requests.get(url)
        return SunlightAPI.get_results(resp.text)

    def get_member_recent_votes(self, bioguide_id):
        url = self.domain + 'votes?voter_ids.{}__exists=true&per_page=50'.format(bioguide_id)
        resp = requests.get(url)
        return SunlightAPI.get_results(resp.text)


