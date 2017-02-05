from sunlightapi import SunlightAPI

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

    @classmethod
    def summarize_bio(cls, bio):
        """Receives full Legislator bio and returns summary tuple"""
        return (bio['first_name'], bio['last_name'], bio['bioguide_id'])

    @classmethod
    def get_bio_data(cls, data):

        if not data: 
            return None

        def query_bio(bio_id, requests):
            full_bio = next((bio for bio in data if bio.get('bioguide_id') == bio_did))
            requested_data = [(req.title(), full_bio.get(req)) for req in requests]
            return requested_data

        found_members = [cls.summarize_bio(bio) for bio in data]

        return query_bio, found_members

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