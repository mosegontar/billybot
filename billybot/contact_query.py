from billy.sunlightparsers import MemberParser
from .query_handler import BaseQueryHandler
from .message_handler import ErrorMessageHandler


class ContactQuery(BaseQueryHandler):

    def __init__(self, query):
        super().__init__(query)

        self.search_parameters['member'] = None

        self.required_parameters = None

    @staticmethod
    def query_setup(message):
        contact_query = ContactQuery(message)
        errors = contact_query.parse_query()
        if errors:
            error_handler = ErrorMessageHandler(results=errors,
                                                error_type=contact_query.ERROR)
            reply = error_handler.make_error.msg()
            return True, reply

        return False, contact_query

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
        print(contact_query.search_parameters)
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

        return ' '.join(results)

    def parse_query(self):

        terms = (word.title() for word in self.query_data['original_query'].split())

        self.query_data['member'] = self.normalize_search_terms(terms)

        errors = self.initialize_params()
        if errors:
            self.ERROR = 'NO_MATCH'
        return errors

    def initialize_params(self):

        no_results_found = []

        if not self.search_parameters.get('member'):

            found_members = MemberParser.find_members(self.query_data['member'].title())
            if not found_members:
                no_results_found.append(self.query_data['member'])
            else:
                self.search_parameters = found_members

        return no_results_found

    def finalize_params(self, key):

        if key == 'member':
            bioguide_id = self.search_parameters['member'][0][1]
            self.search_parameters['member'] = bioguide_id






