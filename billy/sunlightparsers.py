from billy.sunlightapi import SunlightAPI


class MemberParser(object):

    MEMBERS_OF_CONGRESS = SunlightAPI.get_all_members_of_congress()

    @classmethod
    def find_members(cls, query, zipcode=None):
        """Return dictionary dict of legislator matches"""

        initial_data = None
        if zipcode:
            initial_data = cls.find_member_by_zip(zipcode)

        data = cls.lookup_members(query, initial_data)

        if data:
            found_members = [cls.summarize_bio(bio) for bio in data]
        else:
            return None

        return found_members

    @classmethod
    def find_member_by_zip(cls, zipcode):
        data = SunlightAPI.search_legislators_by_zip(zipcode)
        return data

    @classmethod
    def lookup_members(cls, keys, items=None):

        if not items:
            items = cls.MEMBERS_OF_CONGRESS

        key_words = [w.strip('"') for w in keys.split()]

        matches = []

        for member in items:
            if all([k in member.values() for k in key_words]):
                matches.append(member)

        return matches

    @classmethod
    def summarize_bio(cls, bio):
        """Receive full Legislator bio and return tuple summary."""

        member_summary = cls.formalize_name(bio)

        return (member_summary, bio)

    @classmethod
    def formalize_name(cls, member_bio):
        _full_name = ' '.join([member_bio['first_name'],
                              member_bio['last_name']])

        formal_name = '{}. {} ({}-{})'.format(member_bio['title'],
                                              _full_name,
                                              member_bio['party'],
                                              member_bio['state'])
        return formal_name