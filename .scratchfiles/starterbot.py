import os
import time
from slackclient import SlackClient

from billy import SunlightAPI, LegislatorParser

def getsun(name):
    results = SunlightAPI.search_legislators(last_name=name.title())
    bio_id = LegislatorParser.get_bio_ids(results)
    return bio_id    

# startbot's ID as an environment variable
BOT_ID = os.environ.get('BOT_ID')

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = 'do'

# instantiate slack
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"
    else:
        response = getsun(command)

    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output

    if output_list and len(output_list) > 0:

        for output in output_list:
            if ('channel' in output.keys()) and ('text' in output.keys()) and ('D' in output['channel']):
                if output['user'] != BOT_ID:
                    print("@@@@ DIRECT MESSAGE: %s" % output['text'])

                    return output['text'], output['channel']


        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None                          


if __name__ == '__main__':
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between readings from firehose
    if slack_client.rtm_connect():
        print("Billy is running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print('Connection failed')

