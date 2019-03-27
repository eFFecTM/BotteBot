import configparser
from slackclient import SlackClient

config = configparser.ConfigParser()
config.read('init.ini')

SLACK_BOT_TOKEN = str(config.get('slackbot', 'SLACK_BOT_TOKEN'))

slackbot = SlackClient(SLACK_BOT_TOKEN)

slackbot.rtm_connect(with_team_state=False)

message = "go fuck yourself"
channel = "DHCCP42P6"

events = slackbot.rtm_read()

print(events)

# print(slackbot.api_call("chat.postMessage", as_user="true", channel=channel, text=message))

# slackbot.rtm_send_message('random', 'am testing')

# slackbot.send_message(slack_channel, message)

