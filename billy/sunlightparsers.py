from billy.sunlightapi import SunlightAPI


class Parser(SunlightAPI):

    MEMBERS_OF_CONGRESS = SunlightAPI.get_all_members_of_congress()

    @classmethod
    def lookup_members(cls, keys, items=None):

        if not items:
            items = cls.MEMBERS_OF_CONGRESS
        key_words = keys.split()
        matches = []
        for member in items:
            if all([k in member.values() for k in key_words]):
                matches.append(member)
        return matches

class MemberParser(Parser):

    def __init__(self, bioguide_id):
        super().__init__()
        self.bioguide_id = bioguide_id
        self.member_data = self.get_member_data(self.bioguide_id)
        self._recent_votes = None

    @classmethod
    def find_member_by_zip(cls, zipcode):
        data = SunlightAPI.search_legislators_by_zip(zipcode)
        return data

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

        return (member_summary, bio) #bio['bioguide_id'])

    @classmethod
    def find_members(cls, query, zipcode=None):
        """Return dictionary dict of legislator matches"""

        if zipcode:
            initial_data = cls.find_member_by_zip(zipcode)
            data = cls.lookup_members(query, initial_data)
        
        if not zipcode:
            data = cls.lookup_members(query)

        if data:
            found_members = [cls.summarize_bio(bio) for bio in data]
        else:
            return None

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
