import re
import copy
import shlex
import abc
from billy.sunlightparsers import MemberParser
from .message_handler import ContactQueryMessageHandler

import time

class BaseQueryHandler(metaclass=abc.ABCMeta):
    """Abstract base class from which all query handlers derive"""

    def __init__(self):

        self.PENDING = False
        self.ERROR = None
        self._query_results = None

    def run_query(self, incoming_msg):
        """Run query and look for single match."""
        print('Okay running query for', incoming_msg)
        time.sleep(30)
        print('Continuing query for', incoming_msg)
        if not self._query_results:
            self._initialize_results(incoming_msg)
        else:
            self._query_results = self._narrow_results(incoming_msg)

        valid, found = self._validate_results()

        if not valid:
            self.PENDING = False
            self.ERROR = 'NO_RESULTS'
        elif not found:
            self.PENDING = True
        else:
            self.PENDING = False
            self._extract_results()

        reply = self._reply(incoming_msg)
        return reply

    def _narrow_results(self, keywords):
        """Narrow query_results down based on matching keywords."""

        # Try splitting keywords using shlex to preserve words within qoutes
        try:
            keywords = shlex.split(keywords)
        except:
            keywords = keywords.split()

        # If single integer, try getting query_results at that index
        if len(keywords) == 1:
            try:
                return [self._query_results[int(keywords[0])-1]]
            except:
                pass

        # Find matches based on entered keywords.
        # All key words must be in list item to qualify as match.
        matches = []
        for match in self._query_results:
            if all([k in match[1].values() for k in keywords]):
                matches.append(match)

        return matches

    def _validate_results(self):
        """Validate whether results exist and that requested item found."""

        if not self._query_results:
            valid, found = False, False
        elif len(self._query_results) == 1:
            valid, found = True, True
        else:
            valid, found = True, False

        return valid, found

    @abc.abstractmethod
    def _initialize_results(self):
        """Return initial query results from Sunlight API call"""
        pass

    @abc.abstractmethod
    def _extract_results(self):
        """Set instance variables with results data"""
        pass

    @abc.abstractmethod
    def _reply(self):
        """Create and return message based on query results"""
        pass


class MemberQuery(BaseQueryHandler):
    """Handles queries for congress member contact info"""

    def __init__(self, msg_handler):
        super().__init__()
        self.msg_handler = msg_handler
        self.member_summary = None
        self.member_data = None

    def _initialize_results(self, incoming_msg):
        """Calls Sunlight legislator API and returns data matching keywords"""

        # if a zip code is in the message, identify
        # zip code and then remove it from the message
        zip_in_msg = re.search(r'\d{5}', incoming_msg)

        if zip_in_msg:
            zipcode = zip_in_msg.group()
            incoming_msg = incoming_msg.replace(zipcode, '')
        else:
            zipcode = None

        self._query_results = MemberParser.find_members(incoming_msg, zipcode)

    def _extract_results(self):
        """Set instance variables with member summary and full member data."""

        self.member_summary = self._query_results[0][0]
        self.member_data = self._query_results[0][1]

    def _reply(self, msg):
        """Instantiate handler with query data and return reply message"""

        msg_handler = self.msg_handler(query=msg,
                                       pending=self.PENDING,
                                       error=self.ERROR,
                                       summary=self.member_summary,
                                       data=self.member_data,
                                       results=self._query_results)

        return msg_handler.get_message()
