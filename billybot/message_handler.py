
class MessageHandler(object):

    def __init__(self, query, results):

        self.results = results[0]
        self.query = query

    def get_results_as_str(self):
        """Return string of results"""

        numbered = ['[{}] {}'.format(i+1, res) for i, res in enumerate(self.results)]
        return "\n".join(numbered)

    def make_reply(self):
        reply = self.message + '\n' + self.get_results_as_str()
        return reply   


class VoteQueryMessageHandler(MessageHandler):

    def __init__(self, query, results, msg_num):
        super().__init__(query, results)
        self.message = self.get_message(msg_num)

    def get_message(self, msg_num):
        MESSAGES = dict()
        
        MESSAGES[0] = "Here are your results: "
        
        MESSAGES[1] = "I found multiple matches for {}: ".format(self.query)
        MESSAGES[2] = "Still finding multiple matches for {}: "
        MESSAGES[3] = "Okay I guess this isn't work out very well: "

        # need to remember to reset AWAITING_REPLY when moving from one vote param to the next

        return MESSAGES.get(msg_num, "Something went wrong")




results = ['Elizabeth Warren (MA)', 'Pat Warren (MA)']
msg_handler = VoteQueryMessageHandler('Warren', results, 1)
print(msg_handler.make_reply())


