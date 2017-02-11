from collections import OrderedDict

from billy.sunlightparsers import MemberParser, BillParser
from .message_handler import VoteQueryMessageHandler, ErrorMessageHandler


class QueryHandler(object):

    def __init__(self, command, query):
        
        self.query_data = dict()
        self.query_data['original_query'] = query.split(command)[1].strip()

        self.search_parameters = OrderedDict()

        self.results_data = dict()

        self.AWAITING_REPLY = 0

    def select(self, keys, item_list):
        """Select items from item_list that contain all keys"""

        if type(keys) == str:
            keys = keys.split()
        
        if len(keys) == 1:
            try:
                return [item_list[int(keys[0])-1]]
            except:
                pass

        # itm[0] contains the data with which user is making selection
        results = [itm for itm in item_list if all([k in itm[0] for k in keys])]
        
        return results

    def narrow_parameters(self, message):
        """Narrow down list of data based on words in message"""

        if self.AWAITING_REPLY:
            for key, val in self.search_parameters.items():
                if type(val) == list:
                    self.search_parameters[key] = self.select(message, val)
                    break

    def get_reply(self):
        """Returns reply based on state"""

        for key, value in self.search_parameters.items():
            if type(value) == str:
                pass
            elif len(value) == 1:
                self.AWAITING_REPLY = 0
                self.finalize_params(key)
            else:
                self.AWAITING_REPLY += 1
                msg_handler = self.prepare_message_handler(key=key)
                reply = msg_handler.make_reply()
                return reply

        self.AWAITING_REPLY = 0
        resolved_query = self.resolve_query()

        msg_handler = self.prepare_message_handler(results=resolved_query)
        reply = msg_handler.make_reply()
        return reply

    def prepare_message_handler(self, results=None, key=None):
        """Create and return a MessageHandler with query results"""

        if not results:
            results = [itm[0] for itm in self.search_parameters[key]]

        message_data = {'msg_num': self.AWAITING_REPLY,
                        'results': results,
                        'query': self.query_data.get(key)}

        msg_handler = self.handler(**message_data)

        return msg_handler


class VoteQuery(QueryHandler):

    def __init__(self, query):
        super().__init__('vote', query)

        self.search_parameters['member'] = None
        self.search_parameters['bill_votes'] = None

        self.handler = VoteQueryMessageHandler

    @staticmethod
    def run_query(message, existing_query_object=None):
        """Get and return query object and reply for user"""

        # create a VoteQuery object if none exists
        if not existing_query_object:

            if 'member:' not in message and 'bill:' not in message:
                # query not properly formatted
                return False

            vote_query = VoteQuery(message)
            errors = vote_query.parse_query()

            if errors:
                error_handler = ErrorMessageHandler(results=errors)
                reply = error_handler.no_matches()
                return None, reply
        else:
            vote_query = existing_query_object
            vote_query.narrow_parameters(message)

        reply = vote_query.get_reply()

        return vote_query, reply

    def parse_query(self):
        """Break up query string and set instance variables"""

        _member, _bill = self.query_data['original_query'].split('bill:')
        self.query_data['member'] = _member.strip('member:').strip()
        self.query_data['bill_votes'] = _bill.strip()

        errors = self.initialize_params()
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
        
        if bill.bill_data.get('short_title'):
            self.results_data['bill_title'] = bill.bill_data['short_title']
        else:
            self.results_data['bill_title'] = bill.bill_data['official_title']

        self.results_data['bill_id'] = bill.bill_data['bill_id']
        self.results_data['bill_chamber'] = bill.bill_data['chamber']      
        self.results_data['bill_url'] = bill.bill_data['urls']['congress']

    def set_member_results_data(self, bioguide_id):
        member = MemberParser(bioguide_id)

        self.results_data['member_name'] = member.formalize_name(member.member_data)
        self.results_data['member_title'] = member.member_data['title']
        self.results_data['member_chamber'] = member.member_data['chamber']
        self.results_data['member_party'] = member.member_data['party']
        self.results_data['member_state'] = member.member_data['state']
        self.results_data['member_url'] = member.member_data['website']


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
