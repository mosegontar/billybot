import time
import random
import threading

from .config import BOT_ID, AT_BOT, READ_WEBSOCKET_DELAY, SLACK_CLIENT
from .message_handler import ContactQueryMessageHandler
from .query_handler import MemberQuery


class BillyBot(object):

    def connect(self):
        """Connect to Slack RTM and start accepting incoming messages."""

        MessageOperator.ACTIVE_QUERIES = dict()

        if SLACK_CLIENT.rtm_connect():
            print('BillyBot is running!')

            while True:

                stream = SLACK_CLIENT.rtm_read()
                user_id, username, command, channel = self.parse_stream(stream)

                if command and channel:
                    thread = MessageOperator(user_id, username, command, channel)
                    thread.daemon = True
                    thread.start()

                time.sleep(READ_WEBSOCKET_DELAY)
        else:
            print('Connection failed :(')

    def parse_stream(self, stream_output):
        """
            The Slack Real Time Messaging API is an events firehose.
            this parsing function returns None unless a message is
            directed at the Bot, based on its ID.
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


class MessageOperator(threading.Thread):

    ACTIVE_QUERIES = dict()

    def __init__(self, user_id, username, command, channel):
        threading.Thread.__init__(self)
        self.user_id = user_id
        self.username = username
        self.channel = channel
        self.message = command
        self.active_query = MessageOperator.ACTIVE_QUERIES.get(self.user_id)

    @classmethod
    def update_queries(cls, user_id=None, handler=None):

        cls.ACTIVE_QUERIES[user_id] = handler

    def run(self):
        """Triage message and prepare reply to send."""

        if self.message == 'Warren':
            time.sleep(30)

        query_handler, reply = self.process_query()

        if not query_handler.PENDING:
            self.update_queries(self.user_id, None)
        else:
            self.update_queries(self.user_id, query_handler)

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
