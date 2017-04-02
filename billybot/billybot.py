import sys
import time
import threading
import datetime

from .message_handler import ContactQueryMessageHandler
from .query_handler import MemberQuery
from .config import (BOT_ID, AT_BOT, READ_WEBSOCKET_DELAY, SLACK_CLIENT,
    MAX_THREAD_AGE, OLD_THREAD_LIMIT)


class BillyBot(object):

    def connect(self):
        """Connect to Slack RTM and start accepting incoming messages."""

        if SLACK_CLIENT.rtm_connect():
            print('BillyBot is running!')

            while True:

                too_many = self._monitor_old_threads()
                if too_many:
                    return

                stream = SLACK_CLIENT.rtm_read()
                user_id, username, command, channel = self.parse_stream(stream)

                if command and channel:
                    thread = MessageTriage(user_id, username, command, channel)
                    thread.daemon = True # daemons will die if MainThread exits
                    thread.start()

                time.sleep(READ_WEBSOCKET_DELAY)

        else:
            print('Connection failed :(')

    def parse_stream(self, stream_output):
        """The Slack Real Time Messaging API is an events firehose.

        This parsing function returns None unless a message is
        directed at the Bot, based on its ID.

        https://www.fullstackpython.com/blog/build-first-slack-bot-python.html
        """

        output_list = stream_output
        if output_list:

            for message in output_list:

                AT_BOT_REPLY = False
                DIRECT_MESSAGE = False

                channel = message.get('channel')
                text = message.get('text')
                user_id = message.get('user')

                if not user_id:
                    break

                if (channel and text) and message['user'] != BOT_ID:

                    username = "<@{}>".format(user_id)

                    # Channels that start with D are direct messages
                    if channel.startswith('D'):
                        DIRECT_MESSAGE = True
                        username = ''

                    if AT_BOT in text:
                        AT_BOT_REPLY = True
                        text = text.split(AT_BOT)[1].strip()

                    if DIRECT_MESSAGE or AT_BOT_REPLY:

                        return user_id, username, text, channel

        return None, None, None, None

    def _monitor_old_threads(self):
        """Check how many active and old threads are alive."""

        active_threads = [thread.time_alive for thread in threading.enumerate()[1:]]

        old_threads = [item >= MAX_THREAD_AGE for item in active_threads]

        # If we have too many old threads, it means that Thread instances
        # 'run' methods are taking a long time to return (if they are to
        # return at all). This is an indication that there is some problem
        # in our code and we exit.
        if len(old_threads) > OLD_THREAD_LIMIT:

            # print data on old threads to aid debugging
            print('Old Threads: ')
            for thread in old_threads:
                print('{}: {} via {}'.format(thread.username,
                                             thread.message,
                                             thread.active_query))
            return True

        return False


class MessageTriage(threading.Thread):
    """MessageTriage instances run in their own thread and process queries."""

    # We maintain a class variable dictionary with user_id as key and the
    # current query_handler object as the value. This allows us to access
    # the state of a query that required additional user input to resolve.
    ACTIVE_QUERIES = dict()

    def __init__(self, user_id, username, command, channel):

        threading.Thread.__init__(self)
        self._thread_initiated = datetime.datetime.now().timestamp()
        self.name = user_id  # name of the current thread

        self.user_id = user_id
        self.username = username
        self.channel = channel
        self.message = command

        self.active_query = MessageTriage.ACTIVE_QUERIES.get(self.user_id)

    @property
    def time_alive(self):
        """Return number of seconds the thread instance has been alive."""

        current_time = datetime.datetime.now().timestamp()
        return current_time - self._thread_initiated

    def run(self):
        """Triage message and prepare reply to send.

        This method overrides the default Thread.run() implementation.
        """

        query_handler, reply = self.process_query()

        if not query_handler.PENDING:
            MessageTriage.ACTIVE_QUERIES[self.user_id] = None
        else:
            MessageTriage.ACTIVE_QUERIES[self.user_id] = query_handler

        for msg in reply:
            text = msg['text']
            attachments = msg['attachments']
            self.send_message(self.username, text, attachments, self.channel)

    def process_query(self):
        """Run query and return query handler, reply, and attachment."""

        if self.active_query:
            query_handler = self.active_query
        else:
            query_handler = MemberQuery(ContactQueryMessageHandler)

        reply = query_handler.run_query(self.message.strip(':'))

        return query_handler, reply

    def send_message(self, username, text, attachments, channel):
        """Send message back to user via slack api call."""

        SLACK_CLIENT.api_call("chat.postMessage",
                              channel=channel,
                              text=text,
                              as_user=True,
                              unfurl_media=False,
                              unfurl_links=False,
                              attachments=attachments)


if __name__ == '__main__':
    billy = BillyBot()
    billy.connect()
