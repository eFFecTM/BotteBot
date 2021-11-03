import copy
import json
import logging
import re
from datetime import datetime

import requests

import constants
import query

snappy_responses = ["just like the dignity of your {} mother. Mama Mia!",
                    "pick again you {} idiot!",
                    "better luck next time {} person!",
                    u"\U0001F595",
                    "huh? Fine! I'll go build my own restaurant, with blackjack and hookers. In fact, forget about "
                    "the restaurant and blackjack."]

logger = logging.getLogger()
current_food_place = "..."
current_food_place_url = "..."
takeaway_restaurants = []


def process(user, words_received, food_trigger):
    output = blocks = None
    if not output:
        for set_trigger in constants.set_triggers:
            if set_trigger in words_received:
                output = set_restaurant(" ".join(words_received[words_received.index(set_trigger) + 1:]))
                break
    if not output and any(overview_trigger in words_received for overview_trigger in constants.overview_triggers):
        blocks = get_order_overview(False)
    if not output and any(rating_trigger in words_received for rating_trigger in constants.rating_triggers):
        if not output:
            for rating_trigger in constants.rating_triggers:
                if rating_trigger in words_received:
                    output = add_restaurant_rating(words_received, rating_trigger, food_trigger)
                    break
    if not output and any(resto_trigger in words_received for resto_trigger in constants.resto_triggers):
        if not output:
            for add_trigger in constants.add_triggers:
                if add_trigger in words_received:
                    output = add_restaurant(words_received, add_trigger)
                    break
    if not output and any(resetpoll_trigger in words_received for resetpoll_trigger in constants.resetpoll_triggers):
        output = reset_orders()
    return output, blocks


def add_text(blocks, value):
    element = copy.deepcopy(constants.template_text)
    element["text"]["text"] = value
    blocks["blocks"].append(element)


def add_pollentry(blocks, value, value_button):
    element = copy.deepcopy(constants.template_pollentry)
    element["text"]["text"] = value
    element["accessory"]["text"]["text"] = value_button
    blocks["blocks"].append(element)


def add_option(blocks):
    element = copy.deepcopy(constants.template_addoption)
    blocks["blocks"].append(element)


def add_votes(blocks, value):
    element = copy.deepcopy(constants.template_votes)
    element["elements"][0]["text"] = value
    blocks["blocks"].append(element)


def add_divider(blocks):
    element = copy.deepcopy(constants.template_divider)
    blocks["blocks"].append(element)


def add_modal_question(blocks, value):
    element = copy.deepcopy(constants.template_modal_question)
    element["label"]["text"] = value
    blocks["blocks"].append(element)


def add_flattext(blocks):
    element = copy.deepcopy(constants.template_flattext)
    blocks["blocks"].append(element)


def create_modal_dropdown(value):
    element = copy.deepcopy(constants.template_modal_dropdown)
    element["label"]["text"] = value
    return element


def add_dropdown_option(dropdown, initial, value):
    element = copy.deepcopy(constants.template_dropdown_option)
    element["text"]["text"] = value
    element["value"] = value
    if initial:
        dropdown["element"]["initial_options"].append(element)
    else:
        dropdown["element"]["options"].append(element)


def get_order_overview(want_text):
    """
    Command: 'food overview'
    Markdown guide for Slack API: https://api.slack.com/reference/surfaces/formatting
    """
    orders = query.get_food_orders()
    if want_text:
        text = ""
        text += f"We're getting food from <{current_food_place_url}|{current_food_place}>!\n\n"
        prev_item = None
        count = 0
        names = []
        for [name, item] in orders:
            if prev_item is not None and prev_item != item:
                text += f'• *{str(count)} x {prev_item}*: {", ".join(names)}\n'
                count = 0
                names = []
            count = count + 1
            prev_item = item
            names.append(name)
        if len(orders) != 0:
            text += f'• *{str(count)} x {prev_item}*: {", ".join(names)}\n'
            text += f"\n\n_*Total votes: {len(orders)} | Total eaters: {len(set(j[0] for j in orders))}*_"
        return text
    else:
        blocks = {"blocks": []}
        add_text(blocks, f"We're getting food from *<{current_food_place_url}|{current_food_place}>*!\n\n")
        if len(orders) != 0:
            add_text(blocks, f"*Total votes: {len(orders)} | Total eaters: {len(set(j[0] for j in orders))}*")
        add_option(blocks)
        add_flattext(blocks)
        return blocks


def order_food(user, food):
    """Command: 'food order <food>'"""
    if food == "":
        output = "No food input was provided!"
        success = False
    else:
        ordered = query.get_food_order(user, food)
        if len(ordered) == 0:
            query.add_food_order(user, food, current_food_place, datetime.now())
            adjective = requests.get("https://insult.mattbas.org/api/adjective").text
            output = "Order placed: {} for {} {}".format(food, adjective, user)
            success = True
        else:
            output = "Order: {} already exists for user {}!".format(food, user)
            success = False
    return output, success


def remove_order_food(user, food):
    """Command: 'food order remove <food>'"""
    ordered = query.get_food_order(user, food)
    if len(ordered) != 0:
        query.remove_food_order(user, food)
    else:
        noun = requests.get("https://insult.mattbas.org/api/insult").text.split()[-1]
        return "There's no food from {} matching {}, buy some glasses, you blind {}".format(user, food, noun)
    return "Fine. No food for {}".format(user)


def reset_orders():
    global current_food_place
    global current_food_place_url
    query.remove_food_orders()
    current_food_place = "..."
    current_food_place_url = "..."
    return "Successfully cleared food_orders table!"


def get_restaurants_from_takeaway():
    global takeaway_restaurants
    with open(f'{constants.base_dir}/resources/takeaway_restaurants.json') as a:
        takeaway_restaurants_json = json.load(a)

    for takeaway_restaurant in takeaway_restaurants_json["restaurants"]:
        temp_name = takeaway_restaurant["brand"]["name"]
        temp_url = "https://www.takeaway.com/be/menu/" + takeaway_restaurant["primarySlug"]
        default_rating = 6
        takeaway_restaurants.append([temp_name, default_rating, temp_url])
    return takeaway_restaurants


def get_restaurants(words_received=None):
    if words_received and 'takeaway' in words_received:
        restaurants = takeaway_restaurants
    else:
        restaurants = query.get_restaurants()
    amount_restaurants = len(restaurants)

    if words_received and 'top' in words_received:
        next_word = words_received[words_received.index('top') + 1]
        try:
            top_number = int(next_word)
            if top_number > amount_restaurants:
                top_number = amount_restaurants
            elif top_number < 1:
                top_number = 1
        except ValueError:
            top_number = 10
    else:
        top_number = 10

    return_message = ""
    if 0 != amount_restaurants:
        for i in range(0, amount_restaurants if amount_restaurants < top_number else top_number):
            return_message = "{}{}: {} - {}/10 - {}\n".format(return_message, i + 1,
                                                              restaurants[i][0], restaurants[i][1], restaurants[i][2])
    else:
        return_message = "No restaurants available!"
    return return_message, restaurants


def set_restaurant(restaurant):
    """set restaurant: food set <restaurantname>"""
    global current_food_place
    global current_food_place_url
    restaurants = query.get_restaurants()
    # if len(restaurants) == 0:
    #     restaurants = update_restaurant_database()  # generate restaurants
    r = requests.get("https://insult.mattbas.org/api/insult").text.split()
    adjective = r[3]
    noun = r[-1]
    for resto in restaurants:
        logger.debug('{} is {}? '.format(restaurant, resto[0].lower()))
        if restaurant == resto[0].lower():
            current_food_place = f"{resto[0].title()}"
            current_food_place_url = resto[2]
            return f"Restaurant set to {current_food_place}. I heard they serve {adjective} {noun}"
    return "Restaurant '{}' not in our database. " \
           "Add it NOW with the command 'food restaurant add < _restaurantname_ > < _url_ >', you {} {}!" \
        .format(restaurant, adjective, noun)


def add_restaurant(words_received, trigger):
    """Command: 'food restaurant add <restaurant-name> <url>' """
    resto_name = words_received[words_received.index(trigger) + 1:-1]
    resto_url = words_received[-1]
    if ("." in resto_url) and len(resto_name) != 0:
        query.add_restaurant(" ".join(resto_name).replace(",", ""), 6, resto_url)
        return "{} added to restaurants.".format(" ".join(resto_name).replace(",", ""))
    else:
        return "The right format is <restaurant name> <url> but I didn't expect you could use it anyway. {} ~ {}" \
            .format(resto_name, resto_url)


def add_restaurant_rating(words_received, rating_trigger, food_trigger):
    """ Command: food rating <restaurant> <rating>"""
    words_received.remove(rating_trigger)
    words_received.remove(food_trigger)

    rating = int(re.search(r'\d+', " ".join(words_received)).group())
    words_received.remove(str(rating))
    restaurant_name = " ".join(words_received).replace(",", "")

    # Get old rating
    old_rating = query.get_restaurant_rating(restaurant_name)

    # Update rating with mean of old and new rating
    if len(old_rating) != 0:
        mean = (old_rating[0][0] + rating) / 2
        query.set_restaurant_rating(restaurant_name, mean)
        msg = "Restaurant {}: mean rating changed to {}".format(restaurant_name, mean)
    else:
        msg = "you soab, that's a restaurant I do not know."
    logger.debug("Restaurant {} rated with a score of {}".format(restaurant_name, rating))
    return msg
