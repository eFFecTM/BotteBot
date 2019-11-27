import ast
import json
from datetime import datetime, timedelta

from slack.web.slack_response import SlackResponse

import FoodBot
import Globals
import HelpBot
import ImageBot
import RandomBot
import WeatherBot


def send_message(channel, text, attachments, blocks):
    if channel is None:
        Globals.logger.error('Channel is not initialized!')
        return
    if text is None and blocks is None:
        Globals.logger.error('Cannot send as both text and blocks are not initialized!')
        return
    if text is not None:  # text has priority over blocks
        blocks = None
    data = ast.literal_eval(SlackResponse.__str__(
        Globals.web_client.chat_postMessage(as_user="true", channel=channel, text=text,
                                            attachments=attachments, blocks=blocks)))
    Globals.last_message_ts = data["ts"]
    Globals.last_channel_id = data["channel"]
    Globals.logger.debug('Message sent to {}'.format(channel))


def update_message(ts, channel, text, blocks):
    if channel is None:
        Globals.logger.error('Channel is not initialized!')
        return
    if ts is None:
        Globals.logger.error('Timestamp (of last message) is not initialized!')
        return
    if text is None and blocks is None:
        Globals.logger.error('Cannot update as both text and blocks are not initialized!')
        return
    if text is not None:  # text has priority over blocks
        blocks = None
    Globals.web_client.chat_update(as_user="true", ts=ts, channel=channel, text=text, blocks=blocks)


def filter_ignore_words(words_received, ignored_words):
    mentioned = False
    relevant_words = []
    for word in words_received:
        if '@{}'.format(Globals.bot_id.lower()) in word:
            mentioned = True
        elif word not in ignored_words:
            relevant_words.append(word)
    return relevant_words, mentioned


def check_channel(text_words, channel):
    """Check whether a channel got mentioned"""
    for channel_id in Globals.public_channel_ids:
        for word in text_words:
            if '#{}'.format(channel_id.lower()) in word:
                Globals.logger.critical(channel_id)
                text_words.remove(word)
                channel = channel_id
                break
    return channel, text_words


def check_random_keywords(user_name, words_received, channel, message):
    """To check for words used in normal conversation, adding insults and gifs/images"""
    if not message and any(word in words_received for word in Globals.insult_triggers):
        message = RandomBot.insult(words_received, Globals.user_ids, Globals.translator)
        Globals.logger.debug('{} insulted someone in {}'.format(user_name, channel))
    if not message:
        message = RandomBot.definition(words_received, Globals.def_triggers, Globals.translator, Globals.oxford)
        if message:
            Globals.logger.debug('{} asked for a definition a word in {}'.format(user_name, channel))
    if not message:
        message = RandomBot.repeat(words_received, Globals.repeat_triggers)
        if message:
            Globals.logger.debug('{} repeated a word in {}'.format(user_name, channel))
    if not message:
        if Globals.counter_joke >= Globals.counter_threshold:
            if (Globals.previous_joke + timedelta(hours=2)) < datetime.now():
                [message, channel] = RandomBot.joke(channel)
                Globals.previous_joke = datetime.now()
            counter_threshold = RandomBot.generate_threshold(8, 20)
            Globals.counter_joke = 0
            Globals.logger.debug('Joke joked. Joking again in {} messages'.format(counter_threshold))
        else:
            Globals.counter_joke += 1
    return message, channel


def check_general_keywords(user_name, words_received, channel, message):
    """Check for serious shit. Predefined commands etc."""
    attachments = blocks = None
    if not message and any(word in words_received for word in Globals.help_triggers):
        message = HelpBot.get_list_of_commands()
        Globals.logger.debug('{} asked the HelpBot for info in channel {}'.format(user_name, channel))
    if not message:
        for food_trigger in Globals.food_triggers:
            if food_trigger in words_received:
                Globals.logger.debug('{} asked the FoodBot a request in channel {}'.format(user_name, channel))
                message, blocks = FoodBot.process_call(user_name, words_received, Globals.set_triggers,
                                                       Globals.overview_triggers, Globals.order_triggers,
                                                       Globals.schedule_triggers, Globals.add_triggers,
                                                       Globals.remove_triggers, Globals.resto_triggers,
                                                       Globals.rating_triggers, food_trigger)
    if not message and any(word in words_received for word in Globals.menu_triggers):
        Globals.logger.debug('{} asked the Foodbot for menu in channel {}'.format(user_name, channel))
        message = FoodBot.get_menu(words_received)
    if not message and any(word in words_received for word in Globals.resto_triggers):
        Globals.logger.debug('{} asked the Foodbot for restaurants in channel {}'.format(user_name, channel))
        message, restaurants = FoodBot.get_restaurants(words_received)
    if not message and any((word in words_received for word in Globals.image_triggers)):
        Globals.logger.debug('{} asked the ImageBot a request in channel {}'.format(user_name, channel))
        message, attachments = ImageBot.find_image(words_received, Globals.image_triggers)
    if not message and any((word in words_received for word in Globals.joke_triggers)):
        [message, channel] = RandomBot.joke(channel)
    if not message and all(word in Globals.no_imaginelab_triggers for word in words_received):
        Globals.logger.debug(
            '{} asked the Bottebot to toggle ImagineLab for this week in channel {}'.format(user_name, channel))
        message = toggle_imaginelab()
    return message, attachments, blocks


def mention_question(user_name, words_received, channel, message):
    """bot got mentioned or pm'd, answer the question"""
    Globals.logger.debug('BotteBot got mentioned in {}'.format(channel))
    attachments = blocks = None
    if not message:
        message, attachments, blocks = check_general_keywords(user_name, words_received, channel, message)
    if not message and any(word in words_received for word in Globals.weather_triggers):
        message = WeatherBot.get_weather_message(Globals.API_KEY)
    if not message:
        message = RandomBot.lmgtfy(words_received, Globals.lmgtfy_triggers)
    if not message:
        message = HelpBot.report_bug(words_received, Globals.bugreport_triggers, user_name)
    return message, attachments, blocks


def print_where_food_notification():
    if Globals.is_imaginelab:
        send_message(Globals.notification_channel, "<!channel> Where are we going to order today?", None, None)


def print_what_food_notification():
    if Globals.is_imaginelab:
        send_message(Globals.notification_channel, "<!channel> What do you all want to order?", None, None)
        blocks = FoodBot.get_order_overview(False)
        blocks = json.dumps(blocks["blocks"])
        send_message(Globals.notification_channel, None, None, blocks)
        Globals.web_client.pins_add(channel=Globals.last_channel_id, timestamp=Globals.last_message_ts)
    Globals.is_imaginelab = True  # resetting for next time


def toggle_imaginelab():
    if Globals.is_imaginelab:
        send_message(Globals.notification_channel, "<!channel> iMagineLab is cancelled for this week!", None, None)
        Globals.is_imaginelab = False
        return "iMagineLab is cancelled for this week."
    else:
        send_message(Globals.notification_channel, "<!channel> iMagineLab has been rescheduled for this week!", None, None)
        Globals.is_imaginelab = True
        return "iMagineLab has been rescheduled for this week."
