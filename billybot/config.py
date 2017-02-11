import os
from slackclient import SlackClient


# Billy Bot's Slack ID
BOT_ID = os.environ.get('BOT_ID')

# constants
AT_BOT = '<@{}>'.format(BOT_ID)

# Slack Client Config
SLACK_CLIENT = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
READ_WEBSOCKET_DELAY = 1


slack_attachment = {
    "fallback": None, # "Required plain-text summary of the attachment."
    "color": None, # color hex value
    "pretext": None, #"Optional text that appears above the attachment block"
    "author_name": None ,
    "author_link": None,
    "title": None,
    "title_link": None,
    "text": None, #"Optional text that appears within the attachment",
    "footer": None,
    "ts": 123456789
}