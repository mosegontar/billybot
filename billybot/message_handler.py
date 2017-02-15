import json
import copy
from .config import slack_attachment

from eng_join import join

class MessageHandler(object):

    message_dictionary = dict()
    message_dictionary['NONE'] = ''
    message_dictionary['RESOLVED'] = "Here you go :) Let me know if there is anything else I can do."
    message_dictionary['RESULTS'] = "Okay, here's what I found:"
    message_dictionary['CLARIFY'] = "Which one did you mean?"
    message_dictionary['NO_RESULTS'] = "Ugh, I couldn't find anything :("
    message_dictionary['GET_HELP'] = "Type 'help' to get help!"

    def __init__(self, primary, secondary, **kwargs):
        
        self.primary_msg = MessageHandler.message_dictionary[primary]
        self.secondary_msg = MessageHandler.message_dictionary[secondary]
        self.incoming_data = kwargs

        self.attachment = None


    def format_attachment(self, attachment):

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
        self.format_attachment(copy.deepcopy(slack_attachment))
        reply = [{'text': self.primary_msg,
                  'attachments': self.attachment}]

        if self.secondary_msg:
            second = {'text': self.secondary_msg,
                      'attachments': None}
            reply.append(second)

        return reply

    @classmethod
    def create_attachment_fields(cls, proposed_fields):

        fields = []

        for title, value in proposed_fields:
            if value:
                fields.append(dict([('title', title), 
                                   ('value', value), 
                                   ('short', True)]))

        return fields

