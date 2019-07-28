"""This is the main application for the Slackbot called BotteBot."""
import configparser
import json
import logging
import threading
import time
import schedule
import slack
from googletrans import Translator
from oxforddictionaries.words import OxfordDictionaries
import FoodBot
import ImageBot
import RandomBot
import WeatherBot
import HelpBot
from data.sqlquery import SQL_query
from datetime import datetime, timedelta


@slack.RTMClient.run_on(event='message')
def on_message(**payload):
    try:
        data = payload['data']
        global message, attachments, delivery
        message = attachments = None
        if "user" in data:
            user_id, text_received, channel = data['user'], data['text'], data['channel']
        else:
            user_id = bot_id
        if user_id != bot_id:
            webclient = payload['web_client']
            user_name = webclient.users_info(user=user_id)["user"]["name"]
            words_received = text_received.lower().split()
            [channel, words_received] = check_channel(words_received, channel)
            [words_received, mention] = filter_ignore_words(words_received, ignored_words)
            if delivery:
                message = delivery
                delivery = None
            if not message and (mention or (channel not in public_channel_ids)):
                mention_question(user_name, words_received, channel)
            if not message:
                check_random_keywords(user_name, words_received, channel, webclient)
            if message:
                send_message(message, channel, attachments)
    except Exception as e:
        logger.exception(e)


def send_message(text_to_send, channel, attachments):
    client.chat_postMessage(as_user="true", channel=channel, text=text_to_send, attachments=attachments)
    logger.debug('Message sent to {}'.format(channel))


def filter_ignore_words(words_received, ignored_words):
    mentioned = False
    relevant_words = []
    for word in words_received:
        if '@{}'.format(bot_id) in word:
            mentioned = True
        elif word not in ignored_words:
            relevant_words.append(word)
    return relevant_words, mentioned


def check_channel(text_words, channel):
    """Check whether a channel got mentioned"""
    for channel_id in public_channel_ids:
        for word in text_words:
            if '#{}'.format(channel_id.lower()) in word:
                logger.critical(channel_id)
                text_words.remove(word)
                channel = channel_id
                break
    return channel, text_words


def check_random_keywords(user_name, words_received, channel, client):
    """To check for words used in normal conversation, adding insults and gifs/images"""
    global message, counter_threshold, counter, delivery, previous_joke
    if not message and any(word in words_received for word in insult_triggers):
        message = RandomBot.insult(words_received, client, user_ids, trans)
        logger.debug('{} insulted someone in {}'.format(user_name, channel))
    if not message:
        message = RandomBot.definition(words_received, def_triggers, trans, oxford)
        if message:
            logger.debug('{} asked for a definition a word in {}'.format(user_name, channel))
    if not message:
        message = RandomBot.repeat(words_received, repeat_triggers)
        if message:
            logger.debug('{} repeated a word in {}'.format(user_name, channel))
    if not message:
        if counter >= counter_threshold:
            if (previous_joke + timedelta(hours=2)) < datetime.now():
                [message, delivery] = RandomBot.joke()
                previous_joke = datetime.now()
            counter_threshold = RandomBot.generate_threshold(8, 20)
            counter = 0
            logger.debug('Joke joked. Joking again in {} messages'.format(counter_threshold))
        else:
            counter += 1


def check_general_keywords(user_name, words_received, channel):
    """Check for serious shit. Predefined commands etc."""
    global message
    global attachments
    if not message and any(word in words_received for word in help_triggers):
        message = HelpBot.get_list_of_commands()
        logger.debug('{} asked the HelpBot for info in channel {}'.format(user_name, channel))
    if not message:
        for food_trigger in food_triggers:
            if food_trigger in words_received:
                logger.debug('{} asked the FoodBot a request in channel {}'.format(user_name, channel))
                message = FoodBot.process_call(user_name, words_received, set_triggers, overview_triggers, order_triggers,
                                       schedule_triggers, add_triggers, remove_triggers, resto_triggers, rating_triggers, food_trigger)
    if not message and any(word in words_received for word in menu_triggers):
        logger.debug('{} asked the Foodbot for menu in channel {}'.format(user_name, channel))
        message = FoodBot.get_menu(words_received)
    if not message and any(word in words_received for word in resto_triggers):
        logger.debug('{} asked the Foodbot for restaurants in channel {}'.format(user_name, channel))
        message = FoodBot.get_restaurants(words_received)
    if not message and any((word in words_received for word in image_triggers)) and not attachments:
        logger.debug('{} asked the ImageBot a request in channel {}'.format(user_name, channel))
        message, attachments = ImageBot.find_image(words_received, image_triggers)
    if not message and any((word in words_received for word in joke_triggers)):
        message = "You really need to find help. And friends. Bye."
    if not message and any((word in words_received for word in no_imaginelab_triggers)):
        logger.debug('{} asked the Bottebot to toggle ImagineLab for this week in channel {}'.format(user_name, channel))
        message = toggle_imaginelab()


def mention_question(user_name, words_received, channel):
    """bot got mentioned or pm'd, answer the question"""
    logger.debug('BotteBot got mentioned in {}'.format(channel))
    global message
    if not message:
        check_general_keywords(user_name, words_received, channel)
    if not message and any(word in words_received for word in weather_triggers):
        message = WeatherBot.get_weather_message(words_received, API_KEY)
    if not message:
        message = RandomBot.lmgtfy(words_received, lmgtfy_triggers)
    if not message:
        message = HelpBot.report_bug(words_received, bugreport_triggers, user_name)


class Scheduler(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)
            if stop:
                break


def print_where_food_notification():
    if is_imaginelab:
        send_message("<!channel> Where are we going to order today?", notification_channel, None)


def print_what_food_notification():
    global is_imaginelab
    if is_imaginelab:
        send_message("<!channel> What do you all want to order?", notification_channel, None)
    is_imaginelab = True


def toggle_imaginelab():
    global is_imaginelab
    if is_imaginelab:
        send_message("<!channel> iMagineLab is cancelled for this week!", notification_channel, None)
        is_imaginelab = False
        return "iMagineLab is cancelled for this week."
    else:
        send_message("<!channel> iMagineLab has been rescheduled for this week!", notification_channel, None)
        is_imaginelab = True
        return "iMagineLab has been rescheduled for this week."


# Create global logger
logger = logging.getLogger('main')
formatstring = "%(asctime)s - %(name)s:%(funcName)s:%(lineno)i - %(levelname)s - %(message)s"
logging.basicConfig(format=formatstring, level=logging.DEBUG)
logger.info('Starting BotteBot application...')

# Read init file
init = configparser.ConfigParser()
init.read('init.ini')
SLACK_BOT_TOKEN = str(init.get('slackbot', 'SLACK_BOT_TOKEN'))
API_KEY = str(init.get('open_weather_map', 'API_KEY'))
OXFORD_ID = str(init.get('oxford', 'ID'))
OXFORD_KEY = str(init.get('oxford', 'KEY'))
oxford = OxfordDictionaries(app_id=OXFORD_ID, app_key=OXFORD_KEY)

# Stopping scheduler when bottebot is shutting down
stop = False

# Is there an imaginelab this week?
is_imaginelab = True

# Define trigger words
config = configparser.ConfigParser()
config.read('config.ini')

notification_channel = str(config.get("scheduler", "NOTIFICATION_CHANNEL"))
where_time = str(config.get("scheduler", "WHERE_TIME"))
what_time = str(config.get("scheduler", "WHAT_TIME"))
schedule.every().wednesday.at(where_time).do(print_where_food_notification)
schedule.every().wednesday.at(what_time).do(print_what_food_notification)
schedule.every().wednesday.at("09:00").do(FoodBot.update_restaurant_database)
thread = Scheduler()
thread.start()


weather_triggers = json.loads(config.get("triggers", "WEATHER"))
insult_triggers = json.loads(config.get("triggers", "INSULT"))
lmgtfy_triggers = json.loads(config.get("triggers", "LMGTFY"))
def_triggers = json.loads(config.get("triggers", "DEF"))
food_triggers = json.loads(config.get("triggers", "FOOD"))
repeat_triggers = json.loads(config.get("triggers", "INSULT"))
image_triggers = json.loads(config.get("triggers", "IMAGE"))
help_triggers = json.loads(config.get("triggers", "HELP"))
joke_triggers = json.loads(config.get("triggers", "JOKE"))
resto_triggers = json.loads(config.get("triggers", "RESTO"))
menu_triggers = json.loads(config.get("triggers", "MENU"))
set_triggers = json.loads(config.get("triggers", "SET"))
overview_triggers = json.loads(config.get("triggers", "OVERVIEW"))
order_triggers = json.loads(config.get("triggers", "ORDER"))
schedule_triggers = json.loads(config.get("triggers", "SCHEDULE"))
add_triggers = json.loads(config.get("triggers", "ADD"))
remove_triggers = json.loads(config.get("triggers", "REMOVE"))
rating_triggers = json.loads(config.get("triggers", 'RATING'))
no_imaginelab_triggers = json.loads(config.get("triggers", "NO_IMAGINELAB"))
bugreport_triggers = json.loads(config.get("triggers", "BUG_REPORT"))

# Define ignored words
ignored_words = json.loads(config.get("triggers", "IGNORED_WORDS"))

# Init message and translator
message = None
attachments = None
delivery = None
counter = 0
counter_threshold = RandomBot.generate_threshold(1, 10)
trans = Translator()

# Get all user IDs and channel IDs
client = slack.WebClient(token=SLACK_BOT_TOKEN)
bot_id = client.auth_test()["user_id"]
user_ids = [element["id"] for element in client.users_list()["members"]]
public_channel_ids = [element["id"] for element in client.channels_list()["channels"]]

#joke limiter
previous_joke = datetime.now() - timedelta(hours=2)

# Connect to SQLite3 database
s = SQL_query('data/imaginelab.db')
logger.info('Connected to SQLite database!')
# s.sql_delete('DELETE FROM restaurant_database')
FoodBot.update_restaurant_database()

# Connect to Slack
slackbot = slack.RTMClient(token=SLACK_BOT_TOKEN)
logger.info('Connected to Slack!')
slackbot.start()
stop = True
