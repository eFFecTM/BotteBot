"""This is the main application for the Slackbot called BotteBot."""
import asyncio
import configparser
import json
import logging
import os
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler

import nest_asyncio
from googletrans import Translator
from oxforddictionaries.words import OxfordDictionaries

import FoodBot
import Globals
import RandomBot
import Services
from data.SqlQuery import SqlQuery


def main():
    # init globals
    Globals.init()

    # Create global logger
    if not os.path.exists('logs'):
        os.makedirs('logs')
    Globals.logger = logging.getLogger()
    handler = TimedRotatingFileHandler("logs/log", when="midnight", interval=1)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s',
                        handlers=[handler, logging.StreamHandler()])
    logging.getLogger('apscheduler.scheduler').setLevel(logging.WARNING)
    Globals.logger.info('Starting BotteBot application...')

    # Read init file
    init = configparser.ConfigParser()
    init.read('init.ini')
    Globals.SLACK_BOT_TOKEN = str(init.get('slackbot', 'SLACK_BOT_TOKEN'))
    Globals.API_KEY = str(init.get('open_weather_map', 'API_KEY'))
    OXFORD_ID = str(init.get('oxford', 'ID'))
    OXFORD_KEY = str(init.get('oxford', 'KEY'))
    Globals.oxford = OxfordDictionaries(app_id=OXFORD_ID, app_key=OXFORD_KEY)

    # Stopping scheduler when bottebot is shutting down
    Globals.stop = False

    # Is there an imaginelab this week?
    Globals.is_imaginelab = True

    # Define trigger words
    config = configparser.ConfigParser()
    config.read('config.ini')

    Globals.weather_triggers = json.loads(config.get("triggers", "WEATHER"))
    Globals.insult_triggers = json.loads(config.get("triggers", "INSULT"))
    Globals.lmgtfy_triggers = json.loads(config.get("triggers", "LMGTFY"))
    Globals.def_triggers = json.loads(config.get("triggers", "DEF"))
    Globals.food_triggers = json.loads(config.get("triggers", "FOOD"))
    Globals.repeat_triggers = json.loads(config.get("triggers", "REPEAT"))
    Globals.image_triggers = json.loads(config.get("triggers", "IMAGE"))
    Globals.help_triggers = json.loads(config.get("triggers", "HELP"))
    Globals.joke_triggers = json.loads(config.get("triggers", "JOKE"))
    Globals.resto_triggers = json.loads(config.get("triggers", "RESTO"))
    Globals.menu_triggers = json.loads(config.get("triggers", "MENU"))
    Globals.set_triggers = json.loads(config.get("triggers", "SET"))
    Globals.overview_triggers = json.loads(config.get("triggers", "OVERVIEW"))
    Globals.order_triggers = json.loads(config.get("triggers", "ORDER"))
    Globals.schedule_triggers = json.loads(config.get("triggers", "SCHEDULE"))
    Globals.add_triggers = json.loads(config.get("triggers", "ADD"))
    Globals.remove_triggers = json.loads(config.get("triggers", "REMOVE"))
    Globals.rating_triggers = json.loads(config.get("triggers", 'RATING'))
    Globals.no_imaginelab_triggers = json.loads(config.get("triggers", "NO_IMAGINELAB"))
    Globals.bugreport_triggers = json.loads(config.get("triggers", "BUG_REPORT"))

    # Define ignored words
    Globals.ignored_words = json.loads(config.get("triggers", "IGNORED_WORDS"))

    # For Scheduler
    Globals.notification_channel = str(config.get("scheduler", "NOTIFICATION_CHANNEL"))
    Globals.where_time = str(config.get("scheduler", "WHERE_TIME"))
    Globals.what_time = str(config.get("scheduler", "WHAT_TIME"))

    # Init message and translator
    Globals.counter_threshold = RandomBot.generate_threshold(8, 20)
    Globals.translator = Translator()

    # joke limiter
    Globals.previous_joke = datetime.now() - timedelta(hours=2)

    # Connect to SQLite3 database
    Globals.database = SqlQuery('data/imaginelab.db')
    Globals.logger.info('Connected to SQLite database!')
    # s.sql_delete('DELETE FROM restaurant_database')
    FoodBot.update_restaurant_database()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        main()
        nest_asyncio.apply(loop)
        loop.run_until_complete(
            asyncio.gather(Services.start_scheduler(), Services.start_slack_client(), Services.start_web_server()))
    except Exception as e:
        Globals.logger.exception(e)
    finally:
        loop.close()
        logging.shutdown()
