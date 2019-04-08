import configparser
import time
import requests
import pyowm
import json
from googletrans import Translator
from slackclient import SlackClient
from nltk import word_tokenize, pos_tag, ne_chunk, Tree
from oxforddictionaries.words import OxfordDictionaries

from FoodBot import process_call

weather_triggers = ['forecast', 'weather', 'weer', 'voorspelling']
insult_triggers = ["insult", "got em", "scheld", "jan", "bot", "botte"]
def_triggers = ["thefuck", "def", "definitie"]


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
        translated = trans.translate(r.text, dest='nl', src='en')
        send_message(translated.text, channel)
    found = False
    for word in def_triggers:
        if word in text_received:
            triggered_word = word
            found = True
    if found:
        list_of_words = text_received.split()
        next_word = list_of_words[list_of_words.index(triggered_word) + 1]
        translated = trans.translate(next_word, dest='en')
        info = oxford.get_info_about_word(translated.text)
        try:
            json_info = json.loads(info.text)
            answer = str(json_info['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['definitions'][0])
            translated = trans.translate(answer, src='en', dest='nl')
            send_message(translated.text, channel)
        except ValueError as e:
            r = requests.get("https://insult.mattbas.org/api/adjective")
            send_message("You " + r.text + " person, that's no word!", channel)


def check_general_keywords(user_name, text_received, channel):
    """Check for serious shit. Predefined commands etc."""
    if text_received.startswith("food"):
        send_message(process_call(user_name, text_received, channel), channel)


def get_location(text):
    """Get location in a sentence or question from the user"""
    chunked = ne_chunk(pos_tag(word_tokenize(text)))
    continuous_chunk = []
    current_chunk = []

    for subtree in chunked:
        if type(subtree) == Tree and subtree.label() == 'GPE':
            current_chunk.append(" ".join([token for token, pos in subtree.leaves()]))
        elif current_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
                current_chunk = []
        else:
            continue

    if current_chunk:
        return continuous_chunk[0]
    else:
        return None


def get_weather_message(text_received):
    """Get the current weather at a given location. Default location is Antwerp."""
    owm = pyowm.OWM(API_KEY)
    location = get_location(text_received)
    if location is None:
        location = 'Antwerp'  # Default location
    observation = owm.weather_at_place(location)
    w = observation.get_weather()
    status = w.get_detailed_status()
    temperature = w.get_temperature('celsius')
    wind = w.get_wind()
    sunrise = w.get_sunrise_time('iso')
    sunset = w.get_sunset_time('iso')

    msg = "Current status in {}: {} :thermometer: {}°C (min = {}°C, max = {}°C) :tornado_cloud: {} km/h\n" \
          "Sunrise :sunrise: is at {}, sunset :city_sunset: is at {}. ".format(location, status, temperature['temp'],
            temperature['temp_min'], temperature['temp_max'], wind['speed'], sunrise, sunset)
    return msg


def mention_question(user_name, text_received, channel):
    """bot got mentioned or pm'd, answer the question"""
    check_general_keywords(user_name, text_received, channel)
    if any(word in text_received for word in weather_triggers):
        message = get_weather_message(text_received)
        send_message(message, channel)


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

# Keep checking for incoming mentions or keywords
while True:
    parse(slackbot.rtm_read())
    time.sleep(1)
