from collections import OrderedDict

from billy.sunlightparsers import LegislatorParser, BillParser
from .message_handler import VoteQueryMessageHandler


class QueryHandler(object):

    def __init__(self, command, query):

        self.query = dict()
        self.query['original_query'] = query.split(command)[1].strip()

        self.params = OrderedDict()
        self.AWAITING_REPLY = 0

    def select(self, keys, item_list):
        """Select items from item_list that contain all keys"""

        if type(keys) == str:
            keys = keys.split()
        
        if len(keys) == 1:
            try:
                return item_list[int(keys[0])-1]
            except:
                pass

        # itm[0] contains the data with which user is making selection
        results = [itm for itm in item_list if all([k in itm[0] for k in keys])]
        
        return results

    def narrow_parameters(self, message):
        """Narrow down data based on words in message"""

        if self.AWAITING_REPLY:
            for key, val in self.params.items():
                if type(val) == list:
                    self.params[key] = self.select(message, val)
                    break

    def get_reply(self):

        for key, value in self.params.items():
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

        if not results:
            results = [itm[0] for itm in self.params[key]]

        message_data = {'msg_num': self.AWAITING_REPLY, 
                        'results': results,
                        'query': self.query.get(key)}

        msg_handler = self.handler(**message_data)

        return msg_handler


class VoteQuery(QueryHandler):

    def __init__(self, query):
        super().__init__('vote', query)       
      
        self.params['member'] = None
        self.params['bill_votes'] = None
        
        self.handler = VoteQueryMessageHandler

    @staticmethod
    def run_query(message, existing_query_object=None):

        # create a VoteQuery object if none exists
        if not existing_query_object:
            if 'member:' not in message and 'bill:' not in message:
                # query not properly formatted
                return False
                
            vote_query = VoteQuery(message)
            vote_query.parse_query()
        else:
            vote_query = existing_query_object
            vote_query.narrow_parameters(message)
        
        reply = vote_query.get_reply()

        return vote_query, reply

    def parse_query(self):
        """Break up query string and set instance variables"""

        _member, _bill = self.query['original_query'].split('bill:')
        self.query['member'] = _member.strip('member:').strip()
        self.query['bill_votes'] = _bill.strip()

        self.initialize_params()

    def initialize_params(self):
        """Makes API call and sets params if not already set"""

        if not self.params.get('member'):
            members = list(LegislatorParser.get_bio_data(self.query['member'].title()))
            self.params['member'] = members

        if not self.params.get('bill_votes'):
            bill = BillParser(self.query['bill_votes'])
            roll_votes = bill.votes
            self.params['bill_votes'] = roll_votes

    def finalize_params(self, key):

        if key == 'member':
            self.params['member'] = self.params['member'][0][1]

        if key == 'bill_votes':
            self.params['bill_votes'] = self.params['bill_votes'][0][1]

    def resolve_query(self):

        member = LegislatorParser(self.params['member'])
        roll_vote = self.params['bill_votes']
        print(self.params['bill_votes'])
        vote = member.parse_roll_call_vote(roll_vote)

        return '{} voted {} on {}.'.format(self.query['member'], 
                                           vote, 
                                           self.query['bill_votes'])



    def __repr__(self):
        return "VoteQuery({})".format(self.query)



