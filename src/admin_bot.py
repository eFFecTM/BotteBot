from typing import List

import food_bot
import query

admin_channel = 'admin-bot'
admin_channel_id: str
is_imaginelab = False


def init(channels_info: dict):
    global is_imaginelab, admin_channel_id
    is_imaginelab = True
    for k, v in channels_info.items():
        if v["name"] == admin_channel:
            admin_channel_id = k


def is_triggered_in_admin_channel(channel_id: str) -> bool:
    return channel_id == admin_channel_id


def toggle_imaginelab():
    global is_imaginelab
    if is_imaginelab:
        is_imaginelab = False
        return "iMagineLab is cancelled for this week."
    else:
        is_imaginelab = True
        return "iMagineLab has been rescheduled for this week."


def reset_orders():
    query.remove_food_orders()
    food_bot.current_food_place = "..."
    food_bot.current_food_place_url = "..."
    return "Successfully cleared food_orders table!"


def query_database(query_words: List[str]):
    first_word = query_words[0].lower()
    if first_word == "select":
        return str(query.get_query(" ".join(query_words)))
    elif first_word in ["delete", "insert", "update"]:
        query.set_query(" ".join(query_words))
        return "Query succesfully executed!"
    else:
        return f"This is not a valid query with first word {first_word}!"


def dict_to_str(string: str, d: dict):
    for k, v in d.items():
        if isinstance(v, dict):
            return dict_to_str(string, v)
        else:
            return f"{string} {k} : {v}"
