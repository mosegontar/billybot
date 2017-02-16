import re
import copy
import shlex

from billy.sunlightparsers import MemberParser
from .message_handler import MessageHandler


class BaseQueryHandler(object):

    def __init__(self):

        self.query_results = None
        self.PENDING = False
        self.ERROR = None

    def run_query(self, incoming_msg):
        """Run query and look for single match."""

        if not self.query_results:
            self._initialize_results(incoming_msg)
        else:
            self.query_results = self._narrow_results(incoming_msg)

        valid, found = self._validate_results()

        if not valid:
            self.PENDING = False
            self.ERROR = 'NO_RESULTS'
        elif not found:
            self.PENDING = True
        else:
            self.PENDING = False
            self._extract_results()

        reply = self._package_message(incoming_msg)
        return reply

    def _narrow_results(self, keywords):
        """Narrow query_results down based on matching keywords."""

        try:
            keywords = shlex.split(keywords)
        except:
            keywords = keywords.split()

        # if user entered a number corresponding to the results list order
        if len(keywords) == 1:
            try:
                return [self.query_results[int(keywords[0])-1]]
            except:
                pass

        # find matches based on entered keywords
        matches = []
        for match in self.query_results:
            if all([k in match[1].values() for k in keywords]):
                matches.append(match)

        return matches

    def _validate_results(self):
        """Validate whether results exist and that requested item found."""

        if not self.query_results:
            valid, found = False, False
        elif len(self.query_results) == 1:
            valid, found = True, True
        else:
            valid, found = True, False

        return valid, found


class MemberQuery(BaseQueryHandler):

    def __init__(self):
        super().__init__()

        self.member_summary = None
        self.member_data = None

    def _initialize_results(self, incoming_msg):
        """Initialize query results with call to Sunlight API."""

        # if a zip code is in the message, identify
        # zip code and then remove it from the message
        zip_in_msg = re.search(r'\d{5}', incoming_msg)

        if zip_in_msg:
            zipcode = zip_in_msg.group()
            incoming_msg = incoming_msg.replace(zipcode, '')
        else:
             zipcode = None

        self.query_results = MemberParser.find_members(incoming_msg, zipcode)

    def _extract_results(self):
        """Set instance variables with member summary and full member data."""

        self.member_summary = self.query_results[0][0]
        self.member_data = self.query_results[0][1]


class ContactQuery(MemberQuery):

    def _package_message(self, query):
        """Package message and return reply and attachments."""

        primary_reply = 'NONE'
        secondary_reply = 'NONE'
        data = {'title': None, 'title_link': None,
                'fields': [], 'text': None}

        if self.ERROR:
            primary_reply = self.ERROR

        elif not self.PENDING:

            twitter = self.member_data.get('twitter_id')
            twitter_url = 'twitter.com/{}'.format(twitter) if twitter else None

            proposed_fields = [('Twitter', twitter_url),
                               ('Phone', self.member_data.get('phone')),
                               ('Office', self.member_data.get('office')),
                               ('Contact Form', self.member_data.get('contact_form'))]

            fields = MessageHandler.create_attachment_fields(proposed_fields)

            data['title'] = self.member_summary
            data['title_link'] = self.member_data['website']
            data['fields'] = fields

            primary_reply = 'RESOLVED'
            secondary_reply = 'NONE'

        else:
            primary_reply = 'RESULTS'
            secondary_reply = 'CLARIFY'
            items = [item[0] for item in self.query_results]

            data['text'] = items

        msg_handler = MessageHandler(primary_reply, secondary_reply, **data)
        reply = msg_handler.make_reply()

        return reply

