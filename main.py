import configparser
import time

from slackclient import SlackClient


def parse(events):
    for event in events:
        if event['type'] == 'message' and not "subtype" in event:
            user_id, text_received, channel = event['user'], event['text'], event['channel']
            if user_id != bot_id:
                if ('@{}'.format(bot_id) in text_received) or (channel not in public_channels):
                    user_name = slackbot.api_call("users.info", user=user_id)["user"]["name"]
                    message = "hello " + user_name + ", you rule"
                    slackbot.api_call("chat.postMessage", as_user="true", channel=channel, text=message)


config = configparser.ConfigParser()
config.read('init.ini')

SLACK_BOT_TOKEN = str(config.get('slackbot', 'SLACK_BOT_TOKEN'))

slackbot = SlackClient(SLACK_BOT_TOKEN)

slackbot.rtm_connect(with_team_state=False)

bot_id = slackbot.api_call("auth.test")["user_id"]
public_channels = slackbot.api_call("channels.list")

while(True):
    parse(slackbot.rtm_read())
    time.sleep(1)



# print(events)

# print(slackbot.api_call("chat.postMessage", as_user="true", channel=channel, text=message))

# slackbot.rtm_send_message('random', 'am testing')

# slackbot.send_message(slack_channel, message)

