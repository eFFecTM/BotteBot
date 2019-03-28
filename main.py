import configparser
import time
import requests

from slackclient import SlackClient

insult_triggers = ["insult", "got em"]


def send_message(text_to_send, channel):
    slackbot.api_call("chat.postMessage", as_user="true", channel=channel, text=text_to_send)


def check_random_keywords(user_name, text_received, channel):
    """To check for words used in normal conversation, adding instults and gifs/images"""
    if any(word in text_received for word in insult_triggers):
        found = False
        for user_id_mention in user_ids:
            if '@{}'.format(user_id_mention) in text_received:
                found = True
                url = "https://insult.mattbas.org/api/insult?who=" \
                      + slackbot.api_call("users.info", user=user_id_mention)["user"]["profile"]["first_name"]
                r = requests.get(url)
        if not found:
            r = requests.get("https://insult.mattbas.org/api/insult")
        send_message(r.content, channel)


def check_general_keywords(user_name, text_received, channel):
    """Check for serious shit. Predefined commands etc."""
    pass


def mention_question(user_name, text_received, channel):
    """bot got mentioned or pm'd, answer the question"""
    check_general_keywords(user_name, text_received, channel)
    message = "hello " + user_name + ", you rule"
    slackbot.api_call("chat.postMessage", as_user="true", channel=channel, text=message)


def parse(events):
    for event in events:
        if event['type'] == 'message' and not "subtype" in event:
            user_id, text_received, channel = event['user'], event['text'], event['channel']
            if user_id != bot_id:
                user_name = slackbot.api_call("users.info", user=user_id)["user"]["name"]
                if ('@{}'.format(bot_id) in text_received) or (channel not in public_channel_ids):
                    mention_question(user_name, text_received, channel)
                else:
                    check_random_keywords(user_name, text_received, channel)


config = configparser.ConfigParser()
config.read('init.ini')

SLACK_BOT_TOKEN = str(config.get('slackbot', 'SLACK_BOT_TOKEN'))

slackbot = SlackClient(SLACK_BOT_TOKEN)

slackbot.rtm_connect(with_team_state=False)

bot_id = slackbot.api_call("auth.test")["user_id"]
user_ids = [element["id"] for element in slackbot.api_call("users.list")["members"]]
public_channel_ids = [element["id"] for element in slackbot.api_call("channels.list")["channels"]]

while(True):
    parse(slackbot.rtm_read())
    time.sleep(1)



# print(events)

# print(slackbot.api_call("chat.postMessage", as_user="true", channel=channel, text=message))

# slackbot.rtm_send_message('random', 'am testing')

# slackbot.send_message(slack_channel, message)

