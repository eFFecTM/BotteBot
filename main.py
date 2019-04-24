import configparser
from googletrans import Translator
from slackclient import SlackClient
from oxforddictionaries.words import OxfordDictionaries
import time
import FoodBot
import WeatherBot
import RandomBot

weather_triggers = ['forecast', 'weather', 'weer', 'voorspelling']
insult_triggers = ["insult", "got em", "scheld", "jan", "bot", "botte"]
lmgtfy_triggers = ["lmgtfy", "opzoeken"]
def_triggers = ["thefuck", "def", "definitie", "verklaar", "define"]
food_triggers = ["food", "eten"]
repeat_triggers = ["echo", "herhaal", "repeat"]

message = None


def send_message(text_to_send, channel):
    slackbot.api_call("chat.postMessage", as_user="true", channel=channel, text=text_to_send)


def check_channel(text_received, channel):
    """Check whether a channel got mentioned"""
    for channel_id in public_channel_ids:
        if '#{}'.format(channel_id) in text_received:
            channel = channel_id
            break
    return channel


def check_random_keywords(user_name, text_received, channel):
    """To check for words used in normal conversation, adding instults and gifs/images"""
    global message
    if not message and any(word in text_received.lower() for word in insult_triggers):
        message = RandomBot.insult(text_received, slackbot, user_ids, trans)
    if not message:
        message = RandomBot.definition(text_received, def_triggers, trans, oxford)
    if not message:
        message = RandomBot.repeat(text_received, repeat_triggers, public_channel_ids)


def check_general_keywords(user_name, text_received, channel):
    """Check for serious shit. Predefined commands etc."""
    global message
    if not message and any(word in text_received.lower() for word in food_triggers):
        message = FoodBot.process_call(user_name, text_received, channel)


def mention_question(user_name, text_received, channel):
    """bot got mentioned or pm'd, answer the question"""
    global message
    if not message:
        check_general_keywords(user_name, text_received, channel)
    if not message and any(word in text_received.lower() for word in weather_triggers):
        message = WeatherBot.get_weather_message(text_received, API_KEY)
    if not message:
        message = RandomBot.lmgtfy(text_received, lmgtfy_triggers)


def parse(events):
    for event in events:
        if event['type'] == 'message' and not "subtype" in event:
            global message
            message = None
            user_id, text_received, channel = event['user'], event['text'], event['channel']
            if user_id != bot_id:
                user_name = slackbot.api_call("users.info", user=user_id)["user"]["name"]
                if ('@{}'.format(bot_id) in text_received) or (channel not in public_channel_ids):
                    mention_question(user_name, text_received, channel)
                if not message:
                    check_random_keywords(user_name, text_received, channel)
                if message:
                    channel = check_channel(text_received, channel)
                    send_message(message, channel)


# Read config file
config = configparser.ConfigParser()
config.read('init.ini')
SLACK_BOT_TOKEN = str(config.get('slackbot', 'SLACK_BOT_TOKEN'))
API_KEY = str(config.get('open_weather_map', 'API_KEY'))

OXFORD_ID = str(config.get('oxford', 'ID'))
OXFORD_KEY = str(config.get('oxford', 'KEY'))
oxford = OxfordDictionaries(app_id=OXFORD_ID, app_key=OXFORD_KEY)

# Connect to Slack
slackbot = SlackClient(SLACK_BOT_TOKEN)
slackbot.rtm_connect(with_team_state=False)
print("Started Slackbot")

# Get all user IDs and channel IDs
bot_id = slackbot.api_call("auth.test")["user_id"]
user_ids = [element["id"] for element in slackbot.api_call("users.list")["members"]]
public_channel_ids = [element["id"] for element in slackbot.api_call("channels.list")["channels"]]

trans = Translator()

running = True

while running:
    try:
        parse(slackbot.rtm_read())
        FoodBot.save_data()
        time.sleep(1)
    except KeyboardInterrupt as e:
        print("stopped by keyboard interrupt")
        running = False
    except Exception as e:
        print(e)

