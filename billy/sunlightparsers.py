from billy.sunlightapi import SunlightAPI


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
        """Format bill_id. 
        
        E.g.: "S. Con.Res.3." => 'sconres3-115'.
        """

        if not self.bill_id.endswith('-'+self.congress):
            self.bill_id += '-' + self.congress

        self.bill_id = self.bill_id.lower().replace(' ', '').replace('.', '')

    @property
    def votes(self):
        """Return bill's associated votes. If set to None, makes api call."""

        if not self._votes:
            self._votes = self.get_all_bill_votes(self.bill_id)
        return self._votes

    @property
    def official_title(self):
        """Return bill's official title. If set to None, makes api call."""

        if not self._official_title:
            data = self.get_official_bill_title(self.bill_id)

            try:
                self._official_title = data[0].get('official_title')
            except IndexError:
                self._official_title = None

        return self._official_title

    @property
    def short_title(self):
        """Return bill's short title. If set to None, makes api call."""

        if not self._short_title:
            data = self.get_short_bill_title(self.bill_id)

            try:
                self._short_title = data[0].get('short_title')
            except IndexError:
                self._short_title = None

        return self._short_title


class LegislatorParser(SunlightAPI):

    def __init__(self, bioguide_id):

        super().__init__()
        self.bioguide_id = bioguide_id
        self._recent_votes = None

    @classmethod
    def summarize_bio(cls, bio):
        """Receive full Legislator bio and return tuple summary."""
        name = ' '.join([bio['first_name'], bio['last_name']])
        person = '{} ({})'.format(name, bio['state'])
        return (person, bio['bioguide_id'])

    @classmethod
    def get_bio_data(cls, data):
        """Return dictionary dict of legislator matches"""

        if not data:
            return None

        found_members = dict((cls.summarize_bio(bio), bio) for bio in data)

        return found_members

    @property
    def recent_votes(self):
        """Return legislator's recent votes. If set to None, make api call."""

        if not self._recent_votes:
            self._recent_votes = self.get_legislator_recent_votes(self.bioguide_id)
        return self._recent_votes

    def parse_roll_call_vote(self, roll_id):
        """Return legislator's roll call vote (Yea or Nay)."""
        data = self.get_roll_call_vote(roll_id, self.bioguide_id)

        try:
            vote = data[0]['voters'][self.bioguide_id]['vote']
        except IndexError:
            return None

        return vote