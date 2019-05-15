"""Create a bot that responds on requests with 'help' keywords. List all available commands and features."""
import configparser
import logging

# Read config file
config = configparser.ConfigParser()
config.read('init.ini')

# Create global logger
logger = logging.getLogger('helpbot')
formatstring = "%(asctime)s - %(name)s:%(funcName)s:%(lineno)i - %(levelname)s - %(message)s"
logging.basicConfig(format=formatstring, level=logging.DEBUG)


def get_list_of_commands():
    response = "I am only just written by my almighty owner (Thomas J), so excuse me if I do not understand you right now :(\nQuestions? Jan De Laet is our top communication engineer ;)"
    return response

def get_help_with_features():
    pass
