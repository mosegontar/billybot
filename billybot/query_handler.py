from billy.sunlightparsers import BillParser as BP, LegislatorParser as LP

class QueryHandler(object):

    def __init__(self, query):
        self.query = query
        self.query_function = None
        self.data = None

        self.reply = None
        self.clarify = None

    def select_one(self, keys, items):
        
        if type(keys) != list:
            keys = [keys]

        complete = False
        
        if len(keys) == 1:
            try:
                complete = True
                return items[int(keys[0])-1], complete
            except:
                pass

        results = [itm for itm in items if all([k in itm for k in keys])]

        if len(results) == 1:
            results = results[0]
            complete = True
        
        return results, complete

    def parse_message(self, message):

        if self.clarify:
            print(self.query_function(message, 'bill'))

        if message.startswith('vote'):
            member, bill = [m.strip() for m in message.split('member:')[1].strip().split('bill:')]
            self.query_function = self.get_vote
            reply, clarify = self.get_vote(member, bill)
            print(reply)
            if clarify:
                clarification = input('> ')
                self.parse_message(clarification)

class VoteQuery(QueryHandler):

    def __init__(self, member_query, bill_query):
        self.vote_params = {'member': None, 'roll_id': None}
        self.process_query(member_query, bill_query)

    def validate_params(self):
        for key, value in self.vote_params:
            if type(value) != str:
                return False
        return True

    def process_query(self, member, bill):
        


    def get_vote(self, member_query, bill_query):

        if not self.query_params:
            self.query_params = {'member': None, 'bill': None}
        
            query_bio, member_data = LP.get_bio_data(member_query, 'bioguide_id')

            if len(member_data) == 1:
                bio_id = query_bio(member_data[0][2])
                self.query_params['member'] = bio_id
            else:
                self.query_params['member'] = member_data
                self.reply = 'Need more info\n' + '; '.join([' '.join(list(l)) for l in self.query_params['member']])
                self.clarify = 'member'

            if type(self.query_params['member']) == str:
                self.reply = 'Got it!\n' + self.query_params['member']

            return self.reply, self.clarify

        else:
            return self.select_one([member_query], self.query_params[self.clarify])


    def get_vote_triage



message = "vote member: Bishop bill: S. Con. Res. 3"
qh = QueryHandler(message)

qh.parse_message(qh.query)
