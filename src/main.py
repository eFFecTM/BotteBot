"""This is the main application for the Slackbot called BotteBot."""
import asyncio
import logging
import os
import signal
import sys
from logging.handlers import TimedRotatingFileHandler

import nest_asyncio

import constants
import food_bot
import services


def main():
    # Init logger
    if not os.path.exists('logs'):
        os.makedirs('logs')

    handler = TimedRotatingFileHandler("logs/log", when="midnight", interval=1)
    logging.basicConfig(level=constants.logging_level, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
                        handlers=[handler, logging.StreamHandler()])

    logging.getLogger('apscheduler.scheduler').setLevel(logging.WARNING)
    logger.info('Starting BotteBot application...')

    # Connect to SQLite3 database
    logger.info('Connected to SQLite database!')
    food_bot.update_restaurant_database()


def signal_handler():
    logger.info("Program exiting gracefully")
    sys.exit(0)


if __name__ == '__main__':
    logger = logging.getLogger()
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, signal_handler)
    loop.add_signal_handler(signal.SIGTERM, signal_handler)
    try:
        main()
        nest_asyncio.apply(loop)
        loop.run_until_complete(
            asyncio.gather(services.start_scheduler(), services.start_slack_client(), services.start_web_server()))
    except Exception as e:
        logger.exception(e)
    finally:
        loop.close()
        logging.shutdown()
