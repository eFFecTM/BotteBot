"""Create a bot that responds on requests with 'help' keywords. List all available commands and features."""
import logging
from datetime import datetime

import git
import pytz

import query
from constants import bugreport_triggers, add_triggers, overview_triggers

logger = logging.getLogger()


def get_list_of_commands():
    response = """ Need help :question: Here is a list of available features and corresponding commands. 
    You can use synonyms of these words as trigger words.\n
    :one: *General stuff (mention me using `@RUDE-i`):*
    • Get the current weather: `weather in <city>`
    • Report a bug: `bug add <text>`
    • Show an overview of bugs: `bug overview`
    • Let Me Google That For You (LMGTFY): `lmgtfy <text>`
    • Get help: call 112 or type `help`
    • Want to know my current age? type `version`
    • Search for a gif: `gif <search terms>`
                    
    :two: *Food-related stuff (mention me using `@RUDE-i`):*
    • View current restaurant and all current orders: `food list`. Note that I'll already automatically show the current restaurant at noon.
    • Manually add a restaurant that is not on Takeaway: `food restaurant add <restaurant-name> <url>`
    • Add rating to a restaurant (number from 0 to 10): `food rating <restaurant> <rating>`
    • Set or change the restaurant where we are ordering food: `food set <restaurant>`
                    
    :three: *For these features, there is no need to mention me, unless you really want spam in the channel:*
    • Insulting people: `insult <name> in <channel>`
    • Define words: `define <word>`
    • Repeat text in a channel: `repeat <text> in <channel>`
    • Repeat:clap:all:clap:words:clap:in:clap:style: `clap <text> in <channel>`
    • Get a list of restaurants that we ordered at before, sorted by rating: `restaurant top <number>`
    • Get a list of restaurants that are able to deliver @ iMagineLab, sorted by rating: `restaurant takeaway top <number>`
    • Let the bot tell a random joke: _Sit back, relax and wait for the joke. If nothing happens, type_ `joke`
    """
    return response


def report_bug(words_received: list, user):
    """Command: 'bug add <report>'. This saves the report to the bug report database, together with the username."""
    for bug_trigger in bugreport_triggers:
        if bug_trigger in words_received:
            for add_trigger in add_triggers:
                if add_trigger in words_received:
                    words_received.remove(add_trigger)
                    words_received.remove(bug_trigger)
                    bug = " ".join(words_received)
                    logger.debug(f"reported bug {bug} by user {user}")
                    query.add_bug_report(bug, user)
                    return f"Reported '{bug}', should I start pointing out your flaws too, {user}? :ladybug:"
    return None


def get_bugs(words_received: list, user):
    """Command: 'bug overview'. This shows a list of bugs in the database.'"""
    for bug_trigger in bugreport_triggers:
        if bug_trigger in words_received:
            for overview_trigger in overview_triggers:
                if overview_trigger in words_received:
                    logger.debug(f"Showing an overview of reported bugs.")
                    bugs = query.show_bug_report()
                    text = ""
                    for bug in bugs:
                        text += f'• {bug[0]} ~ _{bug[1]} on {bug[2]}_\n'

                    return f"Here is a list of all your flaws, {user}!\n{text}"


def get_version():
    """Command: 'version'. Retrieves the latest commit id and date."""
    repo = git.Repo(search_parent_directories=True)
    latest_datetime = datetime.fromtimestamp(repo.head.object.committed_date, pytz.timezone('Europe/Brussels'))
    return f'I\'m running version of {latest_datetime}\nfrom commit: {repo.head.object.hexsha}'
