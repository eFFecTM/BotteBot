from pathlib import Path

from datetime import datetime
from bs4 import BeautifulSoup
import requests
import random

current_food_place = "Pizza Hut"
current_orders = {}
current_schedule = {}
restaurants = []
polls_path = "data/polls/"
orders_path = "data/orders/"
schedule_path = "data/"
menu = [[], []]


def process_call(user, input_text, channel):
    input = input_text.strip().split(" ")
    if len(input) >= 2 and input[1].lower() == "overview":
        output = get_order_overview()
    elif len(input) >= 3 and input[1].lower() == "order":
        output = order_food(user, input[2])
    elif len(input) >= 3 and input[1].lower() == "schedule" and input[2].lower() == "list":
        output = get_schedule_overview()
    elif len(input) >= 4 and input[1].lower() == "schedule" and input[2].lower() == "add":
        day = datetime.strptime(input[3], "%d/%m/%y").date()
        times = []
        if len(input) > 4:
            for time in input[4:]:
                times.append(datetime.strptime(time, "%H:%M").time())
        output = add_schedule(day, times)
    elif len(input) >= 4 and input[1].lower() == "schedule" and input[2].lower() == "remove":
        day = datetime.strptime(input[3], "%d/%m/%y").date()
        times = []
        if len(input) > 4:
            for time in input[4:]:
                times.append(datetime.strptime(time, "%H:%M").time())
        output = remove_schedule(day, times)
    else:
        output = "I don't talk R0B0T"

    return output


# /////////
# COMMANDS
# /////////

def get_order_overview():
    output = ""
    output += "From where do you want some food? " + current_food_place
    output += "\n\n\n"
    for user, order in current_orders.items():
        output += user + " orders the following: " + order + "\n"

    return output


snappy_responses = ["just like the dignity of your {} mother. Mama Mia!",
                    "pick again you {} idiot!",
                    "better luck next time {} person!",
                    u"\U0001F595",
                    "huh? Fine! I'll go build my own restaurant, with blackjack and hookers. In fact, forget about the restaurant and blackjack."]


def get_menu(text_received):
    global restaurants, snappy_responses, menu
    found = []
    message = ""
    if len(restaurants) == 0:
        get_restaurants('top 1')  # generate restaurants
    for resto_name in restaurants[0]:
        if resto_name.lower() in text_received.lower():
            found = resto_name
            message = "Restaurant: *{}*\n\n".format(resto_name)
            break
    if found:
        response = requests.get(restaurants[1][restaurants[0].index(found)])

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

        rand = random.randint(0, top_number*3)
        location_number = 0
        if top_number > len(menu[0]):
            top_number = len(menu[0])
        for i in range(0, top_number):
            location_number += 1
            if rand == i:
                message = "{}{}: Uw mama voor €0\n".format(message, location_number)
                location_number += 1
            message = "{}{}: {} voor €{}\n".format(message, location_number, menu[0][i], menu[1][i])
    else:
        rand = random.randint(0, len(snappy_responses) - 1)
        r = requests.get("https://insult.mattbas.org/api/adjective")
        return "The restaurant is not found, {}".format(snappy_responses[rand].replace("{}", r.text))

    return message


def order_food(user, values):
    food = " ".join(values)
    current_orders[user] = food
    save_orders(user, food)
    return "Order placed: " + food


def get_restaurants(text_received):
    global restaurants
    response = requests.get('https://www.takeaway.com/be/eten-bestellen-antwerpen-2020')

    soup = BeautifulSoup(response.content, 'html.parser')
    find = soup.find_all('script')
    text = find[9].text
    location = text.find('name')
    restaurants = [[], []]

    while location != -1:
        text = text[location + len('"name":"') - 1:]
        location = text.find('"')
        temp = text[:location]
        temp = temp.replace("\'", '')
        restaurants[0].append(temp)
        location = text.find('url')
        text = text[location + len('"url":"') - 1:]
        location = text.find('"')
        temp = text[:location]
        temp = "https://www.takeaway.com" + temp
        temp = temp.replace("\\", '')
        restaurants[1].append(temp)
        location = text.find('name')

    return_message = ""

    if 'top' in text_received:
        words = text_received.split()
        next_word = words[words.index('top') + 1]
        try:
            top_number = int(next_word)
            if top_number > len(restaurants[0]):
                top_number = len(restaurants[0])
            elif top_number < 1:
                top_number = 1
        except:
            top_number = 10
    else:
        top_number = 10
    for i in range(0, top_number):
        return_message = "{}{}: {}   - {}\n".format(return_message, i+1, restaurants[0][i],
                                                    restaurants[1][i])
    return return_message


def get_schedule_overview():
    if len(current_schedule) == 0:
        return "Schedule is empty"
    output = ""
    output += "ImagineLab Schedule"
    output += "\n\n\n"
    for day, times in current_schedule.items():
        save_times = []
        if times is not None:
            for time in times:
                save_times.append(time.strftime("%H:%M"))
        output += "- " + day.strftime("%d/%m/%y") + ": " + " ".join(save_times) + "\n"
    return output


def add_schedule(day, times):
    try:
        if day < datetime.today().date():
            return "Date is in the past"
        if times is not None:
            current_times = current_schedule.get(day)
            if current_times is None:
                current_times = []
            for time in times:
                if time not in current_times:
                    current_times.append(time)
            current_schedule[day] = current_times
        else:
            current_schedule[day] = None
        save_schedule()
        return "Added to schedule"
    except ValueError:
        return "Format is incorrect, use DD/MM/YY for day and HH:MM for time"


def remove_schedule(day, times):
    if hasattr(current_schedule, day):
        if times is not None:
            current_times = current_schedule[day]
            if current_times is not None:
                for time in times:
                    current_times.pop(time)
        else:
            current_schedule.pop(day)
        save_schedule()
        return "Removed from schedule"
    return "Date does not exist in schedule"


# ////////////////
# FILE MANAGEMENT
# ////////////////


def read_current_day_data():
    if len(current_orders) == 0:
        today = datetime.now().strftime("%Y%m%d")
        path = Path(orders_path + today + "_orders.txt")
        if path.is_file():
            order_file = open(path, "r")
            lines = order_file.readlines()
            for line in lines:
                elements = line.strip().split(";")
                current_orders[elements[0]] = elements[1]

    # expand when polls are used

    if len(current_schedule) == 0:
        path = Path(schedule_path + "schedule.txt")
        if path.is_file():
            schedule_file = open(path, "r")
            lines = schedule_file.readlines()
            for line in lines:
                elements = line.strip().split(";")
                day = datetime.strptime(elements[0], "%d/%m/%y").date()
                times = []
                if elements[1:] is not None:
                    for time in elements[1:]:
                        times.append(datetime.strptime(time, "%H:%M").time())
                current_schedule[day] = times


def save_orders(user, food):
    today = datetime.now().strftime("%Y%m%d")
    file_orders = open(orders_path + today + "_orders.txt", "a+")
    file_orders.write(user + ";" + food + "\n")
    file_orders.close()


def save_polls():
    today = datetime.now().strftime("%Y%m%d")
    file_polls = open(polls_path + today + "_polls.txt", "a+")
    file_polls.write("template")
    file_polls.close()


def save_schedule():
    file_schedule = open(schedule_path + "schedule.txt", "w")
    for day, times in current_schedule.items():
        save_times = []
        if times is not None:
            for time in times:
                save_times.append(time.strftime("%H:%M"))
        file_schedule.write(day.strftime("%d/%m/%y") + ";" + ";".join(save_times) + "\n")
    file_schedule.close()

