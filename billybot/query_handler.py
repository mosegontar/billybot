from billy.sunlightparsers import MemberParser, BillParser
from .query_handler import BaseQueryHandler
from .message_handler import VoteQueryMessageHandler, ErrorMessageHandler


class BaseQueryHandler(object):

    def __init__(self, *args):

        self.requested_data = args
        self.query_results = None
        self.PENDING = 1

    def run_query(self, incoming_msg):
        """Run query and look for single match."""

        if not self.query_results:
            self._initialize_results(incoming_msg)
        else:
            self.query_results = self._narrow_results(incoming_msg)

        valid, found = self._validate_results()

        if not valid:
            self.PENDING = 0
            # prepare error
            pass

        if not found:
            # prepare msg
            self.PENDING += 1

        if found:
            self.PENDING = 0
            self._extract_results()
            self._package_message()

    def _narrow_results(self, keywords):
        """Narrow query_results down based on matching keywords."""

        keywords = keywords.split()
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

    def __init__(self, *args):
        super().__init__(*args)

        self.member_summary = None
        self.bioguide_id = None
        self.member_data = None

    def _initialize_results(self, incoming_msg):
        """Initialize query results with call to Sunlight API."""

        self.query_results = MemberParser.find_members(incoming_msg)

    def _extract_results(self):
        """Set instance variables with member summary and full member data."""

        self.member_summary = self.query_results[0][0]
        self.member_data = self.query_results[0][1]

    def _package_message(self):
        """Package message and return reply and attachments."""

        for item in self.requested_data:
            print(self.member_data[item])


class ContactQuery(BaseQueryHandler):

    def __init__(self):

        self.member = MemberQuery('first_name', 
                                  'last_name', 
                                  'website',
                                  'phone',
                                  'twitter_id')
        self.PENDING = 1

    def run_query(self, incoming_msg):
        """Run member.run_query if a member query is pending."""
        
        if self.PENDING:
            self.member.run_query(incoming_msg)
            self.PENDING = self.member.PENDING








