import configparser
import json
from pathlib import Path

base_dir = Path(__file__).parent.parent

config = configparser.ConfigParser()
config.read(base_dir / 'config/config.ini')

logging_level = config.get('system', 'LOGGING_LEVEL')

notification_channel = str(config.get("scheduler", "NOTIFICATION_CHANNEL"))
where_time = str(config.get("scheduler", "WHERE_TIME"))
what_time = str(config.get("scheduler", "WHAT_TIME"))

ignored_words = json.loads(config.get("triggers", "IGNORED_WORDS"))
weather_triggers = json.loads(config.get("triggers", "WEATHER"))
insult_triggers = json.loads(config.get("triggers", "INSULT"))
lmgtfy_triggers = json.loads(config.get("triggers", "LMGTFY"))
def_triggers = json.loads(config.get("triggers", "DEF"))
food_triggers = json.loads(config.get("triggers", "FOOD"))
repeat_triggers = json.loads(config.get("triggers", "REPEAT"))
image_triggers = json.loads(config.get("triggers", "IMAGE"))
help_triggers = json.loads(config.get("triggers", "HELP"))
joke_triggers = json.loads(config.get("triggers", "JOKE"))
resto_triggers = json.loads(config.get("triggers", "RESTO"))
menu_triggers = json.loads(config.get("triggers", "MENU"))
set_triggers = json.loads(config.get("triggers", "SET"))
overview_triggers = json.loads(config.get("triggers", "OVERVIEW"))
order_triggers = json.loads(config.get("triggers", "ORDER"))
schedule_triggers = json.loads(config.get("triggers", "SCHEDULE"))
add_triggers = json.loads(config.get("triggers", "ADD"))
remove_triggers = json.loads(config.get("triggers", "REMOVE"))
rating_triggers = json.loads(config.get("triggers", 'RATING'))
no_imaginelab_triggers = json.loads(config.get("triggers", "NO_IMAGINELAB"))
bugreport_triggers = json.loads(config.get("triggers", "BUG_REPORT"))
resetpoll_triggers = json.loads(config.get("triggers", "RESET_FOOD_POLL"))

init = configparser.ConfigParser()
init.read(base_dir / 'config/init.ini')

slack_bot_token = str(init.get('slackbot', 'SLACK_BOT_TOKEN'))
open_weather_key = str(init.get('open_weather_map', 'API_KEY'))
oxford_id = str(init.get('oxford', 'ID'))
oxford_key = str(init.get('oxford', 'KEY'))

with open(base_dir / "resources/template_message.json") as a, \
        open(base_dir / "resources/template_text.json") as b, \
        open(base_dir / "resources/template_divider.json") as c, \
        open(base_dir / "resources/template_pollentry.json") as d, \
        open(base_dir / "resources/template_votes.json") as e, \
        open(base_dir / "resources/template_addoption.json") as f, \
        open(base_dir / "resources/template_modal_question.json") as g, \
        open(base_dir / "resources/template_flattext.json") as h, \
        open(base_dir / "resources/template_modal_flattext.json") as i, \
        open(base_dir / "resources/template_modal_dropdown.json") as j, \
        open(base_dir / "resources/template_dropdown_option.json") as k, \
        open(base_dir / "resources/template_modal.json") as l:
    template_message = json.load(a)
    template_text = json.load(b)
    template_divider = json.load(c)
    template_pollentry = json.load(d)
    template_votes = json.load(e)
    template_addoption = json.load(f)
    template_modal_question = json.load(g)
    template_flattext = json.load(h)
    template_modal_flattext = json.load(i)
    template_modal_dropdown = json.load(j)
    template_dropdown_option = json.load(k)
    template_modal = json.load(l)
