"""Create an image bot to post or process images. See https://pythonspot.com/category/nltk/"""
import logging
import urllib
import json

from constants import giphy_key

logger = logging.getLogger()


def find_image(words_received, image_triggers):
    # Get search words in received text
    search_words = []
    logger.info("do we actually get here?")
    animation = False
    for word in words_received:
        if word in ['animation', 'animatie', 'gif']:
            animation = True
        if word not in image_triggers:
            search_words.append(word)
    if not animation:
        return "Pictures are not supported at the moment", None
    search_string = " ".join(search_words)
    logger.debug('Searching Giphy for search: {}'.format(search_string))
    # image_title, image_url = get_image_url(search_string, animation=animation)
    url = "http://api.giphy.com/v1/gifs/search"
    params = urllib.parse.urlencode({
        "q": search_string,
        "api_key": giphy_key,
        "limit": "1"
    })
    with urllib.request.urlopen("?".join([url, params])) as response:
        data = json.loads(response.read())

    # Add attachments to response message
    attachments = [{"title": data['data'][0]['title'], "image_url": data['data'][0]['images']['original']['url']}]
    message = "Here is an image of it!"
    return message, attachments

