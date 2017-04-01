import time
import random
from threading import Thread

from .config import BOT_ID, AT_BOT, READ_WEBSOCKET_DELAY, SLACK_CLIENT
from .message_handler import ContactQueryMessageHandler
from .query_handler import MemberQuery

active_queries = dict()

class MessageTriage(object):

    def __init__(self, message, query_handler=None):

        self.message = message
        self.query_handler = query_handler

    def process_query(self):
        """Run query and return query handler, reply, and attachment."""

        if self.query_handler:
            query_handler = self.query_handler
        else:
            query_handler = MemberQuery(ContactQueryMessageHandler)

        reply = query_handler.run_query(self.message.strip(':'))
        return query_handler, reply


class MessageOperator(Thread):

    def __init__(self, u_id, u_name, cmnd, chnl):
        Thread.__init__(self)
        self.user_id = u_id
        self.username = u_name
        self.channel = chnl
        self.command = cmnd

    def run(self):
        """Triage message and prepare reply to send."""
        if self.command == 'Warren':
            time.sleep(20)
        active_query = active_queries.get(self.user_id)

        triage = MessageTriage(self.command, active_query)
        query_handler, reply = triage.process_query()

        if not query_handler.PENDING:
            active_queries[self.user_id] = None
        else:
            active_queries[self.user_id] = query_handler

        for msg in reply:
            text = msg['text']
            attachments = msg['attachments']
            self.send_message(self.username, text, attachments, self.channel)

    def send_message(self, username, text, attachments, channel):
        """Send message back to user via slack api call."""

        SLACK_CLIENT.api_call("chat.postMessage",
                              channel=channel,
                              text=text,
                              as_user=True,
                              unfurl_media=False,
                              unfurl_links=False,
                              attachments=attachments)


class BillyBot(object):

    def parse_slack_output(self, stream_output):
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

    def run(self):
        """Connect to Slack RTM and start accepting incoming messages."""

        if SLACK_CLIENT.rtm_connect():
            print('BillyBot is running!')
            while True:
                incoming_data = SLACK_CLIENT.rtm_read()
                u_id, u_name, cmnd, chnl = self.parse_slack_output(incoming_data)
                if cmnd and chnl:
                    print('Okay will deal with', cmnd)
                    thread = MessageOperator(u_id, u_name, cmnd, chnl)
                    thread.start()

                time.sleep(READ_WEBSOCKET_DELAY)
        else:
            print('Connection failed :(')


if __name__ == '__main__':
    billy = BillyBot()
    billy.run()
