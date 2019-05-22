from pathlib import Path

from _datetime import datetime
from bs4 import BeautifulSoup
import requests

current_food_place = "Pizza Hut"
current_orders = []
restaurants = []
polls_path = "data/polls/"
orders_path = "data/orders/"
schedule_path = "data"


def process_call(user, input_text, channel):
    input = input_text.split(" ")
    if len(input) >= 2 and input[1].lower() == "overview":
        output = get_overview()
    elif len(input) >= 3 and input[1].lower() == "order":
        input.pop(0)
        input.pop(0)
        output = order_food(user, input)
    elif len(input) >= 3 and input[1].lower() == "schedule" and input[2].lower() == "list":
        input.pop(0)

    else:
        output = "??????????????"

    return output


# /////////
# COMMANDS
# /////////

def get_overview():
    output_text = ""
    output_text += "From where do you want some food? " + current_food_place
    output_text += "\n\n\n"
    for (user, order) in current_orders:
        output_text += user + " orders the following: " + order + "\n"

    return output_text


def get_menu(text_received):
    global restaurants
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

        for i in range(0, top_number):
            location = text.find('name')
            text = text[location + len('"name": "') - 1:]
            location = text.find('"')
            temp = text[:location]
            location = text.find('price')
            text = text[location + len('"price": ') - 1:]
            location = text.find(",")
            message = "{}{}: {} voor €{}\n".format(message, i+1, temp, text[:location])
    else:
        return None

    return message


def order_food(user, values):
    food = " ".join(values)
    current_orders.append((user, food))
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
            top_number = len(restaurants[0])
    else:
        top_number = len(restaurants[0])
    for i in range(0, top_number):
        return_message = "{}{}: {}   - {}\n".format(return_message, i+1, restaurants[0][i],
                                                    restaurants[1][i])
    return return_message


# ////////////////
# FILE MANAGEMENT
# ////////////////


def read_current_day_data():
    if len(current_orders) == 0:
        today = datetime.now().strftime("%Y%m%d")
        order_path = Path(orders_path + today + "_orders.txt")
        if order_path.is_file():
            order_file = open(order_path, "r")
            lines = order_file.readlines()
            for line in lines:
                elements = line.strip().split(";")
                current_orders.append((elements[0], elements[1]))
                print(elements)
    # expand when polls are used


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

