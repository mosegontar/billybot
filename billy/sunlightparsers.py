from billy.sunlightapi import SunlightAPI


class BillParser(SunlightAPI):

    def __init__(self, bill_id, congress=None):
        super().__init__()

        if congress:
            self.congress = congress

        self.bill_id = bill_id
        self.sanitize_bill_id()

        bill_data = self.get_bill_data(self.bill_id)
        if bill_data:
            self.bill_data = bill_data[0]
        else:
            self.bill_data = None

        self._votes = None

    def sanitize_bill_id(self):
        """Format bill_id.

        E.g.: "S. Con.Res.3." => 'sconres3-115'.
        """

        if not self.bill_id.endswith('-'+self.congress):
            self.bill_id += '-' + self.congress

        self.bill_id = self.bill_id.lower().replace(' ', '').replace('.', '')

    def summarize_vote(self, vote):

        date = vote['voted_at'].split('T')[0]

        vote_summary = '{}: {} ({})'.format(vote['roll_id'],
                                            vote['question'],
                                            date)

        return (vote_summary, vote['roll_id'])

    @property
    def votes(self):
        """Return bill's associated votes. If set to None, makes api call."""

        if not self._votes:
            votes = self.get_all_bill_votes(self.bill_id)
            self._votes = [self.summarize_vote(vote) for vote in votes]
        return self._votes

    @staticmethod
    def get_roll_vote_data(roll_id):
        api = SunlightAPI()
        vote_data = api.get_vote_data(roll_id)[0]
        return vote_data


class MemberParser(SunlightAPI):

    def __init__(self, bioguide_id):
        super().__init__()
        self.bioguide_id = bioguide_id
        self.member_data = self.get_member_data(self.bioguide_id)[0]
        self._recent_votes = None

    @classmethod
    def formalize_name(cls, member_bio):

        _full_name = ' '.join([member_bio['first_name'],
                              member_bio['last_name']])

        formal_name = '{}. {} ({}-{})'.format(member_bio['title'],
                                              _full_name,
                                              member_bio['party'],
                                              member_bio['state'])
        return formal_name

    @classmethod
    def summarize_bio(cls, bio):
        """Receive full Legislator bio and return tuple summary."""

        member_summary = cls.formalize_name(bio)

        return (member_summary, bio['bioguide_id'])

    @classmethod
    def find_members(cls, query):
        """Return dictionary dict of legislator matches"""

        data = MemberParser.search_legislators(query)

        found_members = [cls.summarize_bio(bio) for bio in data]
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
        except:
            return None

        return vote
