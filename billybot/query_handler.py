from collections import OrderedDict

from billy.sunlightparsers import LegislatorParser as LP, BillParser as BP
from .message_handler import VoteQueryMessageHandler as VQMH


class QueryHandler(object):

    def __init__(self, command, query):
        self.query = query.split(command)[1].strip()
        self.AWAITING_REPLY = 0

    def select_one(self, keys, items):
        
        if type(keys) == str:
            keys = keys.split()
        
        if len(keys) == 1:
            try:
                return items[int(keys[0])-1]
            except:
                pass

        # itm[0] contains the data with which user is making selection
        results = [itm for itm in items if all([k in itm[0] for k in keys])]
        
        return results

class VoteQuery(QueryHandler):

    def __init__(self, query):
        super().__init__('vote', query)
        
        self.member_query = None
        self.bill_query = None

        self.vote_params = OrderedDict()
        self.vote_params['member'] = None
        self.vote_params['roll_id'] = None

        # for any paramater that == None,
        #   api call
        # IF AWAITING REPLY
        #   for param in parms:
        #       param = select_one(msg)
        #
        # ELSE
        #   if len(member list) == 1
        #       member list = the one member
        #   else:
        #       return member list and instructions
        #   if len(roll votes) == 1:
        #       roll_id = the roll vote
        #   else:
        #       return roll list and instructions
        #
        # get_the_vote(member, roll)



    def set_vote_params(self):
        if not self.vote_params.get('member'):
            self.vote_params['member'] = list(LP.get_bio_data(self.member_query))
        if not self.vote_params.get('roll_id'):
            self.vote_params['roll_id'] = list(BP.get_roll_votes(self.bill_query))
        

    def parse_query(self):
        
        _member, _bill = self.query.split('bill:')
        self.member_query = _member.strip('member:').strip()
        self.bill_query = _bill.strip()

        self.set_vote_params()

    def narrow_parameters(self):
        """Narrow down data based on words in message"""

        if vq.AWAITING_REPLY:
            for key, val in vq.vote_params.items():
                if type(val) == list:
                    vq.vote_params[key] = vq.select_one(message, val)
                    break 

    def get_reply(self):

        if len(vq.vote_params['member']) == 1:
            # vq.vote_params['member'] is a tuple
            # the first item has summariation data
            # the second item has biographical data
            vq.vote_params['member'] = vq.vote_params['member'][0][1]
        else:
            vq.AWAITING_REPLY += 1
            
            # but what if it's a clarifying message?
            msg_handler = VQMH(self.member_query, 
                               vq.vote_params['roll_id'], 
                               vq.AWAITING_REPLY) 

            reply = msg_handler.make_reply()
            return vq, reply

        if len(vq.vote_params['roll_id']) == 1:
            vq.vote_params['roll_id'] = vq.vote_params['roll_id'][0][1]
        else:
            vq.AWAITING_REPLY += 1
            
            # but what if it's a clarifying message?
            msg_handler = VQMH(self.bill_query, 
                               vq.vote_params['roll_id'], 
                               vq.AWAITING_REPLY) 

            reply = msg_handler.make_reply()
            return vq, reply

        # get vote and return
        # vq and reply


    @staticmethod
    def run_query(message, existing_query_object=None):

        # create a VoteQuery object if none exists
        if not existing_query_object:
            if 'member:' not in message and 'bill:' not in message:
                # query not properly formatted
                return False
            vq = VoteQuery(message)
            vq.parse_query()
        else:
            vq = existing_query_object

        vq.narrow_parameters()

        VQ, reply = vq.get_reply()

        return VQ, reply

    def __repr__(self):
        return "VoteQuery({})".format(self.query)


class MessageTriage(object):

    def __init__(self, message):
        self.message = message

    def identify_query(self):

        if self.message.startswith('vote'):
            return VoteQuery.run_query(self.message)

if __name__ == '__main__':
    message = "vote member: Bishop bill: S. Con. Res. 3"
    triage = MessageTriage(message)
