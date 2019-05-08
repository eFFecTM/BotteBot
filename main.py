"""This is the main application for the Slackbot called BotteBot."""
import configparser
from googletrans import Translator
from slackclient import SlackClient
from oxforddictionaries.words import OxfordDictionaries
import time
import FoodBot
import WeatherBot
import RandomBot
import logging
import ImageBot


def send_message(text_to_send, channel, attachments):
    slackbot.api_call("chat.postMessage", as_user="true", channel=channel, text=text_to_send, attachments=attachments)
    logger.debug('Message sent to {}'.format(channel))


def check_channel(text_received, channel):
    """Check whether a channel got mentioned"""
    for channel_id in public_channel_ids:
        if '#{}'.format(channel_id) in text_received:
            channel = channel_id
            break
    return channel


def check_random_keywords(user_name, text_received, channel):
    """To check for words used in normal conversation, adding instults and gifs/images"""
    global message, counter_threshold, counter, delivery
    if not message and any(word in text_received.lower() for word in insult_triggers):
        message = RandomBot.insult(text_received, slackbot, user_ids, trans)
        logger.debug('{} insulted someone in {}'.format(user_name, channel))
    if not message:
        message = RandomBot.definition(text_received, def_triggers, trans, oxford)
        if message:
            logger.debug('{} asked for a definition a word in {}'.format(user_name, channel))
    if not message:
        message = RandomBot.repeat(text_received, repeat_triggers)
        if message:
            logger.debug('{} repeated a word in {}'.format(user_name, channel))
    if not message:
        if counter >= counter_threshold:
            [message, delivery] = RandomBot.joke()
            counter_threshold = RandomBot.generate_threshold(1, 10)
            counter = 0
            logger.debug('Joke joked. Joking again in {} messages'.format(counter_threshold))
        else:
            counter += 1


def check_general_keywords(user_name, text_received, channel):
    """Check for serious shit. Predefined commands etc."""
    global message
    global attachments
    if not message and any(word in text_received.lower() for word in food_triggers):
        message = FoodBot.process_call(user_name, text_received, channel)
    if not message and any((word in text_received.lower() for word in image_triggers)) and not attachments:
        message, attachments = ImageBot.find_image(text_received, channel)


def mention_question(user_name, text_received, channel):
    """bot got mentioned or pm'd, answer the question"""
    logger.debug('BotteBot got mentioned in {}'.format(channel))
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
            global message, attachments, delivery
            message = attachments = None
            user_id, text_received, channel = event['user'], event['text'], event['channel']
            if user_id != bot_id:
                user_name = slackbot.api_call("users.info", user=user_id)["user"]["name"]
                if delivery:
                    message = delivery
                    delivery = None
                if ('@{}'.format(bot_id) in text_received) or (channel not in public_channel_ids):
                    mention_question(user_name, text_received, channel)
                if not message:
                    check_random_keywords(user_name, text_received, channel)
                if message:
                    channel = check_channel(text_received, channel)
                    send_message(message, channel, attachments)


# Create global logger
logger = logging.getLogger('main')
formatstring = "%(asctime)s - %(name)s:%(funcName)s:%(lineno)i - %(levelname)s - %(message)s"
logging.basicConfig(format=formatstring, level=logging.DEBUG)
logger.info('Starting BotteBot application...')

# Read config file
config = configparser.ConfigParser()
config.read('init.ini')
SLACK_BOT_TOKEN = str(config.get('slackbot', 'SLACK_BOT_TOKEN'))
API_KEY = str(config.get('open_weather_map', 'API_KEY'))
OXFORD_ID = str(config.get('oxford', 'ID'))
OXFORD_KEY = str(config.get('oxford', 'KEY'))
oxford = OxfordDictionaries(app_id=OXFORD_ID, app_key=OXFORD_KEY)

# Define trigger words
weather_triggers = ['forecast', 'weather', 'weer', 'voorspelling']
insult_triggers = ["insult", "got em", "scheld", "jan", "bot", "botte"]
lmgtfy_triggers = ["lmgtfy", "opzoeken"]
def_triggers = ["thefuck", "def", "definitie", "verklaar", "define"]
food_triggers = ["food", "eten"]
repeat_triggers = ["echo", "herhaal", "repeat"]
image_triggers = ["image", "photo", "afbeelding", "foto"]

# Init message and translator
message = None
attachments = None
delivery = None
counter = 0
counter_threshold = RandomBot.generate_threshold(1, 10)
trans = Translator()

# Connect to Slack
slackbot = SlackClient(SLACK_BOT_TOKEN)
slackbot.rtm_connect(with_team_state=False)
logger.info('Connected to Slack!')

# Get all user IDs and channel IDs
bot_id = slackbot.api_call("auth.test")["user_id"]
user_ids = [element["id"] for element in slackbot.api_call("users.list")["members"]]
public_channel_ids = [element["id"] for element in slackbot.api_call("channels.list")["channels"]]


# Main loop
running = True
while running:
    try:
        parse(slackbot.rtm_read())
        FoodBot.save_data()
        time.sleep(1)
    except KeyboardInterrupt as e:
        logger.warn("Stopped by keyboard interrupt")
        running = False
    except Exception as e:
        logger.exception(e)

