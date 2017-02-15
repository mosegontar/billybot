import re
import copy
from billy.sunlightparsers import MemberParser, BillParser
from .message_handler import MessageHandler


class BaseQueryHandler(object):

    def __init__(self):

        self.query_results = None
        self.PENDING = False

    def run_query(self, incoming_msg):
        """Run query and look for single match."""

        if not self.query_results:
            self._initialize_results(incoming_msg)
        else:
            self.query_results = self._narrow_results(incoming_msg)

        valid, found = self._validate_results()

        if not valid:
            self.PENDING = False

        if not found:
            self.PENDING = True

        if found:
            self.PENDING = False
            self._extract_results()

        reply = self._package_message(incoming_msg)
        return reply

    def _narrow_results(self, keywords):
        """Narrow query_results down based on matching keywords."""

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
        self.bioguide_id = None
        self.member_data = None
        self.msg_hander = None

    def _initialize_results(self, incoming_msg):
        """Initialize query results with call to Sunlight API."""

        zip_in_msg = re.search(r'\d{5}', incoming_msg)
        
        if zip_in_msg:
            zipcode = zip_in_msg.group()
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

        if not self.PENDING:
            primary = 'Here you go :)'
            secondary = 'Anything else I can do for you?'
            data = {'title': self.member_summary,
                    'title_link': self.member_data['website'],
                    'fields': [{'title': 'Twitter',
                                'value': 'twitter.com/{}'.format(self.member_data['twitter_id']),
                                'short': True},
                               {'title': 'Phone',
                                'value': self.member_data['phone'],
                                'short': True}],
                    'text': 'Contact info'}

        else:
            primary = "I found multiple matches for '{}'".format(query)
            secondary = "Which one did you mean?"
            data = {'title': "Results for '{}'".format(query),
                    'title_link': None,
                    'fields': [],
                    'text': [item[0] for item in self.query_results]}


        msg_handler = MessageHandler(primary, secondary, **data)
        reply = msg_handler.make_reply()
        return reply
















