import time

from .config import BOT_ID, AT_BOT, READ_WEBSOCKET_DELAY, SLACK_CLIENT
from .query_handler import ContactQuery


class MessageTriage(object):

    def __init__(self, message, query_handler=None):

        self.message = message
        self.query_handler = query_handler
        self.command_queries = {'vote': None,
                                'contact': ContactQuery}

    def process_query(self):
        """Run query and return query handler, reply, and attachment."""

        if self.query_handler:

            query_handler = self.query_handler

        else:
            query_handler = ContactQuery()

        reply = query_handler.run_query(self.message)
        return query_handler, reply


class BillyBot(object):

    def __init__(self):
        self.active_queries = dict()

    def handle_command(self, user_id, username, command, channel):
        """Triage message and prepare reply to send."""

        active_query = self.active_queries.get(user_id)

        triage = MessageTriage(command, active_query)
        query_handler, reply = triage.process_query()

        if not query_handler.PENDING:
            self.active_queries[user_id] = None
        else:
            self.active_queries[user_id] = query_handler

        for msg in reply:
            text = msg['text']
            attachments = msg['attachments']
            self.send_message(username, text, attachments, channel)

    def send_message(self, username, text, attachments, channel):
        """Send message back to user via slack api call."""

        SLACK_CLIENT.api_call("chat.postMessage",
                              channel=channel,
                              text=text,
                              as_user=True,
                              unfurl_media=False,
                              unfurl_links=False,
                              attachments=attachments)

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
                user_id, username, command, channel = self.parse_slack_output(SLACK_CLIENT.rtm_read())
                if command and channel:
                    self.handle_command(user_id, username, command, channel)
                time.sleep(READ_WEBSOCKET_DELAY)
        else:
            print('Connection failed :(')


if __name__ == '__main__':
    billy = BillyBot()
    billy.run()
