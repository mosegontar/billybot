from billy.sunlightapi import SunlightAPI


class BillParser(SunlightAPI):

    def __init__(self, bill_id, congress=None):
        super().__init__()
        if congress:
            self.congress = congress
        self.bill_id = bill_id
        self.sanitize_bill_id()
        
        self.bill_data = None
        bill_data = self.get_bill_data(self.bill_id)
        if bill_data:
            self.bill_data = bill_data[0]
        """
        'bill_id', 'bill_type', 'chamber', 'congress', 'committee_ids',
        'congress', 'cosponsors_count', 'enacted_as', 'history', 'introduced_on',
        'last_action_at', 'last_version', 'last_version_on', 'last_vote_at',
        'number', 'official_title', 'short_title', 'popular_title', 'related_bills',
        'sponsor', 'sponsor_id', 'urls', 'withdrawn_cosponsor_count'
        """
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
    def get_roll_vote_data(self, roll_id):
        vote_data = self.get_vote_data(roll_id)[0]
        return vote_data


class MemberParser(SunlightAPI):

    def __init__(self, bioguide_id):

        super().__init__()
        self.bioguide_id = bioguide_id
        self.member_data = self.get_member_data(self.bioguide_id)[0]
        """
        'bioguide_id', 'birthday', 'chamber', 'contact_form', 'crp_id',
        'district', 'facebook_id', 'fax', 'fec_ids', 'first_name',
        'gender', 'govtrack_id', 'icpsr_id', 'in_office', 'last_name',
        'leadership_role', 'lis_id', 'middle_name', 'name_suffix', 
        'nickname', 'oc_email', 'ocd_id', 'office', 'party', 'phone', 
        'senate_class', 'state', 'state_name', 'state_rank', 'term_end', 
        'term_start', 'thomas_id', 'title', 'twitter_id', 'votesmart_id', 
        'website', 'youtube_id'
        """

        self._recent_votes = None

    @classmethod
    def formalize_name(cls, member_bio):

        full_name = ' '.join([member_bio['first_name'], member_bio['last_name']])
        _formal_name = '{}. {} ({}-{})'.format(member_bio['title'],
                                               full_name,
                                               member_bio['party'],
                                               member_bio['state'])
        return _formal_name      

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
        except IndexError:
            return None
        except KeyError:
            return None

        return vote
