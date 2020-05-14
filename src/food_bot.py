import copy
import logging
import random
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

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


def process(user, words_received):
    output = blocks = None
    if not output:
        for set_trigger in constants.set_triggers:
            if set_trigger in words_received:
                output = set_restaurant(" ".join(words_received[words_received.index(set_trigger) + 1:]))
                break
    if not output and any(overview_trigger in words_received for overview_trigger in constants.overview_triggers):
        blocks = get_order_overview(False)
    if not output and any(order_trigger in words_received for order_trigger in constants.order_triggers):
        if not output:
            for remove_trigger in constants.remove_triggers:
                if remove_trigger in words_received:
                    output = remove_order_food(user,
                                               " ".join(words_received[words_received.index(remove_trigger) + 1:]))
                    break
        if not output:
            for order_trigger in constants.order_triggers:
                if order_trigger in words_received:
                    output, success = order_food(user,
                                                 " ".join(words_received[words_received.index(order_trigger) + 1:]))
                    break
    if not output and any(rating_trigger in words_received for rating_trigger in constants.rating_triggers):
        if not output:
            for rating_trigger in constants.rating_triggers:
                if rating_trigger in words_received:
                    output = add_restaurant_rating(words_received, rating_trigger, None)
                    break
    if not output and any(resto_trigger in words_received for resto_trigger in constants.resto_triggers):
        if not output:
            for add_trigger in constants.add_triggers:
                if add_trigger in words_received:
                    output = add_restaurant(words_received, add_trigger)
                    break
    if not output and any(resetpoll_trigger in words_received for resetpoll_trigger in constants.resetpoll_triggers):
        output = remove_orders()
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
    """Command: 'food overview'"""
    orders = query.get_food_orders()
    if want_text:
        text = ""
        text += "We're getting food from " + current_food_place + "\n"
        prev_item = None
        count = 0
        names = ""
        for [name, item] in orders:
            if prev_item is not None and prev_item != item:
                text += str(count) + ": " + names + "   |   " + prev_item + "\n"
                count = 0
                names = ""
            count = count + 1
            prev_item = item
            names = names + " " + name
        if len(orders) != 0:
            text += str(count) + ": " + names + "   |   " + prev_item + "\n"
            text += "Total Votes: " + str(len(orders)) + "   |   Total Eaters: " + str(len(set(j[0] for j in orders)))
        return text
    else:
        blocks = {"blocks": []}
        add_text(blocks, "We're getting food from " + current_food_place)
        if len(orders) != 0:
            add_text(blocks, "Total Votes: " + str(len(orders)) +
                     "   |   Total Eaters: " + str(len(set(j[0] for j in orders))))
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


def remove_orders():
    query.remove_food_orders()
    return "Successfully cleared food_orders table!"


def get_menu(words_received):
    """Command: 'menu <restaurant name> top <number>'"""
    return_message, restaurants = get_restaurants()
    found = []
    message = ""
    if len(restaurants) == 0:
        get_restaurants('top 1')  # generate restaurants
    for resto in restaurants:
        if all(word in resto[0].lower().split(" ") for word in words_received[1:]):
            found = resto
            message = "Restaurant: *{}*\n\n".format(resto[0])
            break
    if found:
        response = requests.get(found[2])

        soup = BeautifulSoup(response.content, 'html.parser')
        location = soup.text.find('MenucardProducts')
        text = soup.text[location:]

        if 'top' in words_received:
            next_word = words_received[words_received.index('top') + 1]
            try:
                top_number = int(next_word)
                if top_number > 50:
                    top_number = 50
                elif top_number < 1:
                    top_number = 1
            except ValueError:
                top_number = 10
        else:
            top_number = 10

        location = text.find('name')
        menu = [[], []]
        while location != -1:
            text = text[location + len('"name": "') - 1:]
            location = text.find('"')
            if "{" in text[:location]:
                break
            menu[0].append(text[:location])
            location = text.find('price')
            text = text[location + len('"price": ') - 1:]
            location = text.find(",")
            menu[1].append(text[:location])
            location = text.find('name')

        rand = random.randint(0, top_number * 3)
        location_number = 0
        if top_number > len(menu[0]):
            top_number = len(menu[0])
        for i in range(0, top_number):
            location_number += 1
            if rand == i:
                adjective = requests.get("https://insult.mattbas.org/api/adjective").text
                message = "{}{}: Your {} mother for €0\n".format(message, location_number, adjective)
                location_number += 1
            message = "{}{}: {} for €{}\n".format(message, location_number, menu[0][i], menu[1][i])
    else:
        rand = random.randint(0, len(snappy_responses) - 1)
        r = requests.get("https://insult.mattbas.org/api/adjective")
        return "The restaurant is not found, {}".format(snappy_responses[rand].replace("{}", r.text))
    return message


def get_restaurants_from_takeaway():
    response = requests.get('https://www.takeaway.com/be/eten-bestellen-antwerpen-2020')

    soup = BeautifulSoup(response.content, 'html.parser')
    find = soup.find_all('script')
    text = find[9].text
    location = text.find('name')
    restaurants = []

    while location != -1:
        text = text[location + len('"name":"') - 1:]
        location = text.find('"')
        temp_name = text[:location].replace("\'", '')
        location = text.find('url')
        text = text[location + len('"url":"') - 1:]
        location = text.find('"')
        temp_url = ("https://www.takeaway.com" + text[:location]).replace("\\", '')
        restaurants.append([temp_name, 6, temp_url])
        location = text.find('name')
    return restaurants


def update_restaurant_database():
    restaurants = get_restaurants_from_takeaway()
    for resto in restaurants:
        query.add_restaurant(resto[0], 6, resto[2])
    logger.debug('Updated restaurant database')
    return restaurants


def get_restaurants(words_received=None):
    restaurants = query.get_restaurants()

    if words_received and 'top' in words_received:
        next_word = words_received[words_received.index('top') + 1]
        try:
            top_number = int(next_word)
            if top_number > len(restaurants):
                top_number = len(restaurants)
            elif top_number < 1:
                top_number = 1
        except ValueError:
            top_number = 10
    else:
        top_number = 10

    return_message = ""
    for i in range(0, top_number):
        return_message = "{}{}: {} - {}/10 - {}\n".format(return_message, i + 1,
                                                          restaurants[i][0], restaurants[i][1], restaurants[i][2])
    return return_message, restaurants


def set_restaurant(restaurant):
    """set restaurant: food set <restaurantname>"""
    global current_food_place
    restaurants = query.get_restaurants()
    if len(restaurants) == 0:
        restaurants = update_restaurant_database()  # generate restaurants
    r = requests.get("https://insult.mattbas.org/api/insult").text.split()
    adjective = r[3]
    noun = r[-1]
    for resto in restaurants:
        logger.debug('{} is {}? '.format(restaurant, resto[0].lower()))
        if restaurant == resto[0].lower():
            current_food_place = "{} with url: {}".format(resto[0], resto[2])
            return "restaurant set to {}. I heard they serve {} {}".format(resto[0], adjective, noun)
    return "Restaurant '{}' not in our database. " \
           "Add it NOW with the command 'food restaurant add < _restaurantname_ > < _url_ >', you {} {}!" \
        .format(restaurant, adjective, noun)


def add_restaurant(words_received, trigger):
    """Command: 'food restaurant add <restaurant-name> <url>' """
    resto_name = words_received[words_received.index(trigger) + 1:-1]
    resto_url = words_received[-1]
    if ("." in resto_url) and len(resto_name) != 0:
        query.add_restaurant(" ".join(resto_name).replace(",", ""), resto_url, 6)
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
        mean = int((old_rating[0][0] + rating) / 2)
        query.set_restaurant_rating(mean, restaurant_name)
        msg = "Restaurant {}: mean rating changed to {}".format(restaurant_name, mean)
    else:
        msg = "you soab, that's a restaurant I do not know."
    logger.debug("Restaurant {} rated with a score of {}".format(restaurant_name, rating))
    return msg
