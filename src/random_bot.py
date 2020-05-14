import json
import logging
import random
from datetime import timedelta, datetime

import requests
from googletrans import Translator
from oxforddictionaries.words import OxfordDictionaries

from constants import oxford_id, oxford_key, lmgtfy_triggers, def_triggers, repeat_triggers

logger = logging.getLogger()
delivery = delivery_channel = oxford = counter_threshold = counter_joke = previous_joke = translator = None


def init():
    global translator, oxford, counter_threshold, counter_joke, previous_joke
    translator = Translator()
    oxford = OxfordDictionaries(app_id=oxford_id, app_key=oxford_key)
    counter_threshold = generate_threshold(8, 20)
    counter_joke = 0
    previous_joke = datetime.now() - timedelta(hours=2)  # joke limiter


def lmgtfy(words_received):
    """let me google that for you with link shortener"""
    found = False
    triggered_word = None
    for word in lmgtfy_triggers:
        if word.lower() in words_received:
            found = True
            triggered_word = word
            break
    if found:
        for word in words_received:
            if word.startswith("<"):  # people and channels
                words_received.remove(word)
        next_words = words_received[words_received.index(triggered_word) + 1:]
        url = "+"
        url = url.join(next_words)
        url = "http://lmgtfy.com/?q=" + url
        logger.debug("found lmgtfy trigger, given url is: " + url)
        return url
    return None


def insult(first_name):
    if first_name:
        r = requests.get("https://insult.mattbas.org/api/insult?who=" + first_name)
    else:
        r = requests.get("https://insult.mattbas.org/api/insult")
    translated = translator.translate(r.text, dest='nl', src='en')
    return translated.text


def definition(words_received):
    triggered_word = None
    for word in def_triggers:
        if word.lower() in words_received:
            triggered_word = word
            break
    if triggered_word:
        for word in words_received:
            if word.startswith("<"):  # people and channels
                words_received.remove(word)
        next_word = words_received[words_received.index(triggered_word) + 1]
        translated = translator.translate(next_word, dest='en')
        info = oxford.get_info_about_word(translated.text)
        try:
            json_info = json.loads(info.text)
            if 'definitions' in json_info['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]:
                answer = str(json_info['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['definitions'][0])
            elif 'crossReferenceMarkers' in json_info['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]:
                answer = str(
                    json_info['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['crossReferenceMarkers'][0])
            else:
                raise ValueError
            subject = str(json_info['results'][0]['id'])
            translated = translator.translate(subject + " is " + answer, src='en', dest='nl')
            return translated.text
        except ValueError:
            r = requests.get("https://insult.mattbas.org/api/adjective")
            return "You " + r.text + " person, that's no word!"
    return None


def repeat(words_received):
    triggered_word = None
    for word in repeat_triggers:
        if word.lower() in words_received:
            triggered_word = word
            break
    if triggered_word:
        for word in words_received:
            if word.startswith("<#"):
                words_received.remove(word)
        text_received = " ".join(words_received)
        text_received = text_received.replace('@channel', '<!channel>')
        return text_received.replace(triggered_word, '', 1)
    return None


def generate_threshold(minimum, maximum):
    return random.randint(minimum, maximum)


def joke(channel, is_triggered):
    """jokes from the joke api at https://sv443.net/jokeapi"""
    global counter_threshold, counter_joke, previous_joke

    if is_triggered:
        return joke_helper(channel)

    if counter_joke < counter_threshold:
        counter_joke += 1
        return None, channel

    message = channel = None
    if (previous_joke + timedelta(hours=2)) < datetime.now():
        message, channel = joke_helper(channel)
        previous_joke = datetime.now()

    counter_threshold = generate_threshold(8, 20)
    counter_joke = 0
    return message, channel


def joke_helper(channel):
    global delivery, delivery_channel
    # category = ["Miscellaneous", "Programming"]
    category = "Any"
    blacklist = ""
    # r = requests.get("https://sv443.net/jokeapi/category/"+category[random.randint(0,
    # 1)]+"?blacklistFlags="+blacklist)
    r = requests.get("https://sv443.net/jokeapi/category/" + category + "?blacklistFlags=" + blacklist)
    json_info = r.json()
    logger.debug('Joke joked. Joking again in {} messages'.format(counter_threshold))
    if json_info['type'] == 'single':
        if json_info['category'] == 'Dark':
            return json_info['joke'], "black"
        else:
            return json_info['joke'], channel
    else:
        delivery = json_info['delivery']
        if json_info['category'] == 'Dark':
            delivery_channel = "black"
            return json_info['setup'], "black"
        else:
            delivery_channel = channel
            return json_info['setup'], channel


def joke_second():
    """returning second part of the joke when exists"""
    global delivery, delivery_channel
    message = channel = None
    if delivery and delivery_channel:
        message = delivery
        channel = delivery_channel
    delivery = delivery_channel = None
    return message, channel
