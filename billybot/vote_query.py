from billy.sunlightparsers import MemberParser, BillParser
from .query_handler import BaseQueryHandler
from .message_handler import VoteQueryMessageHandler, ErrorMessageHandler


class VoteQuery(BaseQueryHandler):

    def __init__(self, query):
        super().__init__('vote', query)

        self.search_parameters['member'] = None
        self.search_parameters['bill_votes'] = None

        self.msg_handler = VoteQueryMessageHandler

        self.required_parameters = ['member:', 'bill:']

    @staticmethod
    def query_setup(message):

        vote_query = VoteQuery(message)
        errors = vote_query.parse_query()
        if errors:
            error_handler = ErrorMessageHandler(results=errors,
                                                error_type=vote_query.ERROR)
            reply = error_handler.make_error_msg()
            return True, reply

        return False, vote_query

    @staticmethod
    def run_query(message, existing_query_object=None):
        """Get and return query object and reply for user"""

        # create a VoteQuery object if none exists
        if not existing_query_object:
            errors, resp = VoteQuery.query_setup(message)
            if errors:
                return None, resp
            else:
                vote_query = resp
        else:
            vote_query = existing_query_object
            vote_query.narrow_parameters(message)

        reply = vote_query.get_reply()

        return vote_query, reply

    def parse_query(self):
        """Break up query string and set instance variables"""

        errors = self.validate_query()
        if errors:
            return errors

        _member, _bill = self.query_data['original_query'].split('bill:')
        print(_member)
        self.query_data['member'] = _member.replace('member:', '').strip()
        self.query_data['bill_votes'] = _bill.strip()

        errors = self.initialize_params()
        if errors:
            self.ERROR = 'NO_MATCH'
        return errors

    def initialize_params(self):
        """Makes API call and sets params if not already set"""

        no_results_found = []

        if not self.search_parameters.get('member'):

            found_members = MemberParser.find_members(self.query_data['member'].title())
            if not found_members:
                no_results_found.append(self.query_data['member'])
            else:
                self.search_parameters['member'] = found_members

        if not self.search_parameters.get('bill_votes'):

            bill = BillParser(self.query_data['bill_votes'])
            if not bill.bill_data or not bill.votes:
                no_results_found.append(self.query_data['bill_votes'])
            else:
                self.search_parameters['bill_votes'] = bill.votes

        return no_results_found

    def finalize_params(self, key):
        """Set search_parameters their proper ID strings

        Each congress member has a 'bioguide_id' and
        each congressional bill has associated with it a number of 'roll_id'
        """

        if key == 'member':
            bioguide_id = self.search_parameters['member'][0][1]
            self.search_parameters['member'] = bioguide_id
            self.set_member_results_data(bioguide_id)

        if key == 'bill_votes':
            roll_id = self.search_parameters['bill_votes'][0][1]
            self.search_parameters['bill_votes'] = roll_id

    def set_bill_results_data(self, bill):

        bill_data = bill.bill_data

        if bill_data.get('short_title'):
            self.results_data['bill_title'] = bill_data['short_title']
        else:
            self.results_data['bill_title'] = bill_data['official_title']

        self.results_data['bill_id'] = bill_data['bill_id']
        self.results_data['bill_chamber'] = bill_data['chamber']
        self.results_data['bill_url'] = bill_data['urls']['congress']

    def set_member_results_data(self, bioguide_id):
        member = MemberParser(bioguide_id)
        member_data = member.member_data

        self.results_data['member_name'] = member.formalize_name(member_data)
        self.results_data['member_title'] = member_data['title']
        self.results_data['member_chamber'] = member_data['chamber']
        self.results_data['member_party'] = member_data['party']
        self.results_data['member_state'] = member_data['state']
        self.results_data['member_url'] = member_data['website']

    def set_roll_vote_data(self, roll_id):
        vote_data = BillParser.get_roll_vote_data(roll_id)

        self.results_data['roll_id'] = vote_data['roll_id']
        self.results_data['roll_question'] = vote_data['question']
        self.results_data['roll_url'] = vote_data['roll_id']

    def resolve_query(self):
        """Return the member's vote (Yea or Nay)"""

        member = MemberParser(self.search_parameters['member'])
        roll_vote = self.search_parameters['bill_votes']
        vote = member.parse_roll_call_vote(roll_vote)
        if not vote:
            return "{} didn't vote on {}".format(self.results_data['member_name'],
                                                 self.query_data['bill_votes'])

        return '{} voted {} on {}.'.format(self.results_data['member_name'],
                                           vote,
                                           self.search_parameters['bill_votes'])

    def __repr__(self):
        return "VoteQuery({})".format(self.query_data)
