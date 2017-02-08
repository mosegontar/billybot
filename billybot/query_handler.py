from billy.sunlightparsers import LegislatorParser as LP


class QueryHandler(object):

    def __init__(self, command, query):
        self.query = query.split(command)[1].strip()

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
        self.vote_params = {'member': None, 'roll_id': None}

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

    def validate_params(self):
        invalid = []
        for key, value in self.vote_params:
            if type(value) != str:
                invalid.append(key)

        return invalid

    def find_member(self):
        data = self.vote_params.get('member')
        if not data:
            query_bio, data = LP.get_bio_data(self.member_query, 'bioguide_id')
        self.vote_params['member'] = data


    def parse_query(self):
        _member, _bill = self.query.split('bill:')
        self.member_query = _member.strip('member:').strip()
        self.bill_query = _bill.strip()

    @staticmethod
    def run_query(message, existing_query_object=None):

        if existing_query_object:
            vp = existing_query_object
            invalid_params = vp.validate_params()
            if 'member' in invalid_params:
                member_results = VoteQuery.select_one(message)
                if len(member_results) == 1:
                    vp.vote_params['member'] = member_results[0]
                else:
                    vp.vote_params 
            elif 'bill' in invalid_params:
                pass
            else:
                pass

        if 'member:' not in message and 'bill:' not in message:
            # query not properly formatted
            return False

        vq = VoteQuery(message)
        vq.parse_query()
        vp.find_member()

        return vq

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
