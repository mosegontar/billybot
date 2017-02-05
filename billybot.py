import os
import time
from collections import defaultdict
from config import BOT_ID, AT_BOT, READ_WEBSOCKET_DELAY, SLACK_CLIENT as SC

class BillyBot(object):

    def __init__(self):
        self.conversation = dict()

    def handle_command(self, user_id, username, command, channel):
        if len(self.conversation.get(user_id)) > 1:
            self.conversation.get(user_id).pop(0)
        convo = self.conversation.get(user_id)[0]
        message = username + ' nice to meet you, you said:\n {}'.format(convo) 
        SC.api_call("chat.postMessage", channel=channel, text=message, as_user=True)

    def get_user_name(self, user_id):
        if not user_id:
            return

        all_users = SC.api_call("users.list").get('members')
        user = [u for u in all_users if u['id'] == user_id]
        return user[0]['name']

    def parse_slack_output(self, stream_output):
        """
            The Slack Real Time Messaging API is an events firehose.
            this parsing function returns None unless a message is
            directed at the Bot, based on its ID.
        """

        output_list = stream_output

        if output_list:

            for message in output_list:
                channel = message.get('channel')
                text = message.get('text')
                user_id = message.get('user')
                username = "<@{}>".format(self.get_user_name(user_id))
                if (channel and text) and message['user'] != BOT_ID:
                    self.conversation.setdefault(user_id, [])
                    self.conversation[user_id].append(text)
                    # Channels that start with D are direct messages
                    if channel.startswith('D'):
                        username = ''
                        return user_id, username, text, channel
                    elif AT_BOT in text:
                        text = text.split(AT_BOT)[1].strip().lower()
                        return user_id, username, text, channel
                    else:
                        pass

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
