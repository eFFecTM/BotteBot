"""This is the main application for the Slackbot called BotteBot."""
import asyncio
import logging
import os
import signal
import sys
from logging.handlers import TimedRotatingFileHandler

import nest_asyncio

import constants
import services


def main():
    # Init logger
    if not os.path.exists(f'{constants.base_dir}/logs'):
        os.makedirs(f'{constants.base_dir}/logs')

    handler = TimedRotatingFileHandler("logs/log", when="midnight", interval=1)
    logging.basicConfig(level=constants.logging_level, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
                        handlers=[handler, logging.StreamHandler()])

    logging.getLogger('apscheduler.scheduler').setLevel(logging.WARNING)
    logger.info('Starting BotteBot application...')

    # Connect to SQLite3 database
    logger.info('Connected to SQLite database!')


def signal_handler():
    loop.stop()
    logger.info("Program exiting gracefully")
    logging.shutdown()


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
    finally:
        sys.exit(0)
