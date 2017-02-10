import os
import time

from .config import BOT_ID, AT_BOT, READ_WEBSOCKET_DELAY, SLACK_CLIENT
from .query_handler import VoteQuery


class MessageTriage(object):

    def __init__(self, message, query_object=None):

        self.message = message
        self.query_object = query_object

    def identify_query(self):
        """Send message to proper QueryHandler object.

        Return QueryHandler object and reply for user.
        """

        if self.query_object and self.query_object.AWAITING_REPLY:
            query, reply = self.query_object.run_query(self.message, self.query_object)
            return query, reply

        if self.message.startswith('vote'):
            query, reply = VoteQuery.run_query(self.message)
            return query, reply


class BillyBot(object):

    def __init__(self):
        self.active_queries = dict()

    def handle_command(self, user_id, username, command, channel):
        """Triage message and prepare reply to use."""

        active_query = self.active_queries.get(user_id)

        triage = MessageTriage(command, active_query)
        query, reply = triage.identify_query()

        self.active_queries[user_id] = query

        self.send_message(username, reply, channel)

    def send_message(self, username, message, channel):
        """Send message back to user via slack api call."""

        SLACK_CLIENT.api_call("chat.postMessage", 
                              channel=channel, 
                              text=message, 
                              as_user=True, 
                              unfurl_media=False,
                              unfurl_links=False)        

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
