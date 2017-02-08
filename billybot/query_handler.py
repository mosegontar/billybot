from collections import OrderedDict
from billy.sunlightparsers import LegislatorParser as LP, BillParser as BP


class QueryHandler(object):

    def __init__(self, command, query):
        self.query = query.split(command)[1].strip()
        self.AWAITING_REPLY = False

    def select_one(self, keys, items):
        
        if type(keys) != list:
            keys = [keys]
        
        if len(keys) == 1:
            try:
                return items[int(keys[0])-1]
            except:
                pass

        results = [itm for itm in items if all([k in itm for k in keys])]
        
        return results

class VoteQuery(QueryHandler):

    def __init__(self, query):
        super().__init__('vote', query)
        self.member_query = None
        self.bill_query = None
        self.vote_params = OrderedDict()
        self.vote_params['member'] = self.member_query
        self.vote_params['roll_id'] = self.bill_query

        # for any paramater == None,
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
            self.vote_params['member'] = LP.search_legislators(self.member_query)
        if not self.vote_params.get('roll_id'):
            self.vote_params['roll_id'] = BP.get_roll_votes(self.bill_query)
        return

    def parse_query(self):
        _member, _bill = self.query.split('bill:')
        self.member_query = _member.strip('member:').strip()
        self.bill_query = _bill.strip()

    @staticmethod
    def run_query(message, existing_query_object=None):

        if not existing_query_object:
            if 'member:' not in message and 'bill:' not in message:
                # query not properly formatted
                return False

            vq = VoteQuery(message)
            vq.parse_query()
        else:
            vq = existing_query_object

        if vq.AWAITING_REPLY:
            for key, val in vq.vote_params:
                if type(val) == list:
                    vq.vote_params[key] = vq.select_one(message, val)
                    break
        if len(vq.vote_params['member']) == 1:
            vq.vote_params['member'] = # member's bioguide_id
        else:
            vq.AWAITING_REPLY = True
            return vq, vq.vote_params['member'], 'Select a member'

        if len(vq.vote_params['roll_id']) == 1:
            vq.vote_params['roll_id'] = vq.vote_params['roll_id'][0]
        else:
            vq.AWAITING_REPLY = True
            return vq, vq.vote_params['roll_id'], 'Select a roll_id'
        


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
