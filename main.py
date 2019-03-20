import configparser
from slackclient import SlackClient

config = configparser.ConfigParser()
config.read('init.ini')

SLACK_BOT_TOKEN=config.get('SLACK_BOT_TOKEN')

slackbot = SlackClient(str(SLACK_BOT_TOKEN))

slackbot.send_message(slack_channel, message)

