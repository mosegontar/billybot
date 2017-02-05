import os
from slackclient import SlackClient


# Billy Bot's Slack ID
BOT_ID = os.environ.get('BOT_ID')

# constants
AT_BOT = '<@{}>'.format(BOT_ID)

# Slack Client Config
SLACK_CLIENT = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
READ_WEBSOCKET_DELAY = 1