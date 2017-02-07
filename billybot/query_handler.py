from billy.sunlightparsers import BillParser as BP, LegislatorParser as LP

class QueryHandler(object):

    def __init__(self, query):
        self.query = query

    def select_one(keys, items):
        
        complete = False
        
        if len(keys) == 1 and type(keys[0]) == int:
            try:
                return items[int(keys[0])-1]
            except:
                complete = True
                return None, complete

        results = [itm for itm in items if all([k in itm for k in keys])]

        if len(results) == 1:
            complete = True
        
        return results, complete

    def get_vote(self, member_query, bill_query):
        data = LP.get_bio_data(member_query)
        if len(data) > 1:
            if
        pass

    def parse_message(self, message):

        if message.startswith('vote'):
            member, bill = [m.strip() for m in message.split('member:')[1].strip().split('bill:')]
            return self.get_vote(member, bill)

message = "vote member: Smith bill: S. Con. Res. 3"
qh = QueryHandler(message)

print(qh.parse_message(qh.query))
