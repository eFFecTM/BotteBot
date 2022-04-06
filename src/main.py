"""This is the main application for the Slackbot called BotteBot."""
import asyncio
import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

import constants
import services


def setup():
    # Init logger
    if not os.path.exists(f'{constants.base_dir}/logs'):
        os.makedirs(f'{constants.base_dir}/logs')

    handler = TimedRotatingFileHandler(f'{constants.base_dir}/logs/log', when="midnight", interval=1)
    logging.basicConfig(level=constants.logging_level, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
                        handlers=[handler, logging.StreamHandler()])

    logging.getLogger('apscheduler.scheduler').setLevel(logging.WARNING)
    logger.info('Starting BotteBot application...')

    # Connect to SQLite3 database
    logger.info('Connected to SQLite database!')


async def main():
    await asyncio.gather(services.start_scheduler(), services.start_slack_client(), services.start_web_server())


if __name__ == '__main__':
    logger = logging.getLogger()
    try:
        setup()
        asyncio.run(main())
    except Exception as e:
        logger.error(e)
    finally:
        sys.exit(0)
