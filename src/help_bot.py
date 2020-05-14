"""Create a bot that responds on requests with 'help' keywords. List all available commands and features."""
import logging

import query
from constants import bugreport_triggers

logger = logging.getLogger()


def get_list_of_commands():
    response = """ >Need help :question: Here is a list of available features and corresponding commands. 
    You can use synonyms of these words as trigger words.\n
    General stuff (mention me using `@BotteBot`):
    \u2022 Get the current weather: `weather in <city>`
    \u2022 Get the menu of a restaurant: `menu <restaurant> top <number>`
    \u2022 Image search: `image of <text>` or `animation of <text>`
    \u2022 Report a bug: `bug <text>`
    \u2022 Get help: `help`
                    
    Food-related stuff (mention me using `@BotteBot`):\n
    \u2022 View current restaurant and all current orders: `food list`
    \u2022 Place a food order: `food order <meal>`
    \u2022 Remove a food order: `food order remove <meal>`
    \u2022 View ImagineLab schedule: `food schedule`
    \u2022 Add date to ImagineLab schedule: `food schedule add <date>`
    \u2022 Remove date from ImagineLab schedule: `food schedule remove <date>`
    \u2022 Manually add a restaurant that is not on Takeaway: `food restaurant add <restaurant-name> <url>`
    \u2022 Add rating to a restaurant (number from 0 to 10): `food rating <restaurant> <rating>`
    \u2022 Set or change the restaurant where we are ordering food: `food set <restaurant>`
                    
    For these features, there is no need to mention me, unless you really want spam in the channel:\n
    \u2022 Insulting people: `insult <name> in <channel>`
    \u2022 Let Me Google That For You (LMGTFY): `lmgtfy <text>`
    \u2022 Define words: `define <word>`
    \u2022 Repeat text in a channel: `repeat <text> in <channel>`
    \u2022 Get a list of restaurants that are able to deliver @ iMagineLab, sorted by rating: `restaurant top <number>`
    \u2022 Let the bot tell a random joke: _Sit back, relax and wait for the joke. If nothing happens, type_ `joke`
    """
    return response


def report_bug(words_received, user):
    """Command: 'bug <report>'. This saves the report to the bug report database, together with the username."""
    for trigger in bugreport_triggers:
        if trigger in words_received:
            after_trigger = " ".join(words_received[words_received.index(trigger) + 1:])
            logger.debug("reported bug {} by user {}".format(after_trigger, user))
            query.add_bug_report(after_trigger, user)
            return "reported '{}', should I start pointing out your flaws too, {}?".format(after_trigger, user)
    return None
