from .config import SLACK_ATTACHMENT

class MessageHandler(object):

    def __init__(self, query, results):

        self.results = results
        self.query = query

    def make_list_string(self):
        """Return string of results."""

        numbered = ['[{}] {}'.format(i+1, res) for i, res in enumerate(self.results)]
        return "\n".join(numbered)

    def make_reply(self):
        """Return full reply to user query."""

        results = self.results
        if type(results) == list:
            results = self.make_list_string()

        reply = self.message + '\n' + results
        return reply   


class VoteQueryMessageHandler(MessageHandler):
    #query, results, msg_num

    def __init__(self, **kwargs):
        super().__init__(kwargs['query'], kwargs['results'])
        self.message = self.get_message(kwargs['msg_num'])

    def get_message(self, msg_num):
        """Return a specific message."""

        MESSAGES = dict()
        
        MESSAGES[0] = "Okay, "
        
        MESSAGES[1] = "I found multiple matches for '{}': ".format(self.query)
        MESSAGES[2] = "Still finding multiple matches for '{}': ".format(self.query)
        MESSAGES[3] = "Okay I guess this isn't work out very well: "

        # need to remember to reset AWAITING_REPLY when moving from one vote param to the next

        return MESSAGES.get(msg_num, "Something went wrong")




