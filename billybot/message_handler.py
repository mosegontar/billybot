import json
from .config import slack_attachment

from eng_join import join

class MessageHandler(object):

    def __init__(self, primary_msg, secondary_msg, **kwargs):
        self.primary_msg = primary_msg
        self.secondary_msg = secondary_msg
        self.attachment = None
        self.incoming_data = kwargs

    def format_attachment(self, attachment):
        attachment = attachment
        for key, value in self.incoming_data.items():
            if key in attachment.keys():
                if key == 'text' and type(value) == list:
                    value = self.make_list_string(value)
                attachment[key] = value

        self.attachment = json.dumps([attachment])

    def make_list_string(self, item_list):

        string_list = '\n'.join(['{}. {}'.format(i+1, item)
                                for i, item in enumerate(item_list)])

        return string_list

    def make_reply(self):
        self.format_attachment(slack_attachment)
        reply = [{'text': self.primary_msg,
                  'attachments': self.attachment}]

        if self.secondary_msg:
            second = {'text': self.secondary_msg,
                      'attachments': None}
            reply.append(second)

        return reply










slack_attachment = {
    "fallback": None, # "Required plain-text summary of the attachment."
    "color": None, # color hex value
    "pretext": None, #"Optional text that appears above the attachment block"
    "author_name": None ,
    "author_link": None,
    "title": None,
    "fields": [],
    "title_link": None,
    "text": None, #"Optional text that appears within the attachment",
    "footer": None,
    "ts": 123456789
}




