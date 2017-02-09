from collections import OrderedDict

from billy.sunlightparsers import LegislatorParser, BillParser
from .message_handler import VoteQueryMessageHandler


class QueryHandler(object):

    def __init__(self, command, query):

        self.query = query.split(command)[1].strip()
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

class VoteQuery(QueryHandler):

    def __init__(self, query):
        super().__init__('vote', query)
        
        self.member_query = None
        self.bill_query = None

        self.params['member'] = None
        self.params['roll_id'] = None

    def set_params(self):
        """Makes API call and sets params if not already set"""

        if not self.params.get('member'):
            members = list(LegislatorParser.get_bio_data(self.member_query.title()))
            self.params['member'] = members

        if not self.params.get('roll_id'):
            bill = BillParser(self.bill_query)
            roll_votes = bill.votes
            self.params['roll_id'] = roll_votes

    def parse_query(self):
        """Break up query string and set instance variables"""

        _member, _bill = self.query.split('bill:')
        self.member_query = _member.strip('member:').strip()
        self.bill_query = _bill.strip()

        self.set_params()

    def get_reply(self):

        if len(self.params['member']) == 1:
            self.params['member'] = self.params['member'][0][1]
        elif type(self.params['member']) != str:
            self.AWAITING_REPLY += 1
            
            # but what if it's a clarifying message?
            msg_handler = VoteQueryMessageHandler(self.member_query, 
                                                  map(lambda item: item[0], self.params['member']), 
                                                  self.AWAITING_REPLY) 

            reply = msg_handler.make_reply()
            return reply
        else:
            pass

        if len(self.params['roll_id']) == 1:
            self.params['roll_id'] = self.params['roll_id'][0][1]

        elif type(self.params['roll_id']) != str:
            self.AWAITING_REPLY += 1
            
            msg_handler = VoteQueryMessageHandler(self.bill_query, 
                                                  map(lambda item: item[0], self.params['roll_id']), 
                                                  self.AWAITING_REPLY) 

            reply = msg_handler.make_reply()
            return reply
        else:
            pass

        self.AWAITING_REPLY = 0
        member = LegislatorParser(self.params['member'])
        roll_vote = self.params['roll_id']
        
        return member.parse_roll_call_vote(roll_vote)


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

    def __repr__(self):
        return "VoteQuery({})".format(self.query)


class MessageTriage(object):

    def __init__(self, message, query_object=None):

        self.message = message
        self.query_object = query_object

    def identify_query(self):
        """Send message to proper QueryHandler object.
        
        Return QueryHandler object and reply for user.
        """
        if self.query_object:
            query, reply = self.query_object.run_query(self.message, 
                                                       self.query_object)

        if self.message.startswith('vote'):
            query, reply = VoteQuery.run_query(self.message)

        return query, reply

