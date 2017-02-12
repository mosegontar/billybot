import json
from .config import slack_attachment

from eng_join import join

class MessageHandler(object):

    def __init__(self, results, results_data, query=None):

        self.results = results
        self.results_data = results_data
        self.query = query
        self.attachment = slack_attachment
        self.message = None

    def make_list_string(self):
        """Return string of results."""

        string_list = ['[{}] {}'.format(i+1, res) for i, res in enumerate(self.results)]
        return "\n".join(string_list)

    def make_reply(self):
        """Return full reply to user query."""

        results = self.results
        if type(results) == list:
            reply = self.message
            attachment_dict = self.format_attachment()
            results = self.create_attachment(**attachment_dict)
        else:
            reply = self.message + ' ' + self.results

        return reply, results

    def create_attachment(self, **kwargs):

        for key, value in kwargs.items():
            if key in self.attachment.keys():
                self.attachment[key] = value
        return json.dumps([self.attachment])


class ErrorMessageHandler(MessageHandler):

    def __init__(self, results, error_type):
        super().__init__(results=results, results_data=None)
        self.error_type = error_type

    def no_matches(self):
        reply = "Sorry, I wasn't able to find matches for "
        results_to_str = join(["'{}'".format(r) for r in self.results],
                              conj='and')
        reply = reply + results_to_str
        return reply

    def bad_query(self):
        return "Sorry, your query is not properly formatted"

    def make_error_msg(self):
        if self.error_type == 'BAD_QUERY':
            return self.bad_query()
        if self.error_type == 'NO_MATCH':
            return self.no_matches()


class VoteQueryMessageHandler(MessageHandler):

    def __init__(self, **kwargs):
        super().__init__(kwargs['results'],
                         kwargs['results_data'],
                         kwargs['query'])

        self.message = self.get_message(kwargs['msg_num'])

    def get_message(self, msg_num):
        """Return a specific message."""

        MESSAGES = dict()

        MESSAGES[0] = "Okay, "

        MESSAGES[1] = "I found multiple matches for '{}': ".format(self.query)
        MESSAGES[2] = "Still finding multiple matches for '{}': ".format(self.query)
        MESSAGES[3] = "Okay I guess this isn't work out very well: "

        return MESSAGES.get(msg_num, "Something went wrong")

    def format_attachment(self):

        attachment_dict = dict()
        attachment_dict['text'] = self.make_list_string()
        return attachment_dict







slack_attachment = {
    "fallback": None, # "Required plain-text summary of the attachment."
    "color": None, # color hex value
    "pretext": None, #"Optional text that appears above the attachment block"
    "author_name": None ,
    "author_link": None,
    "title": None,
    "title_link": None,
    "text": None, #"Optional text that appears within the attachment",
    "footer": None,
    "ts": 123456789
}




