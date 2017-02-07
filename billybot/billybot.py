import os
import time
from collections import defaultdict
from config import BOT_ID, AT_BOT, READ_WEBSOCKET_DELAY, SLACK_CLIENT as SC

class BillyBot(object):

    def __init__(self):
        self.conversation = dict()

    def handle_command(self, user_id, username, command, channel):
        convo = command
        message = username + ' nice to meet you, you said:\n {}'.format(convo) 
        SC.api_call("chat.postMessage", channel=channel, text=message, as_user=True)

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

                if (channel and text) and message['user'] != BOT_ID:
                    
                    username = "<@{}>".format(user_id) 
                    
                    # Channels that start with D are direct messages
                    if channel.startswith('D'):
                        DIRECT_MESSAGE = True
                        username = ''

                    if AT_BOT in text:
                        AT_BOT_REPLY = True
                        text = text.split(AT_BOT)[1].strip().lower()

                    if DIRECT_MESSAGE or AT_BOT_REPLY:
                        return user_id, username, text, channel

        return None, None, None, None

    def run(self):

        if SC.rtm_connect():
            print('BillyBot is running!')
            while True:
                user_id, username, command, channel = self.parse_slack_output(SC.rtm_read())
                if command and channel:
                    self.handle_command(user_id, username, command, channel)
                time.sleep(READ_WEBSOCKET_DELAY)
        else:
            print('Connection failed :(')


if __name__ == '__main__':
    billy = BillyBot()
    billy.run()
