import requests
import json
import random


def lmgtfy(words_received, triggers):
    """let me google that for you with link shortener"""
    found = False
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


def insult(words_received, client, user_ids, translator):
    found = False
    for user_id_mention in user_ids:
        if '@{}'.format(user_id_mention) in words_received:
            found = True
            url = "https://insult.mattbas.org/api/insult?who=" \
                  + client.users_info(user=user_id_mention)["user"]["real_name"].split(" ")[0]
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
                answer = str(json_info['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['crossReferenceMarkers'][0])
            else:
                raise ValueError
            subject = str(json_info['results'][0]['id'])
            translated = translator.translate(subject + " is " + answer, src='en', dest='nl')
            return translated.text
        except ValueError as e:
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


def generate_threshold(min, max):
    temp = random.randint(min, max)
    print(temp)
    return temp

"""jokes from the joke api at https://sv443.net/jokeapi"""
def joke():
    category = ["Miscellaneous", "Programming"]
    blacklist = ""
    r = requests.get("https://sv443.net/jokeapi/category/"+category[random.randint(0, 1)]+"?blacklistFlags="+blacklist)
    json_info = r.json()
    if json_info['type'] == 'single':
        return json_info['joke'], None
    else:
        return json_info['setup'], json_info['delivery']
