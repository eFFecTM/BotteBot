import json
import random

import requests

import Globals


def lmgtfy(words_received, triggers):
    """let me google that for you with link shortener"""
    found = False
    triggered_word = None
    for word in triggers:
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
        print("found lmgtfy trigger, given url is: " + url)
        return url
    return None


def insult(words_received, user_ids, translator):
    found = False
    r = None
    for user_id_mention in user_ids:
        if '<@{}>'.format(user_id_mention.lower()) in words_received:
            found = True
            url = "https://insult.mattbas.org/api/insult?who=" \
                  + Globals.web_client.users_info(user=user_id_mention)["user"]["real_name"].split(" ")[0]
            r = requests.get(url)
            break
    if not found:
        r = requests.get("https://insult.mattbas.org/api/insult")
    translated = translator.translate(r.text, dest='nl', src='en')
    return translated.text


def definition(words_received, triggers, translator, oxford):
    triggered_word = None
    for word in triggers:
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


def repeat(words_received, triggers):
    triggered_word = None
    for word in triggers:
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
    temp = random.randint(minimum, maximum)
    return temp


def joke(channel):
    """jokes from the joke api at https://sv443.net/jokeapi"""
    # category = ["Miscellaneous", "Programming"]
    category = "Any"
    blacklist = ""
    # r = requests.get("https://sv443.net/jokeapi/category/"+category[random.randint(0,
    # 1)]+"?blacklistFlags="+blacklist)
    r = requests.get(
        "https://sv443.net/jokeapi/category/" + category + "?blacklistFlags=" + blacklist)
    json_info = r.json()
    if json_info['type'] == 'single':
        if json_info['category'] == 'Dark':
            return [json_info['joke'], "black"]
        else:
            return [json_info['joke'], channel]
    else:
        Globals.delivery = json_info['delivery']
        if json_info['category'] == 'Dark':
            Globals.delivery_channel = "black"
            return [json_info['setup'], "black"]
        else:
            Globals.delivery_channel = channel
            return [json_info['setup'], channel]
