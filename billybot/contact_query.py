from billy.sunlightparsers import MemberParser
from .query_handler import BaseQueryHandler


class ContactQuery(BaseQueryHandler):

    def __init__(self, query):
        super().__init__(query)

        self.search_parameters['name'] = None

        self.required_parameters = None

    @staticmethod
    def query_setup(message):
        contact_query = ContactQuery(message)

    @staticmethod
    def run_query(message, existing_query_handler=None):
        """Get and return query object and reply for user"""

        # create a VoteQuery object if none exists
        if not existing_query_handler:
            errors, resp = ContactQuery.query_setup(message)
            if errors:
                return None, resp
            else:
                contact_query = resp
        else:
            contact_query = existing_query_handler
            contact_query.narrow_parameters(message)
        reply, attachment = contact_query.get_reply()
        return contact_query, reply, attachment

    def normalize_search_terms(self, terms):

        translation_map = {'Democrat': 'D',
                           'Republican': 'R',
                           'Representative': 'Rep',
                           'Rep.': 'Rep',
                           'Senator': 'Sen',
                           'Sen.': 'Sen'}
        results = []
        for term in terms:
            if term in translation_map.keys():
                term = translation_map[term]
            results.append(term)

        return results

    def parse_query(self):

        terms = (word.title() for word in self.query_data['original_query'].split())
        search_terms = self.normalize_search_terms(terms)






