"""Create an image bot to post or process images. See https://pythonspot.com/category/nltk/"""
import configparser
import logging
from google_images_download import google_images_download

# Read config file
config = configparser.ConfigParser()
config.read('init.ini')

# Create global logger
logger = logging.getLogger('imagebot')
formatstring = "%(asctime)s - %(name)s:%(funcName)s:%(lineno)i - %(levelname)s - %(message)s"
logging.basicConfig(format=formatstring, level=logging.DEBUG)


def find_image(text, channel, triggers):
    # Get search words in received text
    search_words = []
    words = text.split(" ")[1:]
    for word in words:
        if word not in triggers:
            search_words.append(word)
    search_string = " ".join(search_words)
    logger.debug('Searching Google Images for search: {}'.format(search_string))
    image_title, image_url = get_image_url(search_string)

    # Add attachments to response message
    attachments = [{"title": image_title, "image_url": image_url}]
    message = "Here is an image of it!"
    return message, attachments


def get_image_url(search_string):
    response = google_images_download.googleimagesdownload()

    # keywords is the search query
    # format is the image file format
    # limit is the number of images to be downloaded
    # print urs is to print the image file url
    # size is the image size which can
    # be specified manually ("large, medium, icon")
    # aspect ratio denotes the height width ratio
    # of images to download. ("tall, square, wide, panoramic")
    arguments = {"keywords": search_string,
                 "format": "jpg",
                 "limit": 1,
                 "print_urls": True,
                 "no_download": True,
                 "size": "medium",
                 "aspect_ratio": "panoramic"
                 }
    try:
        x = response.download(arguments)
        url = next(iter(x.values()))[0]
        logger.debug('URL of first found image: {}'.format(url))
        return search_string, url

    except Exception as e:
        logger.exception(e)
