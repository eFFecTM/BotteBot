import random
import logging
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from data.sqlquery import SQL_query


# Create global logger
logger = logging.getLogger('FoodBot')
formatstring = "%(asctime)s - %(name)s:%(funcName)s:%(lineno)i - %(levelname)s - %(message)s"
logging.basicConfig(format=formatstring, level=logging.DEBUG)
logger.debug('FoodBot started.')

s = SQL_query('data/imaginelab.db')
current_food_place = "Pizza Hut"
current_user_orders = []
pretty_orders = {}
current_schedule = []
restaurants = []
menu = [[], []]
today = datetime.now().strftime("%Y%m%d")

snappy_responses = ["just like the dignity of your {} mother. Mama Mia!",
                    "pick again you {} idiot!",
                    "better luck next time {} person!",
                    u"\U0001F595",
                    "huh? Fine! I'll go build my own restaurant, with blackjack and hookers. In fact, forget about the restaurant and blackjack."]


def process_call(user, input_text, set_triggers, overview_triggers, order_triggers, schedule_triggers,
                 add_triggers, remove_triggers, restaurant_triggers, rating_triggers, food_trigger):
    output = None
    input_text = input_text.lower()
    if not output:
        for set_trigger in set_triggers:
            if set_trigger in input_text:
                words = input_text.split()
                output = set_restaurant(" ".join(words[words.index(set_trigger) + 1:]))
                break
    if not output and any(overview_trigger in input_text for overview_trigger in overview_triggers):
        output = get_order_overview(output)
    if not output and any(order_trigger in input_text for order_trigger in order_triggers):
        if not output:
            for remove_trigger in remove_triggers:
                if remove_trigger in input_text:
                    words = input_text.split()
                    output = remove_order_food(user, " ".join(words[words.index(remove_trigger) + 1:]))
                    break
        if not output:
            for order_trigger in order_triggers:
                if order_trigger in input_text:
                    words = input_text.split()
                    output = order_food(user, " ".join(words[words.index(order_trigger) + 1:]))
                    break
    if not output and any(rating_trigger in input_text for rating_trigger in rating_triggers):
        if not output:
            for rating_trigger in rating_triggers:
                if rating_trigger in input_text:
                    output = add_restaurant_rating(input_text, rating_trigger, food_trigger)
                    break
    if not output and any(restaurant_trigger in input_text for restaurant_trigger in restaurant_triggers):
        if not output:
            for add_trigger in add_triggers:
                if add_trigger in input_text:
                    output = add_restaurant(input_text, add_trigger)
                    break
    if not output and any(schedule_trigger in input_text for schedule_trigger in schedule_triggers):
        if not output:
            for add_trigger in add_triggers:
                if add_trigger in input_text:
                    words = input_text.split()
                    next_word = words[words.index(add_trigger) + 1]
                    day = None
                    for fmt in (
                            "%d/%m/%Y", "%d.%m.%Y", "%d:%m:%Y", "%d-%m-%Y", "%d/%m/%y", "%d.%m.%y", "%d:%m:%y",
                            "%d-%m-%y", "%d/%m", "%d.%m", "%d:%m", "%d-%m"):
                        try:
                            day = datetime.strptime(next_word, fmt).date()
                            if day.year == 1900:
                                day = day.replace(year=datetime.now().year)
                            break
                        except ValueError:
                            pass
                    if day:
                        output = add_schedule(day)
                    else:
                        adjective = requests.get("https://insult.mattbas.org/api/adjective").text
                        output = "You're going to add no date? No one's going to date you're {} ass anyway.".format(adjective)
        if not output:
            for remove_trigger in remove_triggers:
                if remove_trigger in input_text:
                    words = input_text.split()
                    next_word = words[words.index(remove_trigger) + 1]
                    day = None
                    for fmt in (
                            "%d/%m/%Y", "%d.%m.%Y", "%d:%m:%Y", "%d-%m-%Y", "%d/%m/%y", "%d.%m.%y", "%d:%m:%y",
                            "%d-%m-%y", "%d/%m", "%d.%m", "%d:%m", "%d-%m"):
                        try:
                            day = datetime.strptime(next_word, fmt).date()
                            if day.year == 1900:
                                day = day.replace(year=datetime.now().year)
                            break
                        except ValueError:
                            pass
                    if day:
                        output = remove_schedule(day)
                    else:
                        r = requests.get("https://insult.mattbas.org/api/insult").text.split()
                        adjective = r[3]
                        noun = r[-1]
                        output = "There should be a date behind {}, you {} {}.".format(remove_trigger, adjective, noun)
        if not output:
            output = get_schedule_overview()

    return output


# /////////
# COMMANDS
# /////////




def get_order_overview(output):
    if not output:
        output = ""
    output += "We're getting food from " + current_food_place
    output += "\n\n\n"
    for [user, order] in current_user_orders:
        output += user + " orders the following: " + order + "\n"
    if len(current_user_orders) != 0:
        output += "\nThis results in:\n"
    for order, amount in pretty_orders.items():
        output += "{} times {}\n".format(amount, order)
    return output


def order_food(user, food):
    if food in pretty_orders.keys():
        pretty_orders[food] += 1
    else:
        pretty_orders[food] = 1
    current_user_orders.append([user, food])
    adjective = requests.get("https://insult.mattbas.org/api/adjective").text
    return "Order placed: {} for {} {}".format(food, adjective, user)


def remove_order_food(user, food):
    if [user, food] in current_user_orders:
        pretty_orders[food] -= 1
        if pretty_orders[food] == 0:
            pretty_orders.pop(food)
        current_user_orders.remove([user, food])
    else:
        noun = requests.get("https://insult.mattbas.org/api/insult").text.split()[-1]
        return "There's no food from {} matching {}, buy some glasses, you blind {}".format(user, food, noun)
    return "Fine. No food for {}".format(user)


def get_schedule_overview():
    if len(current_schedule) == 0:
        return "Schedule is empty, like your life."
    output = ""
    output += "ImagineLab Schedule"
    output += "\n\n\n"
    for day in current_schedule:
        output += "- " + day.strftime("%d/%m/%Y") + "\n"
    return output


def add_schedule(day):
    if day < datetime.today().date():
        return "Let's not meet in the past. Actually, let's just not meet at all please!"
    current_schedule.append(day)
    adjective = requests.get("https://insult.mattbas.org/api/adjective").text
    return "Added {} to schedule, hope not to see you're {} ass there!".format(day.strftime("%d/%m/%Y"), adjective)


def remove_schedule(day):
    if day in current_schedule:
        current_schedule.remove(day)
        r = requests.get("https://insult.mattbas.org/api/insult").text.split()
        adjective = r[3]
        noun = r[-1]
        return "Removed {} from schedule, the less I need to meet you {} {}, the better!".format(day.strftime("%d/%m/%Y"), adjective, noun)
    adjective = requests.get("https://insult.mattbas.org/api/adjective").text
    return "Just like your {} friends, {} does not exist.".format(adjective, day.strftime("%d/%m/%Y"))


def get_menu(text_received):
    global restaurants, snappy_responses, menu
    found = []
    message = ""
    if len(restaurants) == 0:
        update_restaurant_database('top 1')  # generate restaurants
    for resto in restaurants:
        if resto[0].lower() in text_received.lower():
            found = resto
            message = "Restaurant: *{}*\n\n".format(resto[0])
            break
    if found:
        response = requests.get(found[2])

        soup = BeautifulSoup(response.content, 'html.parser')
        location = soup.text.find('MenucardProducts')
        text = soup.text[location:]

        if 'top' in text_received:
            words = text_received.split()
            next_word = words[words.index('top') + 1]
            try:
                top_number = int(next_word)
                if top_number > 50:
                    top_number = 50
                elif top_number < 1:
                    top_number = 1
            except:
                top_number = 10
        else:
            top_number = 10

        location = text.find('name')
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
    global restaurants

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
        restaurants.append([temp_name, temp_url])
        location = text.find('name')


def update_restaurant_database(text_received=None):
    global restaurants
    get_restaurants_from_takeaway()
    for resto in restaurants:
        s.sql_edit_insert('INSERT OR IGNORE INTO restaurant_database (restaurant, url) VALUES (?,?)', (resto[0], resto[2]))
        # s.sql_edit_insert('UPDATE restaurant_database SET url=?  WHERE restaurant=? ', (restaurants[1][restaurants[0].index(restaurant)], restaurant))
    logger.debug('Updated restaurant database')

    # Get top number
    if text_received and 'top' in text_received:
        words = text_received.split()
        next_word = words[words.index('top') + 1]
        try:
            top_number = int(next_word)
            if top_number > len(restaurants):
                top_number = len(restaurants)
            elif top_number < 1:
                top_number = 1
        except:
            top_number = 10
    else:
        top_number = 10

    return_message = ""
    for i in range(0, top_number):
        return_message = "{}{}: {}   - {}\n".format(return_message, i + 1, restaurants[i][0], restaurants[i][1])
    return return_message


def get_restaurants(text_received):
    global restaurants
    restaurants = s.sql_db_to_list('SELECT * FROM restaurant_database ORDER BY rating DESC, id')
    a = s.sql_db_to_list('SELECT * FROM restaurant_database ORDER BY rating DESC, id')

    if text_received and 'top' in text_received:
        words = text_received.split()
        next_word = words[words.index('top') + 1]
        try:
            top_number = int(next_word)
            if top_number > len(restaurants):
                top_number = len(restaurants)
            elif top_number < 1:
                top_number = 1
        except:
            top_number = 10
    else:
        top_number = 10

    return_message = ""
    for i in range(0, top_number):
        return_message = "{}{}: {}   - {}\n".format(return_message, i + 1, restaurants[i][0], restaurants[i][2])
    return return_message


def set_restaurant(restaurant):
    """set restaurant: food set <restaurantname>"""
    global restaurants, current_food_place
    if len(restaurants) == 0:
        update_restaurant_database('top 1')  # generate restaurants
    r = requests.get("https://insult.mattbas.org/api/insult").text.split()
    adjective = r[3]
    noun = r[-1]
    for resto in restaurants:
        if restaurant in resto[0].lower():
            current_food_place = "{} \nwith url {}".format(resto[0], resto[2])
            return "restaurant set to {}. I heard they serve {} {}".format(resto[0], adjective, noun)
    return "Restaurant not in our database. Add it NOW with the command 'food restaurant add _restaurantname_ _url_' ,you {} {}!".format(restaurant, adjective, noun)


def add_restaurant(input_text, trigger):
    """add restaurant: Food Restaurant Add <restaurant-name> <url>"""
    words = input_text.split()
    resto_name = words[words.index(trigger)+1:-1]
    resto_url = words[-1]
    if ("." in resto_url) and len(resto_name) != 0:
        s.sql_edit_insert('INSERT OR IGNORE INTO restaurant_database (restaurant, url) VALUES (?,?)',
                          (" ".join(resto_name).replace(",", ""), resto_url))
        return "{} added to restaurants.".format(" ".join(resto_name).replace(",", ""))
    else:
        return "The right format is <restaurant name> <url> but I didn't expect you could use it anyway. {} ~ {}".format(resto_name, resto_url)


def add_restaurant_rating(text_received, rating_trigger, food_trigger):
    """ Command: food rating <restaurant> <rating>"""
    words = text_received.split()
    words.remove(rating_trigger)
    words.remove(food_trigger)

    rating = int(re.search(r'\d+', text_received).group())
    words.remove(str(rating))
    restaurant_name = "".join(words).replace(",", "")
    logger.debug("Restaurant {} rated with a score of {}".format(restaurant_name, rating))


